### IAM

data "aws_iam_policy_document" "assume_role_lambda" {
  statement {
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
    sid     = "LambdaAssumeRole"
    effect  = "Allow"
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = "${var.project_name}-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_lambda.json
}

data "aws_iam_policy_document" "lambda_pull_ecr_policy" {
  statement {
    actions = [
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer"
    ]
    effect = "Allow"
    resources = [
      module.ecr.repository_arn
    ]
  }
}

resource "aws_iam_policy" "allow_ecr" {
  policy = data.aws_iam_policy_document.lambda_pull_ecr_policy.json
  name   = "${var.project_name}-lambda-read-ecr-policy"
}

resource "aws_iam_role_policy_attachment" "attachment_00" {
  role       = aws_iam_role.lambda_role.id
  policy_arn = aws_iam_policy.allow_ecr.arn
}

resource "aws_iam_role_policy_attachment" "attachment_01" {
  role       = aws_iam_role.lambda_role.id
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

### ECR

module "ecr" {
  source                  = "terraform-aws-modules/ecr/aws"
  repository_type         = "private"
  repository_name         = "${var.project_name}-repo"
  repository_force_delete = true
  repository_read_write_access_arns = [
    data.aws_caller_identity.current.arn
  ]
  repository_lambda_read_access_arns = [
    aws_iam_role.lambda_role.arn
  ]
  repository_lifecycle_policy = jsonencode({
    rules = [
      {
        "rulePriority" : 1,
        "description" : "Keep only the most recent image",
        "selection" : {
          "tagStatus" : "any",
          "countType" : "imageCountMoreThan",
          "countNumber" : 1
        },
        "action" : {
          "type" : "expire"
        }
      }
    ]
  })
}

// Push the latest tourist image from GHCR to ECR
resource "null_resource" "push_image_to_ecr" {
  provisioner "local-exec" {
    command = "/tf/push-ecr.sh"
    when    = create
    environment = {
      ACCOUNT_ID      = data.aws_caller_identity.current.account_id
      REGION          = var.region
      REPO_URL        = module.ecr.repository_url
      TOURIST_VERSION = var.image_tag
    }
  }
  depends_on = [ module.ecr ]
}

### LAMBDA

module "lambda_function" {

  count = var.num_functions

  source = "terraform-aws-modules/lambda/aws"

  lambda_role                       = aws_iam_role.lambda_role.arn
  create_role                       = false
  function_name                     = "${var.project_name}-${format("function-%02d", count.index)}"
  description                       = "Handles requests for the Tourist SERP API."
  create_package                    = false
  package_type                      = "Image"
  image_uri                         = "${module.ecr.repository_url}:${var.image_tag}"
  timeout                           = var.timeout
  memory_size                       = var.memory_size
  cloudwatch_logs_retention_in_days = var.cloudwatch_logs_retention_in_days

  # TODO: Move this to secrets manager and pull at runtime
  environment_variables = {
    X_API_KEY = var.x_api_key
  }

  # Public function URL
  create_lambda_function_url = true
  authorization_type         = "NONE"

  tags = {
    Name = "${var.project_name}-function"
  }

  depends_on = [ null_resource.push_image_to_ecr ]
}
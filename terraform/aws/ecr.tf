module "ecr" {
  source = "terraform-aws-modules/ecr/aws"
  repository_type = "private"
  repository_name = "tourist"
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
    command = "/bin/bash ./scripts/ecr-push-image.sh"
    when = create
    environment = {
      ACCOUNT_ID = data.aws_caller_identity.current.account_id
      REGION = "us-east-1"
      REPO_URL = module.ecr.repository_url
      TOURIST_VERSION = var.image_tag
    }
  }
  depends_on = [ module.ecr ]
}

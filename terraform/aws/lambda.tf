module "app_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 6.0"

  function_name                     = var.app_function_name
  description                       = "Tourist application backend."
  lambda_role                       = aws_iam_role.lambda_role.arn
  create_package                    = false
  create_role                       = false
  image_uri                         = module.docker_image_in_ecr.image_uri
  package_type                      = "Image"
  architectures                     = ["x86_64"]
  timeout                           = 30
  create_sam_metadata               = true
  cloudwatch_logs_retention_in_days = 5
  memory_size                       = 3008
}

module "auth_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 6.0"

  function_name                     = var.auth_function_name
  description                       = "Tourist application auth middleware."
  lambda_role                       = aws_iam_role.lambda_role.arn
  create_role                       = false
  timeout                           = 300
  source_path                       = "."
  handler                           = "auth.lambda_handler"
  runtime                           = "python3.12"
  create_package                    = false
  local_existing_package            = "auth.zip"
  ignore_source_code_hash           = false
  cloudwatch_logs_retention_in_days = 5
  environment_variables             = { "X_SECRET_VALUE" = "supersecret" }
}
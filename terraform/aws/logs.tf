resource "aws_cloudwatch_log_group" "api_gw" {
  name = "/aws/apigw/${aws_apigatewayv2_api.api.name}"

  retention_in_days = 30
}

# resource "aws_cloudwatch_log_group" "app_lambda" {
#   name = "/aws/lambda/${module.auth_lambda.lambda_function_name}"

#   retention_in_days = 30
# }

# resource "aws_cloudwatch_log_group" "auth_lambda" {
#   name = "/aws/lambda/${module.auth_lambda.lambda_function_name}"

#   retention_in_days = 30
# }

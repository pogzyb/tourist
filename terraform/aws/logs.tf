resource "aws_cloudwatch_log_group" "api_gw" {
  name = "/aws/apigw/${aws_apigatewayv2_api.api.name}"

  retention_in_days = 30
}

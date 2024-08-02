output "api_endpoint" {
  description = "Tourist API Base URL"
  value       = "${aws_apigatewayv2_api.api.api_endpoint}/${aws_apigatewayv2_stage.stage.name}"
}

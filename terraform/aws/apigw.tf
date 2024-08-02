resource "aws_apigatewayv2_api" "api" {
  name          = var.api_name
  description   = "Tourist HTTP API."
  protocol_type = "HTTP"

  cors_configuration {
    # allow_credentials = false
    allow_headers  = ["*", "x-secret", "content-type", "accept", "authorization"]
    allow_methods  = ["GET", "POST", "OPTIONS", "PUT", "HEAD", "DELETE"]
    allow_origins  = ["*"]
    expose_headers = ["*"]
    max_age        = 300
  }
}

# TODO/contribution: Optional domain name and ACM certificate
# resource "aws_apigatewayv2_domain_name" "domain" {
#   domain_name = var.domain_name

#   domain_name_configuration {
#     certificate_arn = aws_acm_certificate.cert.arn
#     endpoint_type   = "REGIONAL"
#     security_policy = "TLS_1_2"
#   }
# }

# resource "aws_apigatewayv2_api_mapping" "mapping" {
#   api_id      = aws_apigatewayv2_api.api.id
#   domain_name = aws_apigatewayv2_domain_name.domain.id
#   stage       = aws_apigatewayv2_stage.stage.id
# }

resource "aws_apigatewayv2_stage" "stage" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = var.env
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gw.arn

    format = jsonencode({
      requestId               = "$context.requestId"
      sourceIp                = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      protocol                = "$context.protocol"
      httpMethod              = "$context.httpMethod"
      resourcePath            = "$context.resourcePath"
      routeKey                = "$context.routeKey"
      status                  = "$context.status"
      responseLength          = "$context.responseLength"
      integrationErrorMessage = "$context.integrationErrorMessage"
      }
    )
  }
}

# authorizer
resource "aws_apigatewayv2_authorizer" "authorizer" {
  name                              = "authorizer"
  api_id                            = aws_apigatewayv2_api.api.id
  authorizer_uri                    = module.auth_lambda.lambda_function_invoke_arn
  authorizer_type                   = "REQUEST"
  enable_simple_responses           = true
  authorizer_result_ttl_in_seconds  = 300
  authorizer_payload_format_version = "2.0"
  identity_sources                  = ["$request.header.X-Secret"]
  authorizer_credentials_arn        = aws_iam_role.apigw_role.arn
}

# integrations
resource "aws_apigatewayv2_route" "route_get" {
  api_id             = aws_apigatewayv2_api.api.id
  route_key          = "GET /{proxy+}"
  target             = "integrations/${aws_apigatewayv2_integration.app_integration.id}"
  authorizer_id      = aws_apigatewayv2_authorizer.authorizer.id
  authorization_type = "CUSTOM"
  operation_name     = "invoke_tourist"
}

resource "aws_apigatewayv2_route" "route_post" {
  api_id             = aws_apigatewayv2_api.api.id
  route_key          = "POST /{proxy+}"
  target             = "integrations/${aws_apigatewayv2_integration.app_integration.id}"
  authorizer_id      = aws_apigatewayv2_authorizer.authorizer.id
  authorization_type = "CUSTOM"
  operation_name     = "invoke_tourist"
}

resource "aws_apigatewayv2_integration" "app_integration" {
  api_id                 = aws_apigatewayv2_api.api.id
  integration_type       = "AWS_PROXY"
  connection_type        = "INTERNET"
  description            = "Integration for the tourist application."
  integration_method     = "POST"
  integration_uri        = module.app_lambda.lambda_function_invoke_arn
  credentials_arn        = aws_iam_role.apigw_role.arn
  payload_format_version = "2.0"
}

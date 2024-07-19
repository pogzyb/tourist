## APIGW
data "aws_iam_policy_document" "apigw_assume_role" {
  statement {
    principals {
      type        = "Service"
      identifiers = ["apigateway.amazonaws.com"]
    }
    actions = [
      "sts:AssumeRole"
    ]
    sid    = "APIGWAssumeRole"
    effect = "Allow"
  }
}

resource "aws_iam_role" "apigw_role" {
  name               = "tourist-apigw-exec-role"
  assume_role_policy = data.aws_iam_policy_document.apigw_assume_role.json
}

data "aws_iam_policy_document" "apigw_policy_document" {
  statement {
    effect    = "Allow"
    actions   = ["lambda:InvokeFunction"]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "apigw_policy" {
  policy = data.aws_iam_policy_document.apigw_policy_document.json
  name   = "tourist-apigw-service-policy"
}

resource "aws_iam_role_policy_attachment" "attach_to_apigw_service_role" {
  role       = aws_iam_role.apigw_role.id
  policy_arn = aws_iam_policy.apigw_policy.arn
}

## Lambda
data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = [
      "sts:AssumeRole"
    ]
    sid    = "LambdaAssumeRole"
    effect = "Allow"
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = "tourist-lambda-exec-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "attach_to_lambda_service_role" {
  role       = aws_iam_role.lambda_role.id
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
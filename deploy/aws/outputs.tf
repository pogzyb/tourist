output "function_urls" {
  value = module.lambda_function[*].lambda_function_url
}
output "frontend_s3_website_url" {
  description = "Public landing page for the AWS Messaging Learning Lab."
  value       = "http://${aws_s3_bucket_website_configuration.frontend.website_endpoint}"
}

output "sqs_learning_url" {
  description = "Amazon SQS reference guide and live labs."
  value       = "http://${aws_s3_bucket_website_configuration.frontend.website_endpoint}/sqs/"
}

output "sns_learning_url" {
  description = "Amazon SNS module route."
  value       = "http://${aws_s3_bucket_website_configuration.frontend.website_endpoint}/sns/"
}

output "learning_urls" {
  description = "Service pages and the Northline and Clearfile capstones."
  value = {
    for path in ["iam", "vpc", "s3", "lambda", "eventbridge", "projects/northline", "projects/clearfile"] :
    path => "http://${aws_s3_bucket_website_configuration.frontend.website_endpoint}/${path}/"
  }
}

output "api_gateway_custom_domain_url" {
  description = "HTTPS custom domain for POST /buy-direct and POST /buy-queue. Point the dashboard BASE_URL at this value."
  value       = "https://${aws_apigatewayv2_domain_name.api.domain_name}"
}

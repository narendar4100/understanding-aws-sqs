# Temporarily disabled because the S3 and API Gateway resources above are commented out.
# After those resources are uncommented, remove the leading "# " from each line below.

# output "frontend_s3_website_url" {
#   description = "Public HTTP endpoint for the Core Banking Ledger training dashboard."
#   value       = "http://${aws_s3_bucket_website_configuration.frontend.website_endpoint}"
# }
#
# output "api_gateway_custom_domain_url" {
#   description = "HTTPS custom domain for POST /buy-direct and POST /buy-queue. Point the dashboard BASE_URL at this value."
#   value       = "https://${aws_apigatewayv2_domain_name.api.domain_name}"
# }

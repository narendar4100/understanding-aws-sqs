variable "aws_region" {
  type        = string
  description = "AWS region for Lambda, SQS, API Gateway, ACM, S3, and the regional API custom domain."
}

variable "domain_name" {
  type        = string
  description = "Apex domain name of the existing public Route 53 hosted zone. Do not include a trailing dot."
}

variable "subdomain_prefix" {
  type        = string
  description = "Left-most DNS label combined with domain_name to form the API Gateway custom domain and the frontend bucket name."
}

variable "environment" {
  type        = string
  description = "Deployment name prefix for the SQS buffer queue, Lambda functions, and API Gateway."
}

variable "order_ops_email" {
  type        = string
  default     = ""
  description = "Inbox for the operations SNS email subscription. Leave empty to skip that subscription. SNS stays pending until this inbox confirms the subscription email."
}

variable "order_ses_from_email" {
  type        = string
  default     = ""
  description = "Verified SES sender for customer order confirmations. Leave empty to log the confirmation without sending. In the SES sandbox the customer address must be verified too."
}

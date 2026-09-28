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

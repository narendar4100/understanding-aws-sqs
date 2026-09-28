terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.70"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }

  # Values come from backend.hcl via: terraform init -backend-config=backend.hcl
  backend "s3" {}
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = local.project
      ManagedBy   = "terraform"
    }
  }
}

locals {
  project         = "core-banking-ledger"
  api_fqdn        = "${var.subdomain_prefix}.${var.domain_name}"
  frontend_bucket = "${var.subdomain_prefix}.${var.domain_name}"
}

# Remote state — S3 + DynamoDB lock
# Bucket ARN : arn:aws:s3:::statefiles-4100123
# Lock table : arn:aws:dynamodb:us-east-1:471112865321:table/state_lock
# Init with  : terraform init -backend-config=backend.hcl

bucket         = "statefiles-4100123"
key            = "training/core-banking-ledger/terraform.tfstate"
region         = "us-east-1"
encrypt        = true
dynamodb_table = "state_lock"

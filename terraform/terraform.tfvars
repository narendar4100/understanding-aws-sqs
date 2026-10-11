aws_region       = "us-east-1"
domain_name      = "sisuraphotography.com"
subdomain_prefix = "demo"
environment      = "training"

# Fill these before apply when the class should send real mail.
# order_ops_email stays pending until that inbox clicks the SNS confirmation.
# order_ses_from_email must be verified. In the SES sandbox, the shopper address must be verified too.
order_ops_email      = ""
order_ses_from_email = ""

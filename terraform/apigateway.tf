# Temporarily disabled so Terraform will not recreate resources that already exist.
# Line comments are used because a block comment ends early at the */ inside
# source_arn "...execution_arn}/*/POST/buy-direct".
# After you delete these in AWS, remove the leading "# " from each line below:
#   IAM role training-ledger-apigw-sqs
#   API Gateway training-ledger-http-api
#   Custom domain demo.sisuraphotography.com

# resource "aws_apigatewayv2_api" "ledger" {
#   name          = "${var.environment}-ledger-http-api"
#   protocol_type = "HTTP"
#   description   = "Training HTTP API. /buy-direct calls Lambda. /buy-queue writes straight to SQS."
#
#   cors_configuration {
#     allow_origins = ["*"]
#     allow_methods = ["OPTIONS", "POST"]
#     allow_headers = ["*"]
#     max_age       = 300
#   }
# }
#
# resource "aws_apigatewayv2_integration" "direct" {
#   api_id                 = aws_apigatewayv2_api.ledger.id
#   integration_type       = "AWS_PROXY"
#   integration_uri        = aws_lambda_function.direct_lambda.invoke_arn
#   payload_format_version = "2.0"
#   timeout_milliseconds   = 20000
# }
#
# resource "aws_apigatewayv2_route" "buy_direct" {
#   api_id    = aws_apigatewayv2_api.ledger.id
#   route_key = "POST /buy-direct"
#   target    = "integrations/${aws_apigatewayv2_integration.direct.id}"
# }
#
# resource "aws_lambda_permission" "direct" {
#   statement_id  = "AllowAPIGatewayBuyDirect"
#   action        = "lambda:InvokeFunction"
#   function_name = aws_lambda_function.direct_lambda.function_name
#   principal     = "apigateway.amazonaws.com"
#   source_arn    = "${aws_apigatewayv2_api.ledger.execution_arn}/*/POST/buy-direct"
# }
#
# data "aws_iam_policy_document" "apigw_assume" {
#   statement {
#     actions = ["sts:AssumeRole"]
#
#     principals {
#       type        = "Service"
#       identifiers = ["apigateway.amazonaws.com"]
#     }
#   }
# }
#
# data "aws_iam_policy_document" "apigw_sqs_send" {
#   statement {
#     actions   = ["sqs:SendMessage"]
#     resources = [aws_sqs_queue.buffer.arn]
#   }
# }
#
# resource "aws_iam_role" "apigw_sqs" {
#   name               = "${var.environment}-ledger-apigw-sqs"
#   assume_role_policy = data.aws_iam_policy_document.apigw_assume.json
# }
#
# resource "aws_iam_role_policy" "apigw_sqs_send" {
#   name   = "${var.environment}-ledger-apigw-sqs-send"
#   role   = aws_iam_role.apigw_sqs.id
#   policy = data.aws_iam_policy_document.apigw_sqs_send.json
# }
#
# resource "aws_apigatewayv2_integration" "queue" {
#   api_id              = aws_apigatewayv2_api.ledger.id
#   integration_type    = "AWS_PROXY"
#   integration_subtype = "SQS-SendMessage"
#   credentials_arn     = aws_iam_role.apigw_sqs.arn
#
#   request_parameters = {
#     QueueUrl    = aws_sqs_queue.buffer.url
#     MessageBody = "$request.body"
#   }
#
#   depends_on = [aws_iam_role_policy.apigw_sqs_send]
# }
#
# resource "aws_apigatewayv2_route" "buy_queue" {
#   api_id    = aws_apigatewayv2_api.ledger.id
#   route_key = "POST /buy-queue"
#   target    = "integrations/${aws_apigatewayv2_integration.queue.id}"
# }
#
# resource "aws_apigatewayv2_stage" "default" {
#   api_id      = aws_apigatewayv2_api.ledger.id
#   name        = "$default"
#   auto_deploy = true
#   description = "Auto-deployed default stage for the ledger training API."
# }
#
# resource "aws_apigatewayv2_domain_name" "api" {
#   domain_name = local.api_fqdn
#
#   domain_name_configuration {
#     certificate_arn = aws_acm_certificate_validation.api.certificate_arn
#     endpoint_type   = "REGIONAL"
#     security_policy = "TLS_1_2"
#   }
# }
#
# resource "aws_apigatewayv2_api_mapping" "api" {
#   api_id      = aws_apigatewayv2_api.ledger.id
#   domain_name = aws_apigatewayv2_domain_name.api.id
#   stage       = aws_apigatewayv2_stage.default.id
# }
#
# resource "aws_route53_record" "api" {
#   zone_id = data.aws_route53_zone.primary.zone_id
#   name    = local.api_fqdn
#   type    = "A"
#
#   alias {
#     name                   = aws_apigatewayv2_domain_name.api.domain_name_configuration[0].target_domain_name
#     zone_id                = aws_apigatewayv2_domain_name.api.domain_name_configuration[0].hosted_zone_id
#     evaluate_target_health = false
#   }
# }

# Checkout fan-out for the SNS class. The ledger queues and Lambdas stay
# untouched. One order Lambda publishes to one topic. Each subscription filter
# chooses its own messages.

resource "aws_sns_topic" "orders" {
  name = "${var.environment}-order-events"
}

resource "aws_sqs_queue" "order_billing_dlq" {
  name                      = "${var.environment}-order-billing-dlq"
  message_retention_seconds = 86400
}

resource "aws_sqs_queue" "order_shipping_dlq" {
  name                      = "${var.environment}-order-shipping-dlq"
  message_retention_seconds = 86400
}

resource "aws_sqs_queue" "order_subscription_dlq" {
  name                      = "${var.environment}-order-subscription-dlq"
  message_retention_seconds = 86400
}

resource "aws_sqs_queue" "order_billing" {
  name                       = "${var.environment}-order-billing"
  message_retention_seconds  = 86400
  visibility_timeout_seconds = 60

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.order_billing_dlq.arn
    maxReceiveCount     = 3
  })
}

resource "aws_sqs_queue" "order_shipping" {
  name                       = "${var.environment}-order-shipping"
  message_retention_seconds  = 86400
  visibility_timeout_seconds = 60

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.order_shipping_dlq.arn
    maxReceiveCount     = 3
  })
}

data "aws_iam_policy_document" "order_billing_queue" {
  statement {
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.order_billing.arn]

    principals {
      type        = "Service"
      identifiers = ["sns.amazonaws.com"]
    }

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [aws_sns_topic.orders.arn]
    }
  }
}

data "aws_iam_policy_document" "order_shipping_queue" {
  statement {
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.order_shipping.arn]

    principals {
      type        = "Service"
      identifiers = ["sns.amazonaws.com"]
    }

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [aws_sns_topic.orders.arn]
    }
  }
}

data "aws_iam_policy_document" "order_subscription_dlq" {
  statement {
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.order_subscription_dlq.arn]

    principals {
      type        = "Service"
      identifiers = ["sns.amazonaws.com"]
    }

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [aws_sns_topic.orders.arn]
    }
  }
}

resource "aws_sqs_queue_policy" "order_billing" {
  queue_url = aws_sqs_queue.order_billing.id
  policy    = data.aws_iam_policy_document.order_billing_queue.json
}

resource "aws_sqs_queue_policy" "order_shipping" {
  queue_url = aws_sqs_queue.order_shipping.id
  policy    = data.aws_iam_policy_document.order_shipping_queue.json
}

resource "aws_sqs_queue_policy" "order_subscription_dlq" {
  queue_url = aws_sqs_queue.order_subscription_dlq.id
  policy    = data.aws_iam_policy_document.order_subscription_dlq.json
}

resource "aws_sns_topic_subscription" "order_billing" {
  topic_arn            = aws_sns_topic.orders.arn
  protocol             = "sqs"
  endpoint             = aws_sqs_queue.order_billing.arn
  raw_message_delivery = true
  filter_policy_scope  = "MessageAttributes"
  filter_policy = jsonencode({
    payment = ["approved"]
  })

  depends_on = [aws_sqs_queue_policy.order_billing]
}

resource "aws_sns_topic_subscription" "order_shipping" {
  topic_arn            = aws_sns_topic.orders.arn
  protocol             = "sqs"
  endpoint             = aws_sqs_queue.order_shipping.arn
  raw_message_delivery = true
  filter_policy_scope  = "MessageAttributes"
  filter_policy = jsonencode({
    payment  = ["approved"]
    itemType = ["physical"]
    risk     = ["clear"]
  })

  depends_on = [aws_sqs_queue_policy.order_shipping]
}

resource "aws_sns_topic_subscription" "order_risk" {
  topic_arn           = aws_sns_topic.orders.arn
  protocol            = "lambda"
  endpoint            = aws_lambda_function.order_risk.arn
  filter_policy_scope = "MessageAttributes"
  filter_policy = jsonencode({
    risk = ["review"]
  })
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.order_subscription_dlq.arn
  })

  depends_on = [aws_sqs_queue_policy.order_subscription_dlq]
}

resource "aws_sns_topic_subscription" "order_customer" {
  topic_arn           = aws_sns_topic.orders.arn
  protocol            = "lambda"
  endpoint            = aws_lambda_function.order_customer.arn
  filter_policy_scope = "MessageAttributes"
  filter_policy = jsonencode({
    payment          = ["approved"]
    hasCustomerEmail = ["true"]
    risk             = ["clear"]
  })
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.order_subscription_dlq.arn
  })

  depends_on = [aws_sqs_queue_policy.order_subscription_dlq]
}

resource "aws_sns_topic_subscription" "order_ops" {
  count               = var.order_ops_email == "" ? 0 : 1
  topic_arn           = aws_sns_topic.orders.arn
  protocol            = "email"
  endpoint            = var.order_ops_email
  filter_policy_scope = "MessageAttributes"
  filter_policy = jsonencode({
    opsRoute = ["missing-email", "urgent"]
  })
}

resource "aws_iam_role" "order_place" {
  name               = "${var.environment}-order-place"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy_attachment" "order_place_logs" {
  role       = aws_iam_role.order_place.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "order_place_publish" {
  name = "${var.environment}-order-place-publish"
  role = aws_iam_role.order_place.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["sns:Publish"]
      Resource = aws_sns_topic.orders.arn
    }]
  })
}

resource "aws_iam_role" "order_worker" {
  name               = "${var.environment}-order-worker"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy_attachment" "order_worker_logs" {
  role       = aws_iam_role.order_worker.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "order_worker_sqs" {
  role       = aws_iam_role.order_worker.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole"
}

resource "aws_iam_role" "order_risk" {
  name               = "${var.environment}-order-risk"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy_attachment" "order_risk_logs" {
  role       = aws_iam_role.order_risk.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role" "order_customer" {
  name               = "${var.environment}-order-customer"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy_attachment" "order_customer_logs" {
  role       = aws_iam_role.order_customer.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "order_customer_ses" {
  count = var.order_ses_from_email == "" ? 0 : 1
  name  = "${var.environment}-order-customer-ses"
  role  = aws_iam_role.order_customer.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["ses:SendEmail"]
      Resource = "arn:aws:ses:${var.aws_region}:${data.aws_caller_identity.current.account_id}:identity/${var.order_ses_from_email}"
    }]
  })
}

resource "aws_ses_email_identity" "order_from" {
  count = var.order_ses_from_email == "" ? 0 : 1
  email = var.order_ses_from_email
}

data "aws_caller_identity" "current" {}

resource "aws_cloudwatch_log_group" "order_place" {
  name              = "/aws/lambda/${var.environment}-order-place"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "order_billing" {
  name              = "/aws/lambda/${var.environment}-order-billing"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "order_shipping" {
  name              = "/aws/lambda/${var.environment}-order-shipping"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "order_risk" {
  name              = "/aws/lambda/${var.environment}-order-risk"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "order_customer" {
  name              = "/aws/lambda/${var.environment}-order-customer"
  retention_in_days = 14
}

resource "aws_lambda_function" "order_place" {
  function_name    = "${var.environment}-order-place"
  description      = "Accept one checkout and publish it to the order-events topic."
  role             = aws_iam_role.order_place.arn
  handler          = "orders.place"
  runtime          = "python3.12"
  filename         = data.archive_file.lambda_codes.output_path
  source_code_hash = data.archive_file.lambda_codes.output_base64sha256
  timeout          = 10
  memory_size      = 256

  environment {
    variables = {
      TOPIC_ARN = aws_sns_topic.orders.arn
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.order_place_logs,
    aws_iam_role_policy.order_place_publish,
    aws_cloudwatch_log_group.order_place,
  ]
}

resource "aws_lambda_function" "order_billing" {
  function_name    = "${var.environment}-order-billing"
  description      = "Record an approved order drained from the billing queue."
  role             = aws_iam_role.order_worker.arn
  handler          = "orders.billing"
  runtime          = "python3.12"
  filename         = data.archive_file.lambda_codes.output_path
  source_code_hash = data.archive_file.lambda_codes.output_base64sha256
  timeout          = 15
  memory_size      = 256

  depends_on = [
    aws_iam_role_policy_attachment.order_worker_logs,
    aws_iam_role_policy_attachment.order_worker_sqs,
    aws_cloudwatch_log_group.order_billing,
  ]
}

resource "aws_lambda_function" "order_shipping" {
  function_name    = "${var.environment}-order-shipping"
  description      = "Pack a clear physical order drained from the shipping queue."
  role             = aws_iam_role.order_worker.arn
  handler          = "orders.shipping"
  runtime          = "python3.12"
  filename         = data.archive_file.lambda_codes.output_path
  source_code_hash = data.archive_file.lambda_codes.output_base64sha256
  timeout          = 15
  memory_size      = 256

  depends_on = [
    aws_iam_role_policy_attachment.order_worker_logs,
    aws_iam_role_policy_attachment.order_worker_sqs,
    aws_cloudwatch_log_group.order_shipping,
  ]
}

resource "aws_lambda_function" "order_risk" {
  function_name    = "${var.environment}-order-risk"
  description      = "Hold an order whose shipping country differs from its billing country."
  role             = aws_iam_role.order_risk.arn
  handler          = "orders.risk"
  runtime          = "python3.12"
  filename         = data.archive_file.lambda_codes.output_path
  source_code_hash = data.archive_file.lambda_codes.output_base64sha256
  timeout          = 15
  memory_size      = 256

  depends_on = [
    aws_iam_role_policy_attachment.order_risk_logs,
    aws_cloudwatch_log_group.order_risk,
  ]
}

resource "aws_lambda_function" "order_customer" {
  function_name    = "${var.environment}-order-customer"
  description      = "Send the order confirmation to the customer address through SES."
  role             = aws_iam_role.order_customer.arn
  handler          = "orders.customer"
  runtime          = "python3.12"
  filename         = data.archive_file.lambda_codes.output_path
  source_code_hash = data.archive_file.lambda_codes.output_base64sha256
  timeout          = 15
  memory_size      = 256

  environment {
    variables = {
      SES_FROM_EMAIL = var.order_ses_from_email
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.order_customer_logs,
    aws_cloudwatch_log_group.order_customer,
  ]
}

resource "aws_lambda_event_source_mapping" "order_billing" {
  event_source_arn = aws_sqs_queue.order_billing.arn
  function_name    = aws_lambda_function.order_billing.arn
  batch_size       = 1
}

resource "aws_lambda_event_source_mapping" "order_shipping" {
  event_source_arn = aws_sqs_queue.order_shipping.arn
  function_name    = aws_lambda_function.order_shipping.arn
  batch_size       = 1
}

resource "aws_lambda_permission" "order_risk" {
  statement_id  = "AllowOrderTopic"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.order_risk.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.orders.arn
}

resource "aws_lambda_permission" "order_customer" {
  statement_id  = "AllowOrderTopic"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.order_customer.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.orders.arn
}

resource "aws_apigatewayv2_integration" "orders" {
  api_id                 = aws_apigatewayv2_api.ledger.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.order_place.invoke_arn
  payload_format_version = "2.0"
  timeout_milliseconds   = 10000
}

resource "aws_apigatewayv2_route" "orders" {
  api_id    = aws_apigatewayv2_api.ledger.id
  route_key = "POST /orders"
  target    = "integrations/${aws_apigatewayv2_integration.orders.id}"
}

resource "aws_lambda_permission" "orders_api" {
  statement_id  = "AllowAPIGatewayOrders"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.order_place.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.ledger.execution_arn}/*/POST/orders"
}

data "archive_file" "lambda_codes" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda"
  output_path = "${path.module}/lambda_codes.zip"
}

data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_exec" {
  name               = "${var.environment}-ledger-lambda-exec"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_sqs" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole"
}

resource "aws_cloudwatch_log_group" "direct_lambda" {
  name              = "/aws/lambda/${var.environment}-direct-lambda"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "queue_lambda" {
  name              = "/aws/lambda/${var.environment}-queue-lambda"
  retention_in_days = 14
}

resource "aws_lambda_function" "direct_lambda" {
  function_name = "${var.environment}-direct-lambda"
  description   = "Architecture A: synchronous ledger commit with a hard concurrency cap."
  role          = aws_iam_role.lambda_exec.arn
  handler       = "index.handler"
  runtime       = "python3.12"
  filename      = data.archive_file.lambda_codes.output_path
  source_code_hash = data.archive_file.lambda_codes.output_base64sha256
  timeout       = 20
  memory_size   = 256

  # Two reserved slots. The other 98 of a 100-wide burst are throttled with 429
  # before they can enter the 1.5 second ledger critical section.
  reserved_concurrent_executions = 2

  environment {
    variables = {
      LEDGER_MODE = "DIRECT"
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic,
    aws_cloudwatch_log_group.direct_lambda,
  ]
}

resource "aws_lambda_function" "queue_lambda" {
  function_name = "${var.environment}-queue-lambda"
  description   = "Architecture B: asynchronous ledger consumer drained from the SQS buffer."
  role          = aws_iam_role.lambda_exec.arn
  handler       = "index.handler"
  runtime       = "python3.12"
  filename         = data.archive_file.lambda_codes.output_path
  source_code_hash = data.archive_file.lambda_codes.output_base64sha256
  timeout          = 60
  memory_size      = 256

  environment {
    variables = {
      LEDGER_MODE = "QUEUED"
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic,
    aws_iam_role_policy_attachment.lambda_sqs,
    aws_cloudwatch_log_group.queue_lambda,
  ]
}

resource "aws_lambda_event_source_mapping" "queue" {
  event_source_arn = aws_sqs_queue.buffer.arn
  function_name    = aws_lambda_function.queue_lambda.arn
  batch_size       = 10
}

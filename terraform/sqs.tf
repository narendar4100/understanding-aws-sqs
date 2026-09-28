# Standard queue by design. It gives Architecture B a durable buffer so the
# HTTP callers are not limited by the ledger's 1.5 second commit. It does not
# preserve order or suppress duplicates. A production posting path for this
# ledger should be FIFO, with one message group per account. See the dashboard
# deep-dive for that discussion.
resource "aws_sqs_queue" "buffer" {
  name                       = "${var.environment}-buffer-queue"
  message_retention_seconds  = 86400
  visibility_timeout_seconds = 360
}

resource "aws_s3_bucket" "frontend" {
  bucket        = local.frontend_bucket
  force_destroy = true
}

resource "aws_s3_bucket_ownership_controls" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_server_side_encryption_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }
}

data "aws_iam_policy_document" "frontend_public_read" {
  statement {
    sid       = "PublicReadGetObject"
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.frontend.arn}/*"]

    principals {
      type        = "*"
      identifiers = ["*"]
    }
  }
}

resource "aws_s3_bucket_policy" "frontend" {
  bucket     = aws_s3_bucket.frontend.id
  policy     = data.aws_iam_policy_document.frontend_public_read.json
  depends_on = [aws_s3_bucket_public_access_block.frontend]
}

resource "aws_s3_object" "index" {
  bucket        = aws_s3_bucket.frontend.id
  key           = "index.html"
  source        = "${path.module}/../frontend/index.html"
  etag          = filemd5("${path.module}/../frontend/index.html")
  content_type  = "text/html; charset=utf-8"
  cache_control = "no-cache"
}

resource "aws_s3_object" "sqs_index" {
  bucket        = aws_s3_bucket.frontend.id
  key           = "sqs/index.html"
  source        = "${path.module}/../frontend/sqs/index.html"
  etag          = filemd5("${path.module}/../frontend/sqs/index.html")
  content_type  = "text/html; charset=utf-8"
  cache_control = "no-cache"
}

resource "aws_s3_object" "sns_index" {
  bucket        = aws_s3_bucket.frontend.id
  key           = "sns/index.html"
  source        = "${path.module}/../frontend/sns.html"
  etag          = filemd5("${path.module}/../frontend/sns.html")
  content_type  = "text/html; charset=utf-8"
  cache_control = "no-cache"
}

resource "aws_s3_object" "site_css" {
  bucket        = aws_s3_bucket.frontend.id
  key           = "assets/site.css"
  source        = "${path.module}/../frontend/assets/site.css"
  etag          = filemd5("${path.module}/../frontend/assets/site.css")
  content_type  = "text/css; charset=utf-8"
  cache_control = "public, max-age=300"
}

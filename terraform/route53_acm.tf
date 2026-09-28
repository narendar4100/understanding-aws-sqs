data "aws_route53_zone" "primary" {
  name         = "${var.domain_name}."
  private_zone = false
}

resource "aws_acm_certificate" "api" {
  domain_name       = local.api_fqdn
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "acm_validation" {
  zone_id         = data.aws_route53_zone.primary.zone_id
  name            = tolist(aws_acm_certificate.api.domain_validation_options)[0].resource_record_name
  type            = tolist(aws_acm_certificate.api.domain_validation_options)[0].resource_record_type
  records         = [tolist(aws_acm_certificate.api.domain_validation_options)[0].resource_record_value]
  ttl             = 60
  allow_overwrite = true
}

resource "aws_acm_certificate_validation" "api" {
  certificate_arn         = aws_acm_certificate.api.arn
  validation_record_fqdns = [aws_route53_record.acm_validation.fqdn]

  timeouts {
    create = "45m"
  }
}

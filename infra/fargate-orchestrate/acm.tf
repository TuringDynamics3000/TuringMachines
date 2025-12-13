# ACM Certificate for orchestrate.turingmachines.io
resource "aws_acm_certificate" "orchestrate" {
  domain_name               = "orchestrate.turingmachines.io"
  subject_alternative_names = ["api.turingmachines.io"]
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

# DNS validation records (auto-created)
resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.orchestrate.domain_validation_options :
    dvo.domain_name => {
      name  = dvo.resource_record_name
      type  = dvo.resource_record_type
      value = dvo.resource_record_value
    }
  }

  zone_id = aws_route53_zone.turingmachines.zone_id
  name    = each.value.name
  type    = each.value.type
  ttl     = 60
  records = [each.value.value]
}

# Certificate validation resource
resource "aws_acm_certificate_validation" "orchestrate" {
  certificate_arn         = aws_acm_certificate.orchestrate.arn
  validation_record_fqdns = [
    for r in aws_route53_record.cert_validation : r.fqdn
  ]
}

# Output certificate ARN
output "certificate_arn" {
  value       = aws_acm_certificate.orchestrate.arn
  description = "ACM certificate ARN for HTTPS"
}

# Route 53 Hosted Zone for turingmachines.io
resource "aws_route53_zone" "turingmachines" {
  name = "turingmachines.io"
}

# DNS records for ALB (created after ALB exists)
resource "aws_route53_record" "orchestrate_dns" {
  zone_id = aws_route53_zone.turingmachines.zone_id
  name    = "orchestrate"
  type    = "A"

  alias {
    name                   = aws_lb.orchestrate.dns_name
    zone_id                = aws_lb.orchestrate.zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "api_dns" {
  zone_id = aws_route53_zone.turingmachines.zone_id
  name    = "api"
  type    = "A"

  alias {
    name                   = aws_lb.orchestrate.dns_name
    zone_id                = aws_lb.orchestrate.zone_id
    evaluate_target_health = true
  }
}

# Output nameservers for registrar update
output "route53_nameservers" {
  value       = aws_route53_zone.turingmachines.name_servers
  description = "Update these nameservers at your domain registrar"
}

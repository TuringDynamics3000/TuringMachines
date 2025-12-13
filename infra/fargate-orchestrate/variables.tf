variable "aws_region" {
  type = string
}

variable "environment" {
  type = string
}

variable "project_name" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "container_image" {
  type = string
}

variable "database_secret_arn" {
  type = string
}
variable "ecs_subnet_ids" {
  description = "Subnet IDs for ECS tasks (must have VPC endpoint access)"
  type        = list(string)
}

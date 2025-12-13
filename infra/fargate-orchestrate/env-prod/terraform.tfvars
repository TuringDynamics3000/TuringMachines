environment           = "prod"
project_name          = "turing-orchestrate"

aws_region            = "ap-southeast-2"
vpc_id                = "vpc-0e237a196328b3fbd"

ecs_subnet_ids = [
  "subnet-05ce2187d20d8caa7",
  "subnet-0585b15eb8ab99400",
  "subnet-093b4c0062b604657"
]

container_image       = "961971040149.dkr.ecr.ap-southeast-2.amazonaws.com/turing-orchestrate:latest"
database_secret_arn   = "arn:aws:secretsmanager:ap-southeast-2:961971040149:secret:turing/orchestrate/database_url"

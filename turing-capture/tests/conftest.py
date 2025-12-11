# ----------------------------------------
# CONFIGURATION — EDIT THESE VALUES
# ----------------------------------------

$Region = "ap-southeast-2"
$AWSAccountId = "204727484975"
$Project = "turingmachines-dev"
$S3Bucket = "$Project-artifacts-$(Get-Random)"
$DBUser = "turingadmin"
$DBPassword = "IronBaron@#1431"
$DBName = "turingdb"
$CaptureLocalPath = "C:\Users\mjmil\Documents\turingmachines\turing-capture"
$OrchestrateLocalPath = "C:\Users\mjmil\Documents\turingmachines\turing-orchestrate"

# ----------------------------------------
# AWS LOGIN CHECK
# ----------------------------------------
Write-Host "Checking AWS credentials..."
aws sts get-caller-identity --region $Region
if ($LASTEXITCODE -ne 0) {
    Write-Error "AWS CLI not authenticated. Run 'aws configure' first."
    exit 1
}

# ----------------------------------------
# CREATE S3 BUCKET
# ----------------------------------------
Write-Host "Creating S3 bucket: $S3Bucket"
aws s3api create-bucket `
    --bucket $S3Bucket `
    --region $Region `
    --create-bucket-configuration LocationConstraint=$Region

aws s3api put-public-access-block `
    --bucket $S3Bucket `
    --public-access-block-configuration `
        "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

Write-Host "S3 bucket created."

# ----------------------------------------
# CREATE ECR REPOSITORIES
# ----------------------------------------
$Repos = @("turing-capture", "turing-orchestrate")

foreach ($repo in $Repos) {
    Write-Host "Creating ECR repo: $repo"
    aws ecr create-repository `
        --repository-name "$repo" `
        --region $Region
}

# ----------------------------------------
# DOCKER LOGIN
# ----------------------------------------
Write-Host "Logging in to ECR..."
aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin "$AWSAccountId.dkr.ecr.$Region.amazonaws.com"

# ----------------------------------------
# BUILD + PUSH DOCKER IMAGES
# ----------------------------------------
Write-Host "Building & pushing Docker images..."

# ---- TuringCapture ----
cd $CaptureLocalPath
docker build -t turing-capture .
docker tag turing-capture:latest "$AWSAccountId.dkr.ecr.$Region.amazonaws.com/turing-capture:latest"
docker push "$AWSAccountId.dkr.ecr.$Region.amazonaws.com/turing-capture:latest"

# ---- TuringOrchestrate ----
cd $OrchestrateLocalPath
docker build -t turing-orchestrate .
docker tag turing-orchestrate:latest "$AWSAccountId.dkr.ecr.$Region.amazonaws.com/turing-orchestrate:latest"
docker push "$AWSAccountId.dkr.ecr.$Region.amazonaws.com/turing-orchestrate:latest"

Write-Host "Docker images pushed."

# ----------------------------------------
# STORE DB CREDENTIALS IN SECRETS MANAGER
# ----------------------------------------
Write-Host "Creating Secrets Manager secret..."

$SecretJson = @{
    username = $DBUser
    password = $DBPassword
} | ConvertTo-Json -Compress

aws secretsmanager create-secret `
    --name "$Project/postgres" `
    --description "TuringMachines Dev Postgres Credentials" `
    --secret-string "$SecretJson" `
    --region $Region

Write-Host "Secrets Manager entry created."

# ----------------------------------------
# CREATE RDS POSTGRES INSTANCE
# ----------------------------------------
Write-Host "Creating RDS Postgres instance..."

aws rds create-db-instance `
    --db-instance-identifier "$Project-postgres" `
    --allocated-storage 20 `
    --db-instance-class db.t3.micro `
    --engine postgres `
    --master-username $DBUser `
    --master-user-password $DBPassword `
    --backup-retention-period 0 `
    --publicly-accessible false `
    --db-name $DBName `
    --region $Region

Write-Host "RDS creation started. It may take 5–8 minutes."

# ----------------------------------------
# WAIT FOR RDS TO BECOME AVAILABLE
# ----------------------------------------
Write-Host "Waiting for RDS to become available..."
aws rds wait db-instance-available --db-instance-identifier "$Project-postgres" --region $Region

$DBEndpointJson = aws rds describe-db-instances `
    --db-instance-identifier "$Project-postgres" `
    --query "DBInstances[0].Endpoint.Address" `
    --output text `
    --region $Region

$DBEndpoint = $DBEndpointJson.Trim('"')

Write-Host "RDS Endpoint:" $DBEndpoint

# ----------------------------------------
# CREATE ECS CLUSTER
# ----------------------------------------
Write-Host "Creating ECS cluster..."

aws ecs create-cluster `
    --cluster-name "$Project-cluster" `
    --region $Region

# ----------------------------------------
# GENERATE TASK DEFINITION JSON (Capture)
# ----------------------------------------
Write-Host "Creating Capture task definition..."

$CaptureTask = @"
{
  "family": "turing-capture",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::$AWSAccountId:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::$AWSAccountId:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "turing-capture",
      "image": "$AWSAccountId.dkr.ecr.$Region.amazonaws.com/turing-capture:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        { "name": "S3_BUCKET", "value": "$S3Bucket" },
        { "name": "DB_HOST", "value": "$DBEndpoint" },
        { "name": "DB_NAME", "value": "$DBName" },
        { "name": "SECRET_NAME", "value": "$Project/postgres" }
      ]
    }
  ]
}
"@

$CaptureTask | Out-File "capture-task.json"

aws ecs register-task-definition `
    --cli-input-json file://capture-task.json `
    --region $Region

# ----------------------------------------
# GENERATE TASK DEFINITION JSON (Orchestrate)
# ----------------------------------------
Write-Host "Creating Orchestrate task definition..."

$OrchestrateTask = @"
{
  "family": "turing-orchestrate",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::$AWSAccountId:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::$AWSAccountId:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "turing-orchestrate",
      "image": "$AWSAccountId.dkr.ecr.$Region.amazonaws.com/turing-orchestrate:latest",
      "portMappings": [
        {
          "containerPort": 8010,
          "protocol": "tcp"
        }
      ],
      "environment": [
        { "name": "DB_HOST", "value": "$DBEndpoint" },
        { "name": "DB_NAME", "value": "$DBName" },
        { "name": "SECRET_NAME", "value": "$Project/postgres" }
      ]
    }
  ]
}
"@

$OrchestrateTask | Out-File "orchestrate-task.json"

aws ecs register-task-definition `
    --cli-input-json file://orchestrate-task.json `
    --region $Region

# ----------------------------------------
# CREATE ECS SERVICES (Cluster must exist)
# ----------------------------------------
Write-Host "Deploying ECS Service: TuringCapture..."

aws ecs create-service `
    --cluster "$Project-cluster" `
    --service-name "turing-capture-svc" `
    --task-definition "turing-capture" `
    --desired-count 1 `
    --launch-type FARGATE `
    --network-configuration "awsvpcConfiguration={subnets=[],securityGroups=[],assignPublicIp=ENABLED}" `
    --region $Region

Write-Host "Deploying ECS Service: TuringOrchestrate..."

aws ecs create-service `
    --cluster "$Project-cluster" `
    --service-name "turing-orchestrate-svc" `
    --task-definition "turing-orchestrate" `
    --desired-count 1 `
    --launch-type FARGATE `
    --network-configuration "awsvpcConfiguration={subnets=[],securityGroups=[],assignPublicIp=ENABLED}" `
    --region $Region

Write-Host "Deployment complete."
Write-Host "Your services are launching in ECS."

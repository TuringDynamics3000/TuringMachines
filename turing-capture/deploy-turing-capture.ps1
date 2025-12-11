# =========================
# TuringCapture ECS Deployment (CI/CD Safe)
# =========================

# --- Configuration ---
$AWSRegion      = "ap-southeast-2"
$ECRRepo        = "961971040149.dkr.ecr.$AWSRegion.amazonaws.com/turing-capture"
$ServiceName    = "turing-capture-svc"
$ClusterName    = "turingmachines-dev-cluster"
$TaskFamily     = "turing-capture"
$ContainerJSON  = "container-only.json"
$CPU            = "256"
$Memory         = "512"
$NetworkMode    = "awsvpc"
$Compatibility  = "FARGATE"
$ExecutionRole  = "arn:aws:iam::961971040149:role/ecsTaskExecutionRole"
$TaskRole       = "arn:aws:iam::961971040149:role/ecsTaskExecutionRole"
$PollInterval   = 5   # seconds
$MaxWaitTime    = 300 # seconds

# --- Step 1: Build Docker image ---
Write-Host "`n[1] Building Docker image..."
docker build -t turing-capture:latest .

# --- Step 2: Tag Docker image for ECR ---
Write-Host "`n[2] Tagging Docker image for ECR..."
docker tag turing-capture:latest "$ECRRepo:latest"

# --- Step 3: Push Docker image to ECR ---
Write-Host "`n[3] Pushing Docker image to ECR..."
docker push "$ECRRepo:latest"

# --- Step 4: Register ECS task definition ---
Write-Host "`n[4] Registering/updating ECS task definition..."
$TaskDef = aws ecs register-task-definition `
    --family $TaskFamily `
    --execution-role-arn $ExecutionRole `
    --task-role-arn $TaskRole `
    --cpu $CPU `
    --memory $Memory `
    --network-mode $NetworkMode `
    --requires-compatibilities $Compatibility `
    --container-definitions "file://$ContainerJSON" `
    --region $AWSRegion | ConvertFrom-Json

$Revision = $TaskDef.taskDefinition.taskDefinitionArn
Write-Host "✅ Task definition registered: $Revision"

# --- Step 5: Update ECS service ---
Write-Host "`n[5] Updating ECS service to new task revision..."
aws ecs update-service `
    --cluster $ClusterName `
    --service $ServiceName `
    --task-definition $Revision `
    --force-new-deployment `
    --region $AWSRegion

# --- Step 6: Poll ECS service until deployment is stable ---
Write-Host "`n[6] Waiting for ECS service to stabilize..."
$elapsed = 0
while ($true) {
    $service = aws ecs describe-services `
        --cluster $ClusterName `
        --services $ServiceName `
        --region $AWSRegion | ConvertFrom-Json

    $running   = $service.services[0].runningCount
    $desired   = $service.services[0].desiredCount
    $deploying = $service.services[0].deployments | Where-Object { $_.status -eq "PRIMARY" }

    Write-Host "Running: $running / Desired: $desired, Deployment state: $($deploying.rolloutState)"

    # --- Check for any failed tasks ---
    $tasks = aws ecs list-tasks `
        --cluster $ClusterName `
        --service-name $ServiceName `
        --region $AWSRegion | ConvertFrom-Json
    if ($tasks.taskArns.Count -gt 0) {
        $taskDetails = aws ecs describe-tasks `
            --cluster $ClusterName `
            --tasks ($tasks.taskArns -join " ") `
            --region $AWSRegion | ConvertFrom-Json
        foreach ($t in $taskDetails.tasks) {
            if ($t.lastStatus -eq "STOPPED" -and $t.desiredStatus -eq "RUNNING") {
                Write-Host "❌ Task $($t.taskArn) stopped unexpectedly! Deployment failed." -ForegroundColor Red
                exit 1
            }
            if ($t.containers | Where-Object { $_.healthStatus -eq "UNHEALTHY" }) {
                Write-Host "❌ Task $($t.taskArn) has unhealthy container(s)! Deployment failed." -ForegroundColor Red
                exit 1
            }
        }
    }

    if ($running -eq $desired -and $deploying.rolloutState -eq "COMPLETED") {
        Write-Host "✅ ECS service is stable!"
        break
    }

    Start-Sleep -Seconds $PollInterval
    $elapsed += $PollInterval
    if ($elapsed -ge $MaxWaitTime) {
        Write-Host "⚠️ Timeout reached. ECS service may not be fully stable."
        break
    }
}

# --- Step 7: Tail ECS logs ---
Write-Host "`n[7] Tailing logs from ECS service..."
Write-Host "Press Ctrl+C to stop following logs."
aws logs tail "/ecs/$ServiceName" --region $AWSRegion --follow

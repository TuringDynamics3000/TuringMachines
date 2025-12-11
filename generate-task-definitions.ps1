param(
    [string]$AccountId = "961971040149",
    [string]$Region = "ap-southeast-2",
    [string]$BucketName = "turingmachines-dev-artifacts-490189534",
    [string]$DbHost = "turingmachines-dev-postgres.cvyyew6ce7us.ap-southeast-2.rds.amazonaws.com",
    [string]$DbName = "turingdb",
    [string]$SecretName = "turingmachines-dev/postgres"
)

function Write-JsonFile {
    param([object]$Obj, [string]$FileName)
    $json = $Obj | ConvertTo-Json -Depth 40
    Set-Content -Path $FileName -Value $json -Encoding UTF8
}

# ============================================================================================
# Capture Task Definition (ordered)
# ============================================================================================

$captureTask = [ordered]@{
    family = "turing-capture"
    taskRoleArn = "arn:aws:iam::$AccountId:role/ecsTaskExecutionRole"
    executionRoleArn = "arn:aws:iam::$AccountId:role/ecsTaskExecutionRole"
    networkMode = "awsvpc"

    containerDefinitions = @(
        [ordered]@{
            name = "turing-capture"
            image = "$AccountId.dkr.ecr.$Region.amazonaws.com/turing-capture:latest"
            essential = $true

            portMappings = @(
                [ordered]@{
                    containerPort = 8000
                    protocol = "tcp"
                }
            )

            logConfiguration = [ordered]@{
                logDriver = "awslogs"
                options   = [ordered]@{
                    "awslogs-group" = "/ecs/turing-capture"
                    "awslogs-region" = $Region
                    "awslogs-stream-prefix" = "ecs"
                }
            }

            environment = @(
                [ordered]@{ name = "S3_BUCKET";   value = $BucketName },
                [ordered]@{ name = "DB_HOST";     value = $DbHost },
                [ordered]@{ name = "DB_NAME";     value = $DbName },
                [ordered]@{ name = "SECRET_NAME"; value = $SecretName }
            )
        }
    )

    requiresCompatibilities = @("FARGATE")
    cpu = 256
    memory = 512

    runtimePlatform = [ordered]@{
        operatingSystemFamily = "LINUX"
        cpuArchitecture = "X86_64"
    }
}

Write-JsonFile -Obj $captureTask -FileName "capture-task.json"

# ============================================================================================
# Orchestrate Task Definition (ordered)
# ============================================================================================

$orchestrateTask = [ordered]@{
    family = "turing-orchestrate"
    taskRoleArn = "arn:aws:iam::$AccountId:role/ecsTaskExecutionRole"
    executionRoleArn = "arn:aws:iam::$AccountId:role/ecsTaskExecutionRole"
    networkMode = "awsvpc"

    containerDefinitions = @(
        [ordered]@{
            name = "turing-orchestrate"
            image = "$AccountId.dkr.ecr.$Region.amazonaws.com/turing-orchestrate:latest"
            essential = $true

            portMappings = @(
                [ordered]@{
                    containerPort = 8010
                    protocol = "tcp"
                }
            )

            logConfiguration = [ordered]@{
                logDriver = "awslogs"
                options   = [ordered]@{
                    "awslogs-group" = "/ecs/turing-orchestrate"
                    "awslogs-region" = $Region
                    "awslogs-stream-prefix" = "ecs"
                }
            }

            environment = @(
                [ordered]@{ name = "DB_HOST";     value = $DbHost },
                [ordered]@{ name = "DB_NAME";     value = $DbName },
                [ordered]@{ name = "SECRET_NAME"; value = $SecretName }
            )
        }
    )

    requiresCompatibilities = @("FARGATE")
    cpu = 256
    memory = 512

    runtimePlatform = [ordered]@{
        operatingSystemFamily = "LINUX"
        cpuArchitecture = "X86_64"
    }
}

Write-JsonFile -Obj $orchestrateTask -FileName "orchestrate-task.json"

Write-Host "Registering tasks..."

aws ecs register-task-definition --cli-input-json file://capture-task.json --region $Region
aws ecs register-task-definition --cli-input-json file://orchestrate-task.json --region $Region

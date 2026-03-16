# AWS Deployment Guide for Swatantra Backend

## Architecture Overview

```
Internet
    ↓
CloudFront (CDN) → S3 (Frontend)
    ↓
API Gateway / ALB
    ↓
ECS Fargate Cluster
    ↓
RDS PostgreSQL + Secrets Manager
    ↓
CloudWatch Logs
```

## Prerequisites

1. AWS Account with appropriate permissions
2. AWS CLI configured: `aws configure`
3. Docker and Docker Compose installed locally
4. Domain name (optional, for custom domain)

## Step-by-Step Deployment

### Phase 1: Database Setup (RDS)

#### 1a. Create RDS PostgreSQL Instance

```bash
# Using AWS Console or CLI
aws rds create-db-instance \
    --db-instance-identifier swatantra-db \
    --db-instance-class db.t3.small \
    --engine postgres \
    --engine-version 15.2 \
    --master-username postgres \
    --master-user-password YourSecurePassword123! \
    --allocated-storage 20 \
    --storage-type gp2 \
    --publicly-accessible false \
    --vpc-security-group-ids sg-xxxxxxxx \
    --db-name swatantra
```

#### 1b. Create RDS Proxy (optional, for connection pooling)

```bash
aws rds create-db-proxy \
    --db-proxy-name swatantra-proxy \
    --engine-family POSTGRESQL \
    --auth \
        [{AuthScheme: SECRETS,
          SecretArn: arn:aws:secretsmanager:...,
          IAMAuth: DISABLED}] \
    --role-arn arn:aws:iam::ACCOUNT_ID:role/service-role/RDSProxyRole \
    --target-group-config DBPortGroupConfig={DBPort=5432}
```

#### 1c. Store Database Credentials in Secrets Manager

```bash
aws secretsmanager create-secret \
    --name swatantra/rds/credentials \
    --secret-string '{
        "username":"postgres",
        "password":"YourSecurePassword123!",
        "host":"swatantra-db.xxxxx.us-east-1.rds.amazonaws.com",
        "port":5432,
        "dbname":"swatantra"
    }'
```

### Phase 2: Container Registry (ECR)

#### 2a. Create ECR Repository

```bash
aws ecr create-repository \
    --repository-name swatantra-backend \
    --region us-east-1
```

#### 2b. Build and Push Docker Image

```bash
# Get ECR login token
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t swatantra-backend:latest .

# Tag for ECR
docker tag swatantra-backend:latest \
    YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/swatantra-backend:latest

# Push to ECR
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/swatantra-backend:latest
```

### Phase 3: ECS Deployment

#### 3a. Create ECS Task Definition

Create `ecs-task-definition.json`:

```json
{
  "family": "swatantra-backend",
  "containerDefinitions": [
    {
      "name": "swatantra-backend",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/swatantra-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "DEBUG", "value": "False"},
        {"name": "DB_TYPE", "value": "postgresql"},
        {"name": "POSTGRES_DB", "value": "swatantra"}
      ],
      "secrets": [
        {
          "name": "POSTGRES_USER",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:swatantra/rds/credentials:username::"
        },
        {
          "name": "POSTGRES_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:swatantra/rds/credentials:password::"
        },
        {
          "name": "POSTGRES_HOST",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:swatantra/rds/credentials:host::"
        },
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:swatantra/openai/api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/swatantra-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "essential": true
    }
  ],
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "256",
  "memory": "512",
  "taskRoleArn": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskRole",
  "executionRoleArn": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskExecutionRole"
}
```

#### 3b. Register Task Definition

```bash
aws ecs register-task-definition \
    --cli-input-json file://ecs-task-definition.json
```

#### 3c. Create ECS Cluster

```bash
aws ecs create-cluster --cluster-name swatantra-cluster
```

#### 3d. Create Load Balancer

```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer \
    --name swatantra-alb \
    --subnets subnet-xxxxx subnet-yyyyy \
    --security-groups sg-zzzzz \
    --scheme internet-facing \
    --type application

# Create target group
aws elbv2 create-target-group \
    --name swatantra-tg \
    --protocol HTTP \
    --port 8000 \
    --vpc-id vpc-xxxxx

# Create listener
aws elbv2 create-listener \
    --load-balancer-arn arn:aws:elasticloadbalancing:...:loadbalancer/app/swatantra-alb/... \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...:targetgroup/swatantra-tg/...
```

#### 3e. Create ECS Service

Create `ecs-service.json`:

```json
{
  "cluster": "swatantra-cluster",
  "serviceName": "swatantra-backend-service",
  "taskDefinition": "swatantra-backend:1",
  "desiredCount": 2,
  "launchType": "FARGATE",
  "networkConfiguration": {
    "awsvpcConfiguration": {
      "subnets": ["subnet-xxxxx", "subnet-yyyyy"],
      "securityGroups": ["sg-zzzzz"],
      "assignPublicIp": "DISABLED"
    }
  },
  "loadBalancers": [
    {
      "targetGroupArn": "arn:aws:elasticloadbalancing:...:targetgroup/swatantra-tg/...",
      "containerName": "swatantra-backend",
      "containerPort": 8000
    }
  ]
}
```

```bash
aws ecs create-service --cli-input-json file://ecs-service.json
```

### Phase 4: Auto-Scaling

#### 4a. Create Auto Scaling Target

```bash
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --resource-id service/swatantra-cluster/swatantra-backend-service \
    --scalable-dimension ecs:service:DesiredCount \
    --min-capacity 2 \
    --max-capacity 10
```

#### 4b. Create Scaling Policies

```bash
# CPU utilization
aws application-autoscaling put-scaling-policy \
    --policy-name swatantra-cpu-scaling \
    --service-namespace ecs \
    --resource-id service/swatantra-cluster/swatantra-backend-service \
    --scalable-dimension ecs:service:DesiredCount \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration \
        TargetValue=70.0,PredefinedScalingMetricSpecification={PredefinedScalingMetricType=ECSServiceAverageCPUUtilization}
```

### Phase 5: Monitoring & Logging

#### 5a. Create CloudWatch Log Group

```bash
aws logs create-log-group --log-group-name /ecs/swatantra-backend
```

#### 5b. Create CloudWatch Alarms

```bash
# High CPU
aws cloudwatch put-metric-alarm \
    --alarm-name swatantra-high-cpu \
    --alarm-description "Alert when CPU exceeds 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:swatantra-alerts

# Service unhealthy
aws cloudwatch put-metric-alarm \
    --alarm-name swatantra-unhealthy-tasks \
    --metric-name UnhealthyTaskCount \
    --namespace AWS/ECS \
    --statistic Sum \
    --period 60 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold
```

### Phase 6: CI/CD Pipeline (Optional)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS ECS

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to ECR
        run: |
          aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com
      
      - name: Build and push image
        run: |
          docker build -t swatantra-backend:latest ./backend
          docker tag swatantra-backend:latest ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com/swatantra-backend:latest
          docker push ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com/swatantra-backend:latest
      
      - name: Update ECS service
        run: |
          aws ecs update-service \
            --cluster swatantra-cluster \
            --service swatantra-backend-service \
            --force-new-deployment
```

## Post-Deployment Checklist

- [ ] Database is running and accessible
- [ ] ECS service is healthy (2+ tasks running)
- [ ] ALB is forwarding traffic correctly
- [ ] CloudWatch logs are appearing
- [ ] API health check passes: `curl http://your-alb-dns/api/health`
- [ ] Database sync queue is working (if offline mode)
- [ ] CloudWatch alarms are configured
- [ ] Auto-scaling policies are active
- [ ] Backup strategy for RDS configured
- [ ] SSL/TLS certificate installed (via ACM)

## Cost Optimization

1. **RDS** - Use db.t3.small for dev, db.t3.medium for prod
2. **ECS** - Use Fargate Spot for non-critical workloads
3. **Data Transfer** - Use VPC endpoints to minimize costs
4. **Logs** - Set retention policy (14-30 days)
5. **NAT Gateway** - Use NAT instances for cost savings

## Troubleshooting

### Tasks failing to start
```bash
aws ecs describe-task-definition --task-definition swatantra-backend
aws ecs describe-services --cluster swatantra-cluster --services swatantra-backend-service
aws logs tail /ecs/swatantra-backend --follow
```

### Database connection issues
```bash
# Check security group rules
aws ec2 describe-security-groups --group-ids sg-xxxxx

# Test connection from task
aws ecs execute-command \
    --cluster swatantra-cluster \
    --task <task-id> \
    --container swatantra-backend \
    --interactive \
    --command "/bin/bash"
```

### High costs
```bash
# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/ECS \
    --metric-name CPUUtilization \
    --start-time 2024-01-01T00:00:00Z \
    --end-time 2024-01-02T00:00:00Z \
    --period 3600 \
    --statistics Average
```

## Rollback

```bash
# Revert to previous task definition
aws ecs update-service \
    --cluster swatantra-cluster \
    --service swatantra-backend-service \
    --task-definition swatantra-backend:1  # Specify previous version
```

## Additional Resources

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [AWS RDS PostgreSQL Guide](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
- [AWS Elastic Load Balancing](https://docs.aws.amazon.com/elasticloadbalancing/)
- [AWS CloudWatch Logs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/)

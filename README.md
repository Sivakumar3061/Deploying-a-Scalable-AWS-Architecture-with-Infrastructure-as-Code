# Deploying a Scalable AWS Architecture with Infrastructure as Code

A multi-tier, event-driven AWS architecture provisioned through **Terraform** and **CloudFormation**, demonstrating hybrid Infrastructure-as-Code (IaC) patterns, serverless orchestration, and operational automation using AWS Console, CLI, and Python (Boto3).

> **Academic group project** — University of Maryland, Baltimore County (UMBC), Fall 2025.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Deployment Guide](#deployment-guide)
- [Verification & Testing](#verification--testing)
- [Bonus Features](#bonus-features)
- [Key Outcomes](#key-outcomes)
- [Challenges & Solutions](#challenges--solutions)
- [Future Improvements](#future-improvements)
- [Authors](#authors)

---

## Overview

This project designs, implements, and validates a **scalable, highly available cloud architecture** on AWS using Infrastructure as Code. It combines networking, compute, database, serverless, and orchestration layers into a single end-to-end deployment, demonstrating real-world cloud engineering workflows.

**Core objectives:**

- Provision networking with **Terraform** (VPC, subnets, route tables, security groups, NAT gateway).
- Deploy compute, database, and serverless resources with **CloudFormation** (EC2 Auto Scaling, ALB, RDS, Lambda).
- Build an **event-driven pipeline** triggered by S3 uploads, logged via CloudWatch, and orchestrated through Step Functions.
- Interact with AWS programmatically using **Console, CLI, and Python Boto3**.
- Implement **Auto Scaling, monitoring, and alerting** for production-readiness.

---

## Architecture

```
                          ┌─────────────────────────┐
                          │   Internet Gateway      │
                          └───────────┬─────────────┘
                                      │
                              ┌───────▼────────┐
                              │      ALB       │
                              └───────┬────────┘
                                      │
              ┌───────────────────────┴────────────────────────┐
              │                                                │
       ┌──────▼──────┐  AZ: us-east-1a            ┌────────────▼───┐  AZ: us-east-1b
       │ Public      │                            │ Public         │
       │ Subnet 1    │                            │ Subnet 2       │
       └──────┬──────┘                            └────────┬───────┘
              │                                            │
       ┌──────▼──────┐                            ┌────────▼───────┐
       │ EC2 (Web)   │ ←── Auto Scaling Group ──→ │ EC2 (Web)      │
       └──────┬──────┘                            └────────┬───────┘
              │                                            │
       ┌──────▼──────────────────────────────────────────────────┐
       │            Private Subnets (RDS MySQL)                  │
       └──────────────────────────────────────────────────────────┘

         ┌────────────────────────────────────────────────────┐
         │   S3 Bucket  ──▶  Lambda  ──▶  CloudWatch Logs     │
         │                    │                                │
         │                    └──▶  Step Functions  ──▶  SNS  │
         └────────────────────────────────────────────────────┘
```

**Region:** `us-east-1` (N. Virginia)
**VPC CIDR:** `10.0.0.0/16` across two Availability Zones for high availability.

---

## Tech Stack

| Layer | Service / Tool |
|---|---|
| **Infrastructure as Code** | Terraform, AWS CloudFormation |
| **Networking** | VPC, Subnets (public/private), Internet Gateway, NAT Gateway, Route Tables, Security Groups |
| **Compute** | EC2, Auto Scaling Group, Application Load Balancer (ALB) |
| **Database** | RDS (MySQL) |
| **Serverless** | AWS Lambda (Python 3.12), API Gateway, Step Functions, SNS |
| **Storage** | Amazon S3 |
| **Monitoring** | CloudWatch Logs, CloudWatch Alarms |
| **Automation/SDK** | AWS CLI, Python Boto3 |
| **Version Control** | Git, GitHub |

---

## Repository Structure

```
.
├── terraform/
│   ├── main.tf              # VPC, subnets, IGW, NAT, route tables, security groups
│   ├── variables.tf         # Input variables (region, CIDR blocks, etc.)
│   └── outputs.tf           # Exported IDs consumed by CloudFormation
│
├── cloudformation/
│   └── app-stack.yml        # EC2 ASG, ALB, RDS, Lambda, IAM roles
│
├── lambda/
│   ├── s3_upload_logger.py  # Logs S3 object-created events to CloudWatch
│   └── s3_upload_notify.py  # Publishes upload events to SNS
│
├── boto3/
│   ├── createBucket.py      # Creates an S3 bucket via Boto3
│   ├── upload.py            # Uploads a file to S3
│   ├── EC2_Instances.py     # Lists running EC2 instances
│   └── InvokeLambda.py      # Manually invokes the logger Lambda
│
├── stepfunctions/
│   └── workflow.json        # ASL definition for S3 → Lambda → SNS workflow
│
└── README.md
```

---

## Prerequisites

Before deploying, ensure you have:

- **AWS account** with permissions for VPC, EC2, RDS, Lambda, S3, IAM, CloudFormation, Step Functions, SNS, and API Gateway.
- **AWS CLI v2** configured (`aws configure`) with valid access keys.
- **Terraform** ≥ 1.5.
- **Python** ≥ 3.10 with `boto3` installed (`pip install boto3`).
- An existing **EC2 Key Pair** in `us-east-1` if you plan to SSH into instances.

---

## Deployment Guide

### Step 1 — Provision Networking with Terraform

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

This creates the VPC, two public and two private subnets across two AZs, an Internet Gateway, a NAT Gateway, route tables, and security groups for the ALB, EC2, and RDS layers. The output values (VPC ID, subnet IDs, security group IDs) are used in the CloudFormation step.

### Step 2 — Deploy Compute, Database & Serverless with CloudFormation

```bash
cd ../cloudformation
aws cloudformation create-stack \
  --stack-name AwsProject \
  --template-body file://app-stack.yml \
  --capabilities CAPABILITY_NAMED_IAM
```

Provisioned resources:

- **EC2 Auto Scaling Group** (min 1, max 3) behind an **Application Load Balancer**.
- **RDS MySQL** instance in private subnets (MultiAZ disabled for cost; can be enabled in production).
- **Lambda function** (`project-s3-upload-logger`) for S3 event logging.
- **IAM roles** with least-privilege policies.

Once `CREATE_COMPLETE`, retrieve the load balancer DNS from the stack outputs and open it in a browser to verify the web tier.

### Step 3 — Configure S3 Event Trigger

1. Create an S3 bucket (e.g., `awsproject-uploads-<your-id>`) in `us-east-1`.
2. In the bucket's **Properties → Event notifications**, create a notification:
   - **Event types:** `All object create events`
   - **Destination:** Lambda → `project-s3-upload-logger`
3. AWS will auto-add the required `lambda:InvokeFunction` permission.

Any new upload will now trigger the Lambda, which logs metadata (bucket, key, size, event time) to CloudWatch Logs at `/aws/lambda/project-s3-upload-logger`.

### Step 4 — Configure Auto Scaling Policies

CloudWatch alarms drive scaling:

| Policy | Condition | Action |
|---|---|---|
| Scale Out | CPU > 60% for 2 minutes | Add 1 instance |
| Scale In | CPU < 30% for 5 minutes | Remove 1 instance |

Cooldown: 60 seconds between scaling activities.

---

## Verification & Testing

### Via AWS Console
Verify each resource via its service dashboard: VPC, EC2 (instances + ASG), ALB target groups, RDS, Lambda, S3, CloudWatch Logs.

### Via AWS CLI

```bash
# List EC2 instances
aws ec2 describe-instances \
  --query "Reservations[*].Instances[*].[InstanceId,State.Name,InstanceType,PrivateIpAddress]" \
  --output table

# List S3 buckets
aws s3 ls

# Upload a test file
aws s3 cp test.txt s3://<your-bucket-name>/

# Invoke Lambda manually
aws lambda invoke \
  --function-name project-s3-upload-logger \
  --payload "{}" output.json
cat output.json
```

### Via Python Boto3

Four scripts under `boto3/` demonstrate programmatic interaction:

1. `createBucket.py` — creates a new S3 bucket.
2. `upload.py` — uploads a file to S3.
3. `EC2_Instances.py` — lists EC2 instance IDs and states.
4. `InvokeLambda.py` — invokes the logger Lambda with a custom payload.

---

## Bonus Features

### 1. API Gateway → Lambda (HTTP-triggered serverless)

A **REST API** (`S3UploadLoggerAPI`) exposes the logger Lambda via an HTTP `GET /logupload` endpoint, deployed to the `prod` stage. Useful for triggering the function outside of S3 events (e.g., manual testing, external integrations).

### 2. Step Functions Workflow (S3 → Lambda → SNS)

A **Standard state machine** (`S3UploadWorkflow`) orchestrates two tasks:

1. **RunLoggerLambda** — extracts upload metadata.
2. **SendNotification** — publishes an SNS message that delivers an "S3 Upload Alert" email to subscribers.

The state machine is triggered by S3 `PUT` events, demonstrating event-driven serverless orchestration without manual intervention.

ASL definition:

```json
{
  "Comment": "S3 Upload → Extract Metadata → Notify",
  "StartAt": "RunLoggerLambda",
  "States": {
    "RunLoggerLambda": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:REGION:ACCOUNT:function:project-s3-upload-logger",
      "Next": "SendNotification"
    },
    "SendNotification": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:REGION:ACCOUNT:function:s3-upload-notify",
      "End": true
    }
  }
}
```

---

## Key Outcomes

- Provisioned a complete networking stack via Terraform across two AZs.
- Deployed compute, database, and serverless layers via CloudFormation with explicit `DependsOn` and IAM scoping.
- Configured an **ALB + Auto Scaling Group** for elasticity and high availability.
- Built and validated an **event-driven S3 → Lambda → CloudWatch** pipeline.
- Demonstrated AWS interaction through **three interfaces**: Console, CLI, and Boto3.
- Integrated **API Gateway** for HTTP invocation of Lambda.
- Built a **Step Functions workflow** automating S3-triggered notifications via SNS.

---

## Challenges & Solutions

| # | Challenge | Solution |
|---|---|---|
| 1 | EC2/RDS connectivity failures from misconfigured routing | Reviewed route tables and security group inbound rules; corrected public/private subnet routing |
| 2 | CloudFormation template validation errors and dependency conflicts | Added explicit `DependsOn` attributes, validated with `cfn-lint`, fixed IAM role permissions |
| 3 | Lambda not firing on S3 events | Re-created the S3 event notification and granted S3 invoke permission on the Lambda |
| 4 | Auto Scaling not responding promptly to load | Adjusted CloudWatch alarm evaluation periods and cooldown windows; verified with stress testing |
| 5 | API Gateway returning `403 Forbidden` | Enabled Lambda proxy integration and updated resource-based policy for `apigateway.amazonaws.com` |

---

## Future Improvements

### Scalability
- Add **Multi-AZ RDS** for fault tolerance.
- Introduce **ElastiCache (Redis)** for application-layer caching.
- Migrate EC2 workloads to **ECS / Fargate** for containerized microservices.

### Automation & DevOps
- CI/CD pipeline using **GitHub Actions** + **CodePipeline / CodeDeploy** for automated IaC and Lambda deployment.
- Use **Terraform Cloud** or an **S3 + DynamoDB remote backend** for collaborative state management with locking.
- Implement **S3 lifecycle policies** and Glacier archival for cost optimization.

### Monitoring & Security
- Enable **AWS GuardDuty, Config, and CloudTrail** for continuous security auditing.
- Build custom **CloudWatch dashboards** for observability; integrate with Grafana.
- Apply tighter IAM scoping and enforce encryption at rest/in transit across all services.

---

## Authors

This project was completed as a **group academic submission** at the University of Maryland, Baltimore County (UMBC), Fall 2025.

Team contributors (alphabetical):

- *Add team member names here*

---

## License

This project is for academic and educational purposes. AWS service usage is subject to AWS pricing and terms — please clean up resources (`terraform destroy`, delete CloudFormation stack, empty/remove S3 buckets) after testing to avoid charges.

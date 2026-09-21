# NexCell DevOps Assessment

## About You

**Name / Time spent (minutes):**  
Nathaniel Appiah / 200 minutes

**AI tools used, and one thing you changed or corrected from their output:**  
ChatGPT was used to support implementation and review. I corrected a smoke-test issue where the worker check was polling for a Redis job that had not been enqueued, then restored the enqueue step and reran CI successfully.

## Build and Run

**What I delivered, and how to run and verify it (commands):**  
Delivered a production Dockerfile, Docker Compose stack, FastAPI liveness/readiness endpoints, Redis worker, safe migration step, smoke test, and GitHub Actions CI. Run with `docker compose up -d --build`, then verify with `bash smoke_test.sh`.

**Top 3 problems fixed in the starting Dockerfile, and why each matters:**  
1. Replaced `python:latest` with a pinned slim base image to reduce drift and image size.  
2. Removed the hard-coded API secret and run the container as a non-root user to improve security.  
3. Removed `--reload`, improved dependency-layer caching, and added a healthcheck for safer production behaviour.

**How dependencies are kept reproducible, and how migrations run safely on deploy:**  
Python dependencies are pinned to exact versions in `requirements.txt`. Migrations run as a one-off Compose service after Postgres is healthy and must complete successfully before the API starts.

## AWS Design

**Target architecture in 3 to 5 lines:**    
Run the FastAPI API, workers and web frontend on ECS Fargate in `eu-west-2`, with the ALB in front of the API and CloudFront in front of the web app. Keep Redis on ElastiCache, PostgreSQL external as stated in the brief, and the vector database on EC2 initially; scale staging down outside working hours.

**Networking and security: VPC and subnets, IAM, secrets, how CI authenticates to AWS:**  
Use public subnets for the ALB and private subnets across two AZs for ECS tasks, Redis and internal EC2 workloads. Use least-privilege IAM, Secrets Manager, restrictive security groups, and GitHub Actions OIDC for short-lived AWS credentials.

**Deploying without downtime, and how you would roll back:**  
Use ECS rolling deployments with health checks so new tasks must become healthy before old tasks are removed. Tag images with the commit SHA; if health checks or monitoring fail, redeploy the previous known good image/task definition.

**Monitoring: the three alarms you would add first, with thresholds:**  
1. API 5xx error rate above 5% for 5 minutes.  
2. ALB/API p95 latency above 2 seconds for 5 minutes.  
3. Redis/job queue backlog above 100 waiting jobs for 5 minutes.

## Cost

**Top 3 savings: change, estimated £/month, and the risk each introduces:**  
1. Schedule/scale down staging outside working hours: reduce ~£260 to ~£90, saving ~£170/month. Risk: slower access for urgent out-of-hours testing.  
2. Right-size to a baseline of 2 API tasks at 0.5 vCPU/1 GB and 1 worker at 0.5 vCPU/1 GB, with autoscaling for peak load. Using the current bill proportionally, estimated API/worker cost falls from ~£400 to ~£76/month, saving ~£324/month.          Risk:under-sizing could increase latency or queue backlog.  
3. Change CloudWatch logging from DEBUG to INFO and apply retention: reduce ~£95 to ~£25/month, saving ~£70/month. Risk: less verbose logs may make deep debugging harder.

**New projected AWS total and cost per customer (show the sum):**  
£1,415 - £170 - £324 - £70 = ~£851/month. At 20 customers, ~£42.55 per customer/month, below the £45 target.

**One cost you would deliberately not cut, and how you would catch a cost spike early:**  
I would keep production redundancy across multiple AZs and the ALB because reliability during business hours is more important than removing that baseline cost. I would use AWS Budgets/Cost Anomaly Detection to alert on unexpected spend increases before they become a full-month surprise.

## Judgement

**How this scales to 100 customers:**  
Scale the API horizontally behind the ALB and scale workers on queue depth. Reassess Redis and vector database sizing from real utilisation as customer volume grows.

**The biggest production risk in the current setup, and your first fix:**  
The biggest immediate risk is unsafe delivery: long-lived AWS credentials, manual migrations and weak monitoring. My first fix is OIDC, automated migration ordering, health checks and CI smoke tests.

**One thing kept intentionally simple, and what you would do with 3 more hours:**  
I kept the application stub and migration minimal because the assessment focuses on DevOps rather than business logic. With 3 more hours I would add an architecture diagram, improve observability and test Redis/Postgres failure scenarios.

# Python Todo App

A full-stack Todo application built with a Python backend and an HTML/CSS frontend, containerized with Docker, and deployed to Kubernetes via a Jenkins CI/CD pipeline.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Running with Docker Compose](#running-with-docker-compose)
  - [Running with the Start Script](#running-with-the-start-script)
- [CI/CD Pipeline](#cicd-pipeline)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Security Scanning](#security-scanning)
- [Environment Variables](#environment-variables)

---

## Overview

This project is a containerized Todo application with a clear separation between the frontend and backend. It is designed with DevOps practices in mind, featuring Docker-based local development, a Jenkins pipeline for automated builds and deployments, and Kubernetes manifests for production-grade orchestration. Secrets are managed securely via AWS Secrets Manager and synced into the cluster using External Secrets Operator.

---

## Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Frontend    | HTML, CSS, JavaScript (Nginx)       |
| Backend     | Python (Flask)                      |
| Database    | MySQL 8.0                           |
| Container   | Docker, Docker Compose              |
| Orchestration | Kubernetes                        |
| CI/CD       | Jenkins                             |
| Registry    | Docker Hub                          |
| Secrets     | AWS Secrets Manager, External Secrets Operator |
| Security    | Trivy (image vulnerability scanning) |

---

## Project Structure

```
python_todo_app/
├── backend/              # Python Flask API + Dockerfile + schema.sql
├── frontend/             # Static HTML/CSS/JS + Nginx Dockerfile
├── k8s/                  # Kubernetes manifests (deployments, services, secrets)
├── docker-compose.yml    # Local multi-service setup with Trivy scanning
├── Jenkinsfile           # Declarative Jenkins CI/CD pipeline
└── start.sh              # Helper script to bootstrap local environment
```

---

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [AWS CLI](https://aws.amazon.com/cli/) configured with appropriate permissions (for `start.sh`)
- `jq` installed on your system

### Running with Docker Compose

If you already have the `MYSQL_ROOT_PASSWORD` environment variable set, you can bring the stack up directly:

```bash
export MYSQL_ROOT_PASSWORD=your_password_here
docker compose build
docker compose up -d
```

The services will be available at:
- **Frontend**: `http://localhost:8080`
- **Backend API**: `http://localhost:5000`

### Running with the Start Script

If your database password is stored in AWS Secrets Manager under the secret ID `db_credentials`, use the provided helper script. It fetches the password automatically, sets the environment variable, and starts all services including Trivy scans.

```bash
chmod +x start.sh
./start.sh
```

---

## CI/CD Pipeline

The `Jenkinsfile` defines a fully automated pipeline with the following stages:

1. **Build Docker Image** — Builds frontend and backend images tagged with the Jenkins build number.
2. **Scan Docker Image** — Runs Trivy vulnerability scans on both images and saves reports as artifacts.
3. **Login to DockerHub** — Authenticates using Jenkins-stored credentials.
4. **Tag Docker Image** — Tags both images with `:latest` in addition to the build number tag.
5. **Push Docker Image** — Pushes all tags to Docker Hub.
6. **Docker Cleanup** — Logs out and removes local images to free disk space.
7. **Deploy to Kubernetes** — Applies Kubernetes manifests, waits for External Secrets to sync from AWS, then rolls out updated deployments.
8. **Verify Deployment** — Waits for rollout completion on both deployments.

Trivy scan reports (`trivy-*.txt`) are archived as build artifacts on every run.

---

## Kubernetes Deployment

The `k8s/` directory contains all manifests required to run the application in a Kubernetes cluster. Secrets are not stored in the repository. Instead, the pipeline uses **External Secrets Operator** to sync credentials from AWS Secrets Manager into the cluster at deploy time:

```bash
kubectl apply -f k8s/secret-store.yaml
kubectl apply -f k8s/external-secret.yaml
kubectl wait externalsecret db-credentials --for=condition=Ready --timeout=60s
kubectl apply -f k8s/
```

Deployments are updated with the latest image tag on every successful pipeline run:

```bash
kubectl set image deployment/backend-deployment backend-deployment=<image>:<tag>
kubectl set image deployment/frontend-deployment frontend-deployment=<image>:<tag>
```

---

## Security Scanning

Trivy scans are integrated at two points:

- **Locally** via Docker Compose — `trivy_frontend` and `trivy_backend` services scan the built images and write reports to a shared volume.
- **In the Jenkins pipeline** — Trivy runs against both images before they are pushed to Docker Hub, with results archived as build artifacts.

---

## Environment Variables

| Variable             | Description                                      | Required    |
|----------------------|--------------------------------------------------|-------------|
| `MYSQL_ROOT_PASSWORD`| Root password for the MySQL database             | Yes         |
| `DB_HOST`            | Hostname of the database (defaults to `db`)      | Set by Compose |

In production (Kubernetes), secrets are injected via External Secrets Operator from AWS Secrets Manager and do not need to be set manually.

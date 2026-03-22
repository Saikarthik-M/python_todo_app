# Practical Experience Summary — python_todo_app

This document outlines the tools and technologies I have hands-on experience with through building and deploying a Python Todo application end-to-end on a Kubernetes cluster.

---

## Tools & Technologies Used

**Docker**
Containerized the frontend (Nginx) and backend (Python/Flask) services using Docker. Wrote multi-service docker-compose configurations covering health checks, named volumes, bridge networking, and dedicated Trivy scanner services for local image scanning.

**Docker Compose**
Defined a full multi-service local environment with frontend, backend, MySQL 8 database, and Trivy scanner containers. Implemented proper startup ordering using `depends_on` with `condition: service_healthy` to avoid race conditions.

**Trivy**
Integrated Trivy image scanning at two levels — inside docker-compose as dedicated scanner services, and inside the Jenkins pipeline as a separate stage. Scan reports are saved as build artifacts for review.

**Jenkins**
Built a declarative CI/CD pipeline (Jenkinsfile) with seven stages: Docker image build, Trivy security scan, DockerHub login, image tagging, push, Kubernetes deployment, and rollout verification. Used `withCredentials` for secure secret injection and `cleanWs()` for workspace cleanup.

**Kubernetes**
Deployed the application onto a Kubernetes cluster using manifests for Deployments and Services. Used `kubectl set image` for rolling updates and `kubectl rollout status` to verify successful deployments within the pipeline.

**External Secrets Operator (ESO)**
Configured `SecretStore` and `ExternalSecret` Kubernetes manifests to pull database credentials from AWS Secrets Manager into the cluster at deploy time.

**AWS Secrets Manager**
Stored database credentials in AWS Secrets Manager as the single source of truth.

**Shell Scripting (Bash)**
Wrote a `start.sh` script to automate local startup — fetching secrets from AWS, exporting them as environment variables, building images, and running docker-compose with Trivy scan containers.

**Python / Flask + MySQL**
Built the backend REST API with Python and Flask, connected to a MySQL 8 database. Managed schema initialization via an SQL file mounted into the MySQL container on first run.

---

> All of the above was done practically as part of building and deploying the `python_todo_app` project end-to-end.

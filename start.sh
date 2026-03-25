#!/bin/bash

# Step 1: fetch secret and parse using jq
aws_res=$(aws secretsmanager get-secret-value --secret-id db_credentials)
password=$(echo "$aws_res" | jq -r '.SecretString | fromjson | .root')
# Step 2: export as environment variable
export MYSQL_ROOT_PASSWORD=$password

# Step 3: docker-compose up
docker compose build
docker compose up -d
docker compose up -d --force-recreate trivy_frontend trivy_backend 

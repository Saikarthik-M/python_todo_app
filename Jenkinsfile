pipeline {
    agent any

    environment {
        DOCKER_USERNAME = "saikarthik28"
        BACKEND_IMAGE   = "python-todo-backend"
        FRONTEND_IMAGE  = "python-todo-frontend"
        IMAGE_TAG       = "${BUILD_NUMBER}"
        NAMESPACE       = "default"
        KUBECONFIG      = "/var/lib/jenkins/.kube/config"
    }

    stages {

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $DOCKER_USERNAME/$FRONTEND_IMAGE:$IMAGE_TAG ./frontend'
                sh 'docker build -t $DOCKER_USERNAME/$BACKEND_IMAGE:$IMAGE_TAG ./backend'
            }
        }

        stage('Scan Docker Image') {
            steps {
                sh 'trivy image --exit-code 0 --format table --output trivy-frontend.txt $DOCKER_USERNAME/$FRONTEND_IMAGE:$IMAGE_TAG'
                sh 'trivy image --exit-code 0 --format table --output trivy-backend.txt $DOCKER_USERNAME/$BACKEND_IMAGE:$IMAGE_TAG'
            }
        }

        stage('Login to DockerHub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                }
            }
        }

        stage('Tag Docker Image') {
            steps {
                sh 'docker tag $DOCKER_USERNAME/$FRONTEND_IMAGE:$IMAGE_TAG $DOCKER_USERNAME/$FRONTEND_IMAGE:latest'
                sh 'docker tag $DOCKER_USERNAME/$BACKEND_IMAGE:$IMAGE_TAG $DOCKER_USERNAME/$BACKEND_IMAGE:latest'
            }
        }

        stage('Push Docker Image') {
            steps {
                sh """
                    docker push $DOCKER_USERNAME/$FRONTEND_IMAGE:$IMAGE_TAG
                    docker push $DOCKER_USERNAME/$BACKEND_IMAGE:$IMAGE_TAG
                    docker push $DOCKER_USERNAME/$FRONTEND_IMAGE:latest
                    docker push $DOCKER_USERNAME/$BACKEND_IMAGE:latest
                """
            }
        }

        stage('Docker Cleanup') {
            steps {
                sh """
                    # Logout after push
                    docker logout

                    # Remove images to free disk space
                    docker rmi $DOCKER_USERNAME/$FRONTEND_IMAGE:$IMAGE_TAG || true
                    docker rmi $DOCKER_USERNAME/$BACKEND_IMAGE:$IMAGE_TAG || true
                    docker rmi $DOCKER_USERNAME/$FRONTEND_IMAGE:latest || true
                    docker rmi $DOCKER_USERNAME/$BACKEND_IMAGE:latest || true

                    # Clean dangling images
                    docker image prune -f
                """
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh """
                    # Apply manifests — creates if not exists, updates if exists
                    kubectl apply -f k8s/ -n ${NAMESPACE}

                    # Update images to new build
                    kubectl set image deployment/backend-deployment \
                      backend-deployment=$DOCKER_USERNAME/$BACKEND_IMAGE:$IMAGE_TAG \
                      -n ${NAMESPACE}

                    kubectl set image deployment/frontend-deployment \
                      frontend-deployment=$DOCKER_USERNAME/$FRONTEND_IMAGE:$IMAGE_TAG \
                      -n ${NAMESPACE}
                """
            }
        }

        stage('Verify Deployment') {
            steps {
                sh """
                    kubectl rollout status deployment/backend-deployment \
                      -n ${NAMESPACE} --timeout=120s

                    kubectl rollout status deployment/frontend-deployment \
                      -n ${NAMESPACE} --timeout=120s
                """
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'trivy-*.txt', allowEmptyArchive: true
            cleanWs()    // ← clean workspace every run
        }
        success {
            echo "Build succeeded"
        }
        failure {
            echo "Build failed"
        }
    }
}
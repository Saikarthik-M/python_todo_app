pipeline {
    agent any
    environment {
        DOCKER_USERNAME = "saikarthik28"
        BACKEND_IMAGE = "python-todo-backend"
        FRONTEND_IMAGE = "python-todo-frontend"
        IMAGE_TAG = "${BUILD_NUMBER}"
    }
    stages {
        stage('Build Docker image'){
            steps {
                sh 'docker build -t $DOCKER_USERNAME/$FRONTEND_IMAGE:$IMAGE_TAG ./frontend'
                sh 'docker build -t $DOCKER_USERNAME/$BACKEND_IMAGE:$IMAGE_TAG ./backend'
            }
        }
        stage('Check Docker image'){
            steps {
                sh 'trivy image --exit-code 0 --format table --output trivy-frontend.txt $DOCKER_USERNAME/$FRONTEND_IMAGE:$IMAGE_TAG'
                sh 'trivy image --exit-code 0 --format table --output trivy-backend.txt $DOCKER_USERNAME/$BACKEND_IMAGE:$IMAGE_TAG'
            }
        }
        stage('Login Docker'){
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]){
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                }
            }
        }
        stage('Docker Image Tag'){
            steps{
                sh 'docker tag $DOCKER_USERNAME/$FRONTEND_IMAGE:$IMAGE_TAG $DOCKER_USERNAME/$FRONTEND_IMAGE:latest'
                sh 'docker tag $DOCKER_USERNAME/$BACKEND_IMAGE:$IMAGE_TAG $DOCKER_USERNAME/$BACKEND_IMAGE:latest'
            }
        }
        stage('Push Docker image'){
            steps {
                sh 'docker push $DOCKER_USERNAME/$FRONTEND_IMAGE:$IMAGE_TAG'
                sh 'docker push $DOCKER_USERNAME/$BACKEND_IMAGE:$IMAGE_TAG'
                sh 'docker push $DOCKER_USERNAME/$FRONTEND_IMAGE:latest'
                sh 'docker push $DOCKER_USERNAME/$BACKEND_IMAGE:latest'
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                sh """
                kubectl set image deployment/backend-deployment \
                backend-deployment=$DOCKER_USERNAME/$BACKEND_IMAGE:$IMAGE_TAG

                kubectl set image deployment/frontend-deployment \
                frontend=$DOCKER_USERNAME/$FRONTEND_IMAGE:$IMAGE_TAG
                """
            }
        }
        stage('Verify Deployment') {
            steps {
                sh """
                kubectl rollout status deployment/backend-deployment
                kubectl rollout status deployment/frontend-deployment
                """
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'trivy-*.txt', allowEmptyArchive: true
        }
        success {
            echo "Build succeeded"
        }
        failure {
            echo "Build failed"
        }
    }
}
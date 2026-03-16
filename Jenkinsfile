pipeline {
    agent any
    stages {
        stage('Build Docker image'){
            steps {
                sh 'docker build -t saikarthik28/python-todo-frontend:${BUILD_NUMBER} ./frontend'
                sh 'docker build -t saikarthik28/python-todo-backend:${BUILD_NUMBER} ./backend'
            }
        }
        stage('Check Docker image'){
            steps {
                sh 'trivy image --exit-code 0 --format table --output trivy-frontend.txt saikarthik28/python-todo-frontend:${BUILD_NUMBER}'
                sh 'trivy image --exit-code 0 --format table --output trivy-backend.txt saikarthik28/python-todo-backend:${BUILD_NUMBER}'
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
                sh 'docker tag saikarthik28/python-todo-frontend:${BUILD_NUMBER} saikarthik28/python-todo-frontend:latest'
                sh 'docker tag saikarthik28/python-todo-backend:${BUILD_NUMBER} saikarthik28/python-todo-backend:latest'
            }
        }
        stage('Push Docker image'){
            steps {
                sh 'docker push saikarthik28/python-todo-frontend:${BUILD_NUMBER}'
                sh 'docker push saikarthik28/python-todo-backend:${BUILD_NUMBER}'
                sh 'docker push saikarthik28/python-todo-frontend:latest'
                sh 'docker push saikarthik28/python-todo-backend:latest'
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
pipeline {
    agent any

    environment {
        APP_NAME = 'todo-app'
        PORT = '5000'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                sh 'python -m pip install --upgrade pip'
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                echo 'Running automated test suite with pytest...'
                sh 'pytest -v'
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker container image...'
                sh "docker build -t ${APP_NAME}:latest ."
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying application container...'
                sh "docker rm -f ${APP_NAME} || true"
                sh "docker run -d -p ${PORT}:${PORT} --name ${APP_NAME} ${APP_NAME}:latest"
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully! Application is live.'
        }
        failure {
            echo 'Pipeline failed. Check previous stages for errors.'
        }
    }
}

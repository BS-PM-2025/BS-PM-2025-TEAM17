pipeline {
    agent any
    
    environment {
        VENV_DIR = 'venv'
    }
    
    stages {
        stage('Setup Python Env') {
            steps {
                sh '''
                    python3 -m venv $VENV_DIR
                    source $VENV_DIR/bin/activate
                    pip install --upgrade pip
                    pip install django
                    pip install coverage
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running tests...'
                sh 'python manage.py test'
            }
        }
    }
    
    post {
        always {
            echo "Build finished"
        }
        success {
            echo "Tests completed successfully"
        }
        failure {
            echo "Tests failed"
        }
    }
}
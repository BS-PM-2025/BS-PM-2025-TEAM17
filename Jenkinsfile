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
                sh '''
                    source $VENV_DIR/bin/activate
                    python manage.py test
                '''
            }
        }
    }
}
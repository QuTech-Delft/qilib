pipeline {
    agent {
        docker {
              image 'python:3.6'
              args  '-v pip_cache:/var/pip_cache'
        }
    }
    stages {
        stage('Test') {
            steps {
                sh 'pwd'
                sh 'ls -lah'
                sh 'python -m venv env'
                sh '''
                        . ./env/bin/activate &&
                        pip install --cache-dir /var/pip_cache . &&
                        coverage run --source="." --omit="*/test_*","env/*","setup.py" -m unittest discover -s src &&
                        coverage report &&
                        coverage report -m &&
                        coverage xml
                    '''
            }
        }
        stage('Collect') {
            steps {
                step([$class: 'CoberturaPublisher', coberturaReportFile: 'coverage.xml'])
            }
        }
    }
}
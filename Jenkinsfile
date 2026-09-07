pipeline { 
    agent any 

    stages { 
        stage('Git Checkout ') { 
            steps { 
                git branch: 'main', url: 'https://github.com/VigneshSelvam92/DevOps-Project-1.git'
            } 
        } 

        stage('Install Dependencies') { 
            steps { 
                echo 'Installing dependencies...'   
                sh '''
                    python3 -m venv venv
                    ./venv/bin/python3 -m pip install --upgrade pip
                    ./venv/bin/python3 -m pip install -r app/requirements.txt
                '''
            } 
        }

        stage('Run Tests') { 
            steps { 
                echo 'Running tests...'   
                sh './venv/bin/python3 -m pytest app/test/test_app.py --cov=app --cov-report=xml:coverage.xml --junitxml=results.xml'
            } 
        }
       
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('sonarqube') {
                    script {
                        def scannerHome = tool 'SonarQubeScanner'
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Docker Build and Push') {
            steps {
                script {
                    def imageName = "mydockervicky992/devops-project-1"
                    def timestamp = sh(script: 'date +%Y%m%d_%H%M%S', returnStdout: true).trim()
                    def imageTag = "build-${env.BUILD_NUMBER}-${timestamp}"
                    sh "docker build -t ${imageName}:${imageTag} app/"
                    withCredentials([usernamePassword(credentialsId: 'Docker-id', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        sh "echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin"
                        sh "docker push ${imageName}:${imageTag}"
                    }
                }
            }
        }
    } 
}
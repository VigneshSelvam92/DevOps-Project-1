pipeline {
    agent any

    environment {
        AWS_REGION = 'eu-west-1'
        UAT_INSTANCE_TYPE = 't2.small'
        IMAGE_NAME = 'mydockervicky992/devops-project-1'
        APP_PORT = '5000'
    }

    stages {
        stage('Git Checkout') {
            steps {
                checkout scm
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

        stage('Run Unit Tests') {
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
                    def timestamp = sh(script: 'date +%Y%m%d_%H%M%S', returnStdout: true).trim()
                    def imageTag = "build-${env.BUILD_NUMBER}-${timestamp}"
                    env.IMAGE_TAG = imageTag

                    sh "docker build -t ${IMAGE_NAME}:${env.IMAGE_TAG} app/"
                    withCredentials([usernamePassword(credentialsId: 'Docker-id', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        sh "echo \"$DOCKER_PASSWORD\" | docker login -u \"$DOCKER_USERNAME\" --password-stdin"
                        sh "docker push ${IMAGE_NAME}:${env.IMAGE_TAG}"
                    }
                }
            }
        }

        stage('Create UAT EC2 Instance') {
            when {
                expression {
                    def branchName = env.BRANCH_NAME ?: ''
                    return branchName.startsWith('PR-') || branchName.startsWith('feature/') || branchName.startsWith('hotfix/')
                }
            }
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'aws-uat-deploy-role-arn', variable: 'UAT_DEPLOY_ROLE_ARN'),                       
                        string(credentialsId: 'aws-uat-key-name', variable: 'UAT_KEY_NAME'),
                        string(credentialsId: 'aws-uat-security-group-id', variable: 'UAT_SECURITY_GROUP_ID'),
                        string(credentialsId: 'aws-uat-subnet-id', variable: 'UAT_SUBNET_ID'),
                        string(credentialsId: 'aws-uat-ami-id', variable: 'UAT_AMI_ID')
                    ]) {
                        sh '''
                            set -e

                            export AWS_DEFAULT_REGION="${AWS_REGION}"

                            CREDS=$(aws sts assume-role \
                                --role-arn "${UAT_DEPLOY_ROLE_ARN}" \
                                --role-session-name "jenkins-uat-${BUILD_NUMBER}" \
                                --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
                                --output text)

                            export AWS_ACCESS_KEY_ID="$(echo "$CREDS" | awk '{print $1}')"
                            export AWS_SECRET_ACCESS_KEY="$(echo "$CREDS" | awk '{print $2}')"
                            export AWS_SESSION_TOKEN="$(echo "$CREDS" | awk '{print $3}')"

                            INSTANCE_ID=$(aws ec2 run-instances \
                                --image-id "${UAT_AMI_ID}" \
                                --count 1 \
                                --instance-type "${UAT_INSTANCE_TYPE}" \
                                --key-name "${UAT_KEY_NAME}" \
                                --security-group-ids "${UAT_SECURITY_GROUP_ID}" \
                                --subnet-id "${UAT_SUBNET_ID}" \
                                --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=uat-${JOB_NAME}-${BUILD_NUMBER}},{Key=Environment,Value=UAT}]' \
                                --query 'Instances[0].InstanceId' \
                                --output text)

                            echo "$INSTANCE_ID" > instance_id.txt
                            aws ec2 wait instance-status-ok --instance-ids "$INSTANCE_ID"
                            aws ec2 describe-instances \
                                --instance-ids "$INSTANCE_ID" \
                                --query 'Reservations[0].Instances[0].PublicIpAddress' \
                                --output text > public_ip.txt
                        '''
                    }

                    env.UAT_INSTANCE_ID = readFile('instance_id.txt').trim()
                    env.UAT_PUBLIC_IP = readFile('public_ip.txt').trim()
                    echo "UAT EC2 instance created: ${env.UAT_INSTANCE_ID} (${env.UAT_PUBLIC_IP})"
                }
            }
        }

        stage('Deploy to UAT EC2') {
            when {
                expression {
                    def branchName = env.BRANCH_NAME ?: ''
                    return branchName.startsWith('PR-') || branchName.startsWith('feature/') || branchName.startsWith('hotfix/')
                }
            }
            steps {
                script {
                    withCredentials([
                        sshUserPrivateKey(credentialsId: 'uat-ec2-ssh-key', keyFileVariable: 'UAT_SSH_KEY', usernameVariable: 'UAT_SSH_USER')
                    ]) {
                        sh '''
                            set -e
                            ssh -i "${UAT_SSH_KEY}" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "${UAT_SSH_USER}@${UAT_PUBLIC_IP}" <<EOF
                                sudo yum update -y
                                sudo yum install -y docker
                                sudo systemctl enable docker
                                sudo systemctl start docker
                                sudo usermod -aG docker "${UAT_SSH_USER}"
                                docker pull ${IMAGE_NAME}:${IMAGE_TAG}
                                docker stop myapp || true
                                docker rm myapp || true
                                docker run -d --name myapp -p 80:${APP_PORT} -e APP_VERSION="${BUILD_NUMBER}" ${IMAGE_NAME}:${IMAGE_TAG}
                            EOF
                        '''
                    }
                }
            }
        }

        stage('Functional Testing on UAT') {
            when {
                expression {
                    def branchName = env.BRANCH_NAME ?: ''
                    return branchName.startsWith('PR-') || branchName.startsWith('feature/') || branchName.startsWith('hotfix/')
                }
            }
            steps {
                script {
                    sh '''
                        set -e
                        curl -fsS "http://${UAT_PUBLIC_IP}/healthz"
                        curl -fsS "http://${UAT_PUBLIC_IP}/" | grep -q "Hello from"
                    '''
                }
            }
        }
    }

    
}
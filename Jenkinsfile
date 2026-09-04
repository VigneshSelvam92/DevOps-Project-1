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
                sh './venv/bin/python3 -m pytest app/tests/test_app.py --junitxml=results.xml'
            } 
        }
       
    } 
}
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
                sh 'sudo apt install -y python3 python3-pip python3-venv build-essential'
                sh 'python3 -m pip install -r requirements.txt'
            } 
        } 
       
    } 
}
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
                sh 'pip install --upgrade pip'
                sh 'pip install -r requirements.txt'
            } 
        } 
       
    } 
}
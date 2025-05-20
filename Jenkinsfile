pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh 'docker build -t backendapi .'
      }
    }
    stage('Test') {
      steps {
        sh 'echo Running tests...'
      }
    }
    stage('Deploy') {
      when { branch 'main' }
      steps {
        sh 'echo Deploying backend...'
      }
    }
  }
}

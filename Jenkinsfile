// pipeline {
//   agent any
//   stages {
//     stage('Build') {
//       steps {
//         sh 'docker build -t backendapi .'
//       }
//     }
//     stage('Test') {
//       steps {
//         sh 'echo Running tests...'
//       }
//     }
//     stage('Deploy') {
//       when { branch 'main' }
//       steps {
//         sh 'echo Deploying backend...'
//       }
//     }
//   }
// }

pipeline {
  agent any
  stages {
    stage('Lint') {
      steps {
        sh 'docker run --rm -v $(pwd):/app python:3.9-slim bash -c "pip install flake8 && flake8 /app --max-line-length=120"'
      }
    }
    stage('Build') {
      steps {
        sh 'docker build -t backendapi .'
      }
    }
    stage('Test') {
      steps {
        sh 'docker run --rm backendapi pytest --tb=short'
      }
    }
    stage('Deploy') {
      when { branch 'main' }
      steps {
        sh '''
          docker tag backendapi myregistry.com/backendapi:latest
          docker push myregistry.com/backendapi:latest
          docker-compose -f /app/docker-compose.yml up -d app101apipy
        '''
      }
    }
  }
  post {
    always {
      sh 'docker system prune -f'
    }
    failure {
      echo 'Pipeline failed. Check logs.'
    }
  }
}
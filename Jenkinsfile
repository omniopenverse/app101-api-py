pipeline {
  environment {
    DOCKER_HOST = 'tcp://dind:2376'
    DOCKER_CERT_PATH = '/certs/client'
    DOCKER_TLS_VERIFY = '1'
  }
  agent {
    docker {
      // Docker CLI image (includes docker + compose plugin)
      image 'docker:24.0-cli'
      // Run as root to install tools; mount TLS certs and point to DinD
      args '-u root:root -v /certs:/certs:ro -e DOCKER_HOST=tcp://dind:2376 -e DOCKER_CERT_PATH=/certs/client -e DOCKER_TLS_VERIFY=1'
    }
  }
  stages {
    stage('Setup tools') {
      steps {
        sh '''
          set -eux
          apk add --no-cache python3 py3-pip make bash docker-cli-compose
          python3 -m ensurepip || true
          python3 -m pip install --upgrade pip
        '''
      }
    }
    stage('Build') {
      steps {
        sh 'make build'
      }
    }
    stage('Test') {
      steps {
        sh 'make test'
      }
    }
    stage('Coverage') {
      steps {
        sh 'make coverage-html'
      }
    }
    stage('Deploy') {
      when { branch 'main' }
      steps {
        sh 'echo Deploying backend...'
      }
    }
  }
  post {
    always {
      archiveArtifacts artifacts: 'htmlcov/**', allowEmptyArchive: true
      sh 'make clean || true'
    }
  }
}

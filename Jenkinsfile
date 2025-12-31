pipeline {
  agent any

  options {
    timestamps()
    ansiColor('xterm')
    disableConcurrentBuilds()
    timeout(time: 30, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '30', artifactNumToKeepStr: '30'))
    preserveStashes(buildCount: 10)
  }

  parameters {
    string(name: 'DOCKERHUB_NAMESPACE', defaultValue: 'omniopenverse', description: 'Docker Hub namespace/org')
    string(name: 'IMAGE_NAME', defaultValue: 'app101apipy', description: 'Docker image name (repo)')
  }

  environment {
    IMAGE_REPO = "${params.DOCKERHUB_NAMESPACE}/${params.IMAGE_NAME}"
  }

  stages {
    stage('Checkout') {
      agent any
      steps {
        checkout scm
        script {
          env.GIT_SHA_SHORT = sh(script: "git rev-parse --short=12 HEAD", returnStdout: true).trim()
          env.GIT_BRANCH_SAFE = (env.BRANCH_NAME ?: "detached").replaceAll(/[^A-Za-z0-9._-]/, '-')
          env.GIT_TAG = sh(script: "git describe --tags --exact-match 2>/dev/null || true", returnStdout: true).trim()
          env.IMAGE_REPO = "${params.DOCKERHUB_NAMESPACE}/${params.IMAGE_NAME}"
        }
      }
    }

    stage('Install') {
      agent {
        docker {
          image 'app101/jenkins-python-agent:latest'
          args '--user 1000:1000 -v /workspace:/home/ciuser/workspace --workdir /home/ciuser/workspace'
          reuseNode true
        }
      }
      steps {
        sh '''
          set -euo pipefail
          make pre-install
          make install
        '''
      }
    }

    stage('Test') {
      agent {
        docker {
          image 'app101/jenkins-python-agent:latest'
          args '--user 1000:1000 -v /workspace:/home/ciuser/workspace --workdir /home/ciuser/workspace'
          reuseNode true
        }
      }
      steps {
        // workspace already populated by previous stage; rerun checkout if using different nodes
        sh '''
          set -euo pipefail
          make test
        '''
      }
    }

    stage('Coverage') {
      agent {
        docker {
          image 'app101/jenkins-python-agent:latest'
          args '--user 1000:1000 -v /workspace:/home/ciuser/workspace --workdir /home/ciuser/workspace'
          reuseNode true
        }
      }
      steps {
        sh '''
          set -euo pipefail
          make coverage
          make coverage-html
        '''
      }
      post {
        always {
          // If pytest produced JUnit XML you can publish it here. (Optional)
          // junit allowEmptyResults: true, testResults: '**/junit*.xml'
          sh 'ls -la || true'
        }
      }
    }

    // stage('Lint') {
    //   agent {
    //     docker {
    //       image 'app101/jenkins-python-agent:latest'
    //       args '--user 1000:1000 -v /workspace:/home/ciuser/workspace --workdir /home/ciuser/workspace'
    //       reuseNode true
    //     }
    //   }
    //   steps {
    //     sh '''
    //       set -euo pipefail
    //       make lint
    //     '''
    //   }
    // }

    stage('Audit') {
      agent {
        docker {
          image 'app101/jenkins-python-agent:latest'
          args '--user 1000:1000 -v /workspace:/home/ciuser/workspace --workdir /home/ciuser/workspace'
          reuseNode true
        }
      }
      steps {
        // workspace already populated by previous stage; rerun checkout if using different nodes
        sh '''
          set -euo pipefail
          make pip-audit
        '''
      }
    }

    stage('Safety') {
      agent {
        docker {
          image 'app101/jenkins-python-agent:latest'
          args '--user 1000:1000 -v /workspace:/home/ciuser/workspace --workdir /home/ciuser/workspace'
          reuseNode true
        }
      }
      steps {
        // workspace already populated by previous stage; rerun checkout if using different nodes
        sh '''
          set -euo pipefail
          make safety
        '''
      }
    }

    stage('Bandit') {
      agent {
        docker {
          image 'app101/jenkins-python-agent:latest'
          args '--user 1000:1000 -v /workspace:/home/ciuser/workspace --workdir /home/ciuser/workspace'
          reuseNode true
        }
      }
      steps {
        // workspace already populated by previous stage; rerun checkout if using different nodes
        sh '''
          set -euo pipefail
          make bandit
        '''
      }
    }

    stage('Package') {
      agent {
        docker {
          image 'app101/jenkins-python-agent:latest'
          args '--user 1000:1000 -v /workspace:/home/ciuser/workspace --workdir /home/ciuser/workspace'
          reuseNode true
        }
      }
      steps {
        // workspace already populated by previous stage; rerun checkout if using different nodes
        sh '''
          set -euo pipefail
          make package
        '''
      }
    }

    // ...

    // stage('Stash Sources') {
    //   agent any
    //   steps {
    //     // Stash source for later Docker build stage
    //     stash name: 'srcs', includes: '**/*', excludes: '**/.git/**', useDefaultExcludes: false
    //   }
    // }

    stage('Docker Build & Push') {
      agent any
      // when { anyOf { branch 'main'; branch 'arsene'; buildingTag() } }
      environment {
        HOME = "${WORKSPACE}"
      }
      steps {
        // unstash 'srcs'
        // unstash 'dist'

        script {
          def tags = []
          tags << "sha-${env.GIT_SHA_SHORT}"

          if ((env.BRANCH_NAME ?: '') == 'main') {
            tags << "latest"
          }
          if (env.GIT_TAG?.trim()) {
            tags << env.GIT_TAG.trim()
          }

          env.IMAGE_TAGS = tags.join(',')
          echo "Will push tags: ${env.IMAGE_TAGS}"
        }

        withCredentials([
          usernamePassword(
            credentialsId: 'dockerhub-creds',
            usernameVariable: 'DH_USER',
            passwordVariable: 'DH_PASS'
          )]) {
          sh '''
            bash -lc '
              set -euo pipefail

              echo "DOCKER_HOST=${DOCKER_HOST:-}"
              echo "DOCKER_CERT_PATH=${DOCKER_CERT_PATH:-}"
              docker info || true
              echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
              # Build once, tag many
              docker build \
                --pull \
                --label "org.opencontainers.image.revision=${GIT_SHA_SHORT}" \
                --label "org.opencontainers.image.source=${GIT_URL:-unknown}" \
                -t "${IMAGE_REPO}:sha-${GIT_SHA_SHORT}" \
                .
              IFS="," read -r -a TAG_ARR <<< "${IMAGE_TAGS}"
              for t in "${TAG_ARR[@]}"; do
                if [ "$t" != "sha-${GIT_SHA_SHORT}" ]; then
                  docker tag "${IMAGE_REPO}:sha-${GIT_SHA_SHORT}" "${IMAGE_REPO}:$t"
                fi
              done
              # Push
              for t in "${TAG_ARR[@]}"; do
                docker push "${IMAGE_REPO}:$t"
              done
              docker logout
            '
          '''
        }
      }
    }
  }

  post {
    success {
      echo "✅ Build succeeded. Image: ${env.IMAGE_REPO} Tags: ${env.IMAGE_TAGS}"
    }
    failure {
      echo "❌ Build failed."
    }
    always {
      cleanWs(deleteDirs: true, disableDeferredWipeout: true)
    }
  }
}

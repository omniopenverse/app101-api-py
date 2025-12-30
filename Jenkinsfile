pipeline {
  agent any

  options {
    timestamps()
    ansiColor('xterm')
    disableConcurrentBuilds()
    timeout(time: 30, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '30', artifactNumToKeepStr: '30'))
    // skipDefaultCheckout(true)
    preserveStashes(buildCount: 10)
  }

  parameters {
    string(name: 'DOCKERHUB_NAMESPACE', defaultValue: 'omniopenverse', description: 'Docker Hub namespace/org')
    string(name: 'IMAGE_NAME', defaultValue: 'app101apipy', description: 'Docker image name (repo)')
  }

  environment {
    // DinD daemon (your docker:dind service should be named "docker")
    // DOCKER_HOST = 'tcp://dind:2375'
    // DOCKER_TLS_CERTDIR = ''
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

        stash name: 'src_files', includes: '**/*', excludes: '**/.git/**', useDefaultExcludes: false
      }
    }

    stage('CI: lint/test/coverage/security') {
      agent {
        docker {
          image 'app101/jenkins-python-agent:latest'
          args '--user 1000:1000 -v /workspace:/home/ciuser/workspace --workdir /home/ciuser/workspace'
          reuseNode true
        }
      }
      unstash 'src_files'
      stages {
        stage('Install') {
          steps {
            sh '''
              set -euo pipefail
              make pre-install
              make install
            '''
          }
        }
        stage('test') {
          steps {
            sh '''
              set -euo pipefail
              make test
            '''
          }
        }
        // stage('lint') {
        //   steps {
        //     sh '''
        //       set -euo pipefail
        //       make lint
        //     '''
        //   }
        // }
        stage('coverage') {
          steps {
            sh '''
              set -euo pipefail
              make coverage
              make coverage-html
            '''
          }
        }
        // stage('Package & Stash') {
        //   steps {
        //     // Archive built python packages in Jenkins
        //     archiveArtifacts artifacts: 'dist/*', fingerprint: true, onlyIfSuccessful: true
        //     // // Stash dist artifacts for image build stage (optional, but useful)
        //     // stash name: 'dist', includes: 'dist/*', allowEmpty: true
        //     // Stash source for later containerized stages
        //     stash name: 'srcs', includes: '**/*', excludes: '**/.git/**', useDefaultExcludes: false
        //   }
        // }
      }
      post {
        always {
          // If pytest produced JUnit XML you can publish it here. (Optional)
          // junit allowEmptyResults: true, testResults: '**/junit*.xml'
          sh 'ls -la || true'
        }
      }
    }

    stage('Docker Build & Push') {
      // agent {
      //   docker {
      //     image 'app101/jenkins-agent:latest'
      //     // Provide Docker daemon connectivity to dind over TLS and ensure network reachability
      //     // Join the same Docker network as compose services so hostname "dind" resolves
      //     args '--user root:root --privileged -e DOCKER_HOST=tcp://dind:2376 -e DOCKER_TLS_VERIFY=1 -e DOCKER_CERT_PATH=/certs/client -v /certs:/certs:ro'
      //     reuseNode true
      //   }
      // }
      agent { label 'docker' }
      // when { anyOf { branch 'main'; branch 'arsene'; buildingTag() } }
      environment {
        // helps some environments that need HOME writable
        HOME = "${WORKSPACE}"
      }
      steps {
        unstash 'srcs'
        // unstash 'dist'

        script {
          // Tag strategy:
          // - Always: sha-<shortsha>
          // - main branch: latest
          // - git tag builds: <tag>
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

              hostname || true
              cat /etc/os-release || true
              id || true
              ls -la || true

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
    // always {
    //   cleanWs(deleteDirs: true, disableDeferredWipeout: true)
    // }
  }
}

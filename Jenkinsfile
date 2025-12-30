pipeline {
  agent any

  options {
    timestamps()
    ansiColor('xterm')
    disableConcurrentBuilds()
    timeout(time: 30, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '30', artifactNumToKeepStr: '30'))
    skipDefaultCheckout(true)
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

    // Python build behavior
    // PIP_DISABLE_PIP_VERSION_CHECK = '1'
    // PYTHONDONTWRITEBYTECODE = '1'
    // PYTHONUNBUFFERED = '1'
    IMAGE_REPO = "${params.DOCKERHUB_NAMESPACE}/${params.IMAGE_NAME}"
  }

  stages {
    stage('Checkout') {
      agent { label 'built-in' } // or any label that has workspace; change if needed
      steps {
        checkout scm
        script {
          // Metadata we will reuse
          env.GIT_SHA_SHORT = sh(script: "git rev-parse --short=12 HEAD", returnStdout: true).trim()
          env.GIT_BRANCH_SAFE = (env.BRANCH_NAME ?: "detached").replaceAll(/[^A-Za-z0-9._-]/, '-')

          // Tag name if this build is on an exact tag
          env.GIT_TAG = sh(script: "git describe --tags --exact-match 2>/dev/null || true", returnStdout: true).trim()

          // Image repo
          env.IMAGE_REPO = "${params.DOCKERHUB_NAMESPACE}/${params.IMAGE_NAME}"
        }

        // Stash source for later containerized stages
        stash name: 'src', includes: '**/*', useDefaultExcludes: false
      }
    }

    stage('CI: lint/test/coverage/security') {
      agent {
        docker {
          image 'python:3.12-slim'
          args '--user root:root' // needed to apt-get if required
          reuseNode true
        }
      }
      steps {
        unstash 'src'

        sh '''
          set -euo pipefail

          apt-get update -y
          apt-get install -y --no-install-recommends make git ca-certificates
          rm -rf /var/lib/apt/lists/*

          # Run your Makefile CI (creates .venv and runs lint/test/coverage + security checks)
          make ci

          # Build Python package artifacts (wheel + sdist)
          ./.venv/bin/python -m pip install --upgrade build
          ./.venv/bin/python -m build

          ls -la dist || true
        '''

        // Archive built python packages in Jenkins
        archiveArtifacts artifacts: 'dist/*', fingerprint: true, onlyIfSuccessful: true

        // Stash dist artifacts for image build stage (optional, but useful)
        stash name: 'dist', includes: 'dist/*', allowEmpty: true
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
      agent {
        docker {
          image 'docker:27.4-cli'
          args '--user root:root'
          reuseNode true
        }
      }
      environment {
        // helps some environments that need HOME writable
        HOME = "${WORKSPACE}"
      }
      steps {
        unstash 'src'
        unstash 'dist'

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
            set -euo pipefail

            echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin

            # Build once, tag many
            docker build \
              --pull \
              --label "org.opencontainers.image.revision=${GIT_SHA_SHORT}" \
              --label "org.opencontainers.image.source=${GIT_URL:-unknown}" \
              -t "${IMAGE_REPO}:sha-${GIT_SHA_SHORT}" \
              .

            IFS=',' read -r -a TAG_ARR <<< "${IMAGE_TAGS}"
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

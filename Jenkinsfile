node {
    def app

    stage('Clone Repository') {
        checkout scm
    }

    stage('SonarQube Scan') {
        def scannerHome = tool name: 'sonarq', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
        echo "SonarQube Scanner Path: ${scannerHome}"

        withSonarQubeEnv('sonarq') {
            withCredentials([string(credentialsId: 'sonarq', variable: 'SONARQUBE_TOKEN')]) {
                sh """
                    ${scannerHome}/bin/sonar-scanner \
                    -Dsonar.projectKey=my_project_key \
                    -Dsonar.sources=. \
                    -Dsonar.host.url=http://13.229.130.29:9000 \
                    -Dsonar.login=${SONARQUBE_TOKEN}
                """
            }
        }
    }

    stage('Quality Gate') {
        steps {
            script {
                // Waits for the quality gate result; fails if the gate fails.
                def qg = waitForQualityGate(credentialsId: 'sonarq')
                if (qg.status != 'OK') {
                    error "Quality gate failed: ${qg.status}"
                }
            }
        }
    }

    stage('Build Image') {
        app = docker.build("02042025/dockerhub:${env.BUILD_NUMBER}")
    }

    stage('Push Image') {
        docker.withRegistry('https://index.docker.io/v1/', 'dockerhub') {
            app.push("${env.BUILD_NUMBER}")
            app.push("latest")  // Also tag as 'latest' for easy retrieval
        }
    }

    stage('Trivy Scan') {
        echo "Running Trivy security scan for the Docker image"
        sh """
            docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v /root/.cache/trivy:/root/.cache/ \
            aquasec/trivy:latest image \
            --cache-dir /root/.cache/trivy \
            02042025/dockerhub:${env.BUILD_NUMBER}
        """
    }

    stage('Trigger Manifest Update') {
        echo "Triggering updatemanifest job"
        build job: 'updatemanifest', parameters: [string(name: 'DOCKERTAG', value: env.BUILD_NUMBER)]
    }
}

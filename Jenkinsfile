node {
    def app

    stage('Clone repository') {
        checkout scm
    }

    stage('SonarQube Scan') {
        // Ensure SonarQube Scanner is configured in Jenkins
        def scannerHome = tool name: 'sonarq', type: 'hudson.plugins.sonar.SonarRunnerInstallation'

        withSonarQubeEnv('sonarq') { // Use SonarQube environment configured in Jenkins
            withCredentials([string(credentialsId: 'sonarq', variable: 'SONARQUBE_TOKEN')]) {
                sh """
                    ${scannerHome}/bin/sonar-scanner \
                    -Dsonar.projectKey=my_project_key \
                    -Dsonar.sources=. \
                    -Dsonar.host.url=http://13.229.130.29:32769 \
                    -Dsonar.login=${SONARQUBE_TOKEN}
                """
            }
        }

        // Wait for SonarQube Quality Gate analysis and fail if gate fails
        timeout(time: 5, unit: 'MINUTES') {
            def qualityGate = waitForQualityGate()
            if (qualityGate.status != 'OK') {
                error "SonarQube quality gate failed: ${qualityGate.status}"
            }
        }
    }

    stage('Build image') {
        // Build Docker image and tag it
        app = docker.build("02042025/dockerhub:${env.BUILD_NUMBER}")
    }

    stage('Push image') {
        // Push the Docker image to DockerHub
        docker.withRegistry('https://registry.hub.docker.com', 'dockerhub') {
            app.push("${env.BUILD_NUMBER}")
        }
    }

    stage('Trivy Scan') {
        echo "Running Trivy security scan for the Docker image"
        sh """
            docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v /tmp/trivy:/root/.cache/ \
            aquasec/trivy:latest image 02042025/dockerhub:${env.BUILD_NUMBER}
        """
    }

    stage('Trigger ManifestUpdate') {
        // Trigger the 'updatemanifest' job and pass the Docker tag as a parameter
        echo "Triggering updatemanifest job"
        build job: 'updatemanifest', parameters: [string(name: 'DOCKERTAG', value: env.BUILD_NUMBER)]
    }
}

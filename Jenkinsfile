node {
    def app

    stage('Clone repository') {
        checkout scm
    }

    stage('SonarQube Scan') {
        // Configure the SonarQube environment name in Jenkins global configuration
        def scannerHome = tool name: 'SonarQube Scanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'

        withSonarQubeEnv('SonarQube') {
            sh """
                ${scannerHome}/bin/sonar-scanner \
                -Dsonar.projectKey=my_project_key \
                -Dsonar.sources=. \
                -Dsonar.host.url=http://<your-sonarqube-server>:9000 \
                -Dsonar.login=<your-sonarqube-auth-token>
            """
        }

        // Wait for SonarQube analysis to complete and check Quality Gate status
        timeout(time: 5, unit: 'MINUTES') {
            def qualityGate = waitForQualityGate()
            if (qualityGate.status != 'OK') {
                error "SonarQube quality gate failed: ${qualityGate.status}"
            }
        }
    }
	
	stage('Build image') {
        app = docker.build("02042025/dockerhub")
    }

    stage('Push image') {
        docker.withRegistry('https://registry.hub.docker.com', 'dockerhub') {
            app.push("${env.BUILD_NUMBER}")
        }
    }

    stage('Trivy Scan') {
        echo "Running Trivy security scan for the Docker image"
        sh """
            trivy image 02042025/dockerhub:${env.BUILD_NUMBER}
        """
    }

    stage('Trigger ManifestUpdate') {
        echo "Triggering updatemanifest job"
        build job: 'updatemanifest', parameters: [string(name: 'DOCKERTAG', value: env.BUILD_NUMBER)]
    }
}

pipeline {
    agent any

    environment {
        // 1. CẤU HÌNH DOCKER HUB
        DOCKER_USER = 'ntnguyen055' 
        IMAGE_NAME = 'doctor-appointment'
        TAG = "${env.BUILD_NUMBER}"
        
        // 2. CẤU HÌNH GITHUB
        GIT_URL     = 'https://github.com/NTNguyen055/Doctor-Appointment-System.git'
        GIT_BRANCH  = 'main'
        
        // 3. CẤU HÌNH SONARQUBE (Tại Local)
        SCANNER_HOME      = tool 'SonarQubeScanner'
        SONAR_URL         = 'http://192.168.100.102:9000'
        SONAR_PROJECT_KEY = 'devsecops-lab'
        
        // 4. CẤU HÌNH AWS EC2 DEPLOYMENT (Môi trường Production)
        // IP từ cấu hình cụm máy chủ gốc
        EC2_SERVER_IPS = '13.212.214.54,13.229.211.98'
        DEPLOY_DIR    = '~/doctor-appointment'
        
        // 5. CẤU HÌNH OWASP ZAP (Tấn công)
        TARGET_URL = 'http://13.212.214.54' // Hoặc điền ALB URL

    }

    stages {

        stage('2. SAST - SonarQube Analysis') {
            steps {
                echo '--- Scanning Code with SonarQube ---'
                withSonarQubeEnv('sonar-server') {
                    sh """
                    ${SCANNER_HOME}/bin/sonar-scanner \
                    -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                    -Dsonar.sources=docappsystem \
                    -Dsonar.host.url=${SONAR_URL} \
                    -Dsonar.login=${SONAR_AUTH_TOKEN}
                    """
                }
            }
        }

        stage('3. Build & Push Docker Image') {
            steps {
                echo '--- Building Docker Image ---'
                script {
                    // Dùng dockerhub-creds từ Jenkinsfile gốc
                    docker.withRegistry('', 'dockerhub-creds') {
                        // Build context là thư mục docappsystem
                        def appImage = docker.build("${DOCKER_USER}/${IMAGE_NAME}:${TAG}", "./docappsystem")
                        appImage.push()
                        appImage.push('latest')
                    }
                }
            }
        }

        stage('4. Container Security - Trivy Scan') {
            steps {
                echo '--- Scanning Image with Trivy ---'
                sh "trivy image --severity HIGH,CRITICAL --exit-code 0 ${DOCKER_USER}/${IMAGE_NAME}:${TAG}"
            }
        }

        stage('5. Deploy to AWS EC2 (GitOps Style)') {
            steps {
                script {
                    def servers = env.EC2_SERVER_IPS.split(',')
                    
                    // Sử dụng app-server-ssh-key từ Jenkinsfile gốc để SSH vào EC2
                    sshagent(credentials: ['app-server-ssh-key']) {
                        for (server in servers) {
                            def ip = server.trim()
                            
                            // Tạo thư mục trên EC2
                            sh "ssh -o StrictHostKeyChecking=no ubuntu@${ip} 'mkdir -p ${DEPLOY_DIR}'"
                            
                            // Copy file docker-compose.yml từ Jenkins sang máy EC2
                            sh "scp -o StrictHostKeyChecking=no docker-compose.yml ubuntu@${ip}:${DEPLOY_DIR}/"
                            
                            // Bỏ ghi đè file .env, truyền trực tiếp image tags vào lệnh chạy
                            sh """
                            ssh -o StrictHostKeyChecking=no ubuntu@${ip} '
                                cd ${DEPLOY_DIR}
                                
                                mkdir -p waf-logs
                                sudo chmod 777 waf-logs
                                
                                # Dọn dẹp container cũ
                                sudo docker ps -q --filter "publish=80" | xargs -r sudo docker rm -f
                                sudo docker-compose down --remove-orphans
                                
                                # Chạy container mới: Truyền Image tags vào (Docker Compose sẽ tự tự động đọc file .env cố định trên máy chủ)
                                sudo DOCKER_USER=${DOCKER_USER} IMAGE_NAME=${IMAGE_NAME} TAG=${TAG} docker-compose up -d
                            '
                            """
                        }
                    }
                }
            }
        }
        
        stage('6. DAST - OWASP ZAP Attack') {
            steps {
                echo '--- 💣 Starting ZAP Attack ---'
                script {
                    sh 'rm -rf zap-reports && mkdir -p zap-reports'
                    sh 'docker rm -f zap-scanner > /dev/null 2>&1 || true'
                    
                    def exitCode = sh(
                        script: """
                        docker run --name zap-scanner -u 0 \
                        -v /zap/wrk \
                        -t ghcr.io/zaproxy/zaproxy:stable zap-full-scan.py \
                        -t ${env.TARGET_URL} \
                        -r zap_report.html \
                        -I \
                        -a \
                        -m 2
                        """,
                        returnStatus: true
                    )
                    
                    echo "ZAP finished with exit code: ${exitCode}"
                    sh 'docker cp zap-scanner:/zap/wrk/zap_report.html ./zap-reports/zap_report.html || echo "Failed to copy report"'
                    sh 'docker rm -f zap-scanner > /dev/null 2>&1 || true'
                    sh 'ls -la zap-reports'
                }
            }
        }
        
        stage('7. Publish Report') {
            steps {
                echo '--- 📊 Archiving Report ---'
                publishHTML (target: [
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'zap-reports',
                    reportFiles: 'zap_report.html',
                    reportName: 'OWASP ZAP DAST Report',
                    reportTitles: 'ZAP Security Scan Results'
                ])
            }
        }
    }
}
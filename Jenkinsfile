pipeline {
    agent any

    environment {
        // 1. CẤU HÌNH DOCKER HUB
        DOCKER_USER = 'phanquan277dockerhub' 
        IMAGE_NAME = 'doctor-appointment'
        TAG = "${env.BUILD_NUMBER}"
        
        // 2. CẤU HÌNH GITHUB
        GIT_URL     = 'https://github.com/phanquan277github/Doctor-Appointment-System.git'
        GIT_BRANCH  = 'main'
        
        // 3. CẤU HÌNH SONARQUBE (Tại Local)
        SCANNER_HOME      = tool 'SonarQubeScanner'
        SONAR_URL         = 'http://192.168.100.102:9000'
        SONAR_PROJECT_KEY = 'devsecops-lab'
        
        // 4. CẤU HÌNH AWS EC2 DEPLOYMENT (Môi trường Production)
        // IP từ cấu hình cụm máy chủ gốc
        EC2_SERVER_IPS = '100.111.117.71,100.90.177.20'
        DEPLOY_DIR    = '~/doctor-appointment'
        
        // 5. CẤU HÌNH OWASP ZAP (Tấn công)
        TARGET_URL = 'http://Appointment-Web-ALB-147818110.ap-southeast-1.elb.amazonaws.com' // Hoặc điền ALB URL

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
                    -Dsonar.token=${SONAR_AUTH_TOKEN} \
                    -Dsonar.exclusions=**/static/assets/**,**/*.min.js,**/*.min.css
                    """
                }
            }
        }

        stage('3. Build & Push Docker Image') {
            steps {
                echo '--- Building Docker Image ---'
                script {
                    docker.withRegistry('', 'docker-hub-credentials') {
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
                echo '--- Scanning Image with Trivy Container ---'
                // Dùng container Trivy quét image, tự động xóa container (--rm) sau khi quét xong
                sh """
                docker run --rm \
                -v /var/run/docker.sock:/var/run/docker.sock \
                aquasec/trivy:latest image \
                --severity HIGH,CRITICAL \
                --exit-code 0 \
                ${DOCKER_USER}/${IMAGE_NAME}:${TAG}
                """
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
                                sudo -E env DOCKER_USER=${DOCKER_USER} IMAGE_NAME=${IMAGE_NAME} TAG=${TAG} docker-compose up -d
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
                    sh 'rm -rf zap-reports && mkdir -p zap-reports && chmod 777 zap-reports'
                    sh 'docker rm -f zap-scanner > /dev/null 2>&1 || true'
                    
                    try {
                        // Ép khối lệnh chạy tối đa 5 phút, quá 5 phút Jenkins sẽ tự động trảm
                        timeout(time: 5, unit: 'MINUTES') {
                            def exitCode = sh(
                                script: """
                                docker run --name zap-scanner -u 0 \
                                -v \$(pwd)/zap-reports:/zap/wrk:rw \
                                -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
                                -t ${env.TARGET_URL} \
                                -r zap_report.html \
                                -m 1 \
                                -T 2 -I
                                """,
                                returnStatus: true
                            )
                            echo "ZAP finished with exit code: ${exitCode}"
                        }
                    } catch (org.jenkinsci.plugins.workflow.steps.FlowInterruptedException e) {
                        echo "⚠️ CẢNH BÁO: ZAP Scan mất quá nhiều thời gian và đã bị Jenkins ép dừng!"
                    } catch (Exception e) {
                        echo "⚠️ ZAP Scan gặp lỗi vặt: ${e.getMessage()}"
                    } finally {
                        // Khối 'finally' LUÔN LUÔN CHẠY dù ở trên có bị lỗi hay bị ép dừng
                        // Phương án dự phòng: Cố gắng copy file ra nếu Volume Mount thất bại
                        sh 'docker cp zap-scanner:/zap/wrk/zap_report.html ./zap-reports/zap_report.html > /dev/null 2>&1 || echo "Report already exists or container stopped"'
                        
                        // Dọn dẹp container và in danh sách file đúng như bạn muốn
                        sh 'docker rm -f zap-scanner > /dev/null 2>&1 || true'
                        sh 'ls -la zap-reports'
                    }
                }
            }
        }
        
        stage('7. Publish Report') {
            steps {
                echo '--- 📊 Archiving Report ---'
                script {
                    if (fileExists('zap-reports/zap_report.html')) {
                        publishHTML (target: [
                            allowMissing: false,
                            alwaysLinkToLastBuild: true,
                            keepAll: true,
                            reportDir: 'zap-reports',
                            reportFiles: 'zap_report.html',
                            reportName: 'OWASP ZAP DAST Report',
                            reportTitles: 'ZAP Security Scan Results'
                        ])
                    } else {
                        echo "⚠️ Warning: ZAP Report file not found, skipping publish step."
                    }
                }
                echo 'DONE test web hook 30/4 v5'
            }
        }
    }
}
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'ntnguyen055/doctor-appointment'
        APP_SERVER_IP = '18.183.172.77'
        APP_SERVER_USER = 'ubuntu'
        DOCKERHUB_CREDS = credentials('dockerhub-creds')
    }

    stages {
        stage('1. Checkout SCM') {
            steps {
                echo 'Đang kéo mã nguồn mới nhất từ GitHub.....'
                checkout scm
            }
        }

        stage('2. Build Image') {
            steps {
                echo 'Đóng gói Docker Image...'
                sh "docker build -t ${IMAGE_NAME}:latest ./docappsystem"
            }
        }

        stage('3. Push to Docker Hub') {
            steps {
                echo 'Đẩy Image lên lưu trữ...'
                sh 'echo $DOCKERHUB_CREDS_PSW | docker login -u $DOCKERHUB_CREDS_USR --password-stdin'
                sh "docker push ${IMAGE_NAME}:latest"
            }
        }

        stage('4. Đồng bộ Cấu hình (SCP)') {
            steps {
                echo 'Đẩy tệp cấu hình và Nginx sang App Server...'
                sshagent(credentials: ['app-server-ssh-key']) {
                    sh "ssh -o StrictHostKeyChecking=no ${APP_SERVER_USER}@${APP_SERVER_IP} 'mkdir -p ~/doctor-appointment/SQLFile ~/doctor-appointment/nginx'"
                    sh "scp -o StrictHostKeyChecking=no docker-compose.yml ${APP_SERVER_USER}@${APP_SERVER_IP}:~/doctor-appointment/"
                    sh "scp -o StrictHostKeyChecking=no SQLFile/docaspythondb.sql ${APP_SERVER_USER}@${APP_SERVER_IP}:~/doctor-appointment/SQLFile/"
                    sh "scp -o StrictHostKeyChecking=no nginx/default.conf ${APP_SERVER_USER}@${APP_SERVER_IP}:~/doctor-appointment/nginx/"
                }
            }
        }

        stage('5. Deploy & Auto-Rollback') {
            steps {
                echo 'Triển khai hệ thống với cơ chế Rollback an toàn...'
                sshagent(credentials: ['app-server-ssh-key']) {
                    sh """ssh -o StrictHostKeyChecking=no ${APP_SERVER_USER}@${APP_SERVER_IP} '
                        cd ~/doctor-appointment
                        
                        echo "1. Backup phiên bản đang chạy (nếu có)..."
                        docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:previous || true
                        
                        echo "2. Kéo và chạy phiên bản mới..."
                        docker-compose pull web
                        docker-compose down
                        docker-compose up -d
                        
                        echo "3. Health Check: Chờ 10 giây để kiểm tra ứng dụng..."
                        sleep 10
                        if [ "\$(docker inspect -f '{{.State.Running}}' django_web)" != "true" ]; then
                            echo "PHÁT HIỆN LỖI: Container web bị sập! Tiến hành Auto-Rollback..."
                            docker-compose down
                            docker tag ${IMAGE_NAME}:previous ${IMAGE_NAME}:latest
                            docker-compose up -d
                            echo "Rollback thành công! Đã khôi phục phiên bản cũ."
                            exit 1
                        else
                            echo "Container web hoạt động ổn định. Triển khai thành công!"
                            docker image prune -f
                        fi
                    '"""
                }
            }
        }
        
        stage('6. Dọn dẹp Jenkins') {
            steps {
                sh 'docker image prune -f'
                sh 'docker logout'
            }
        }
    }
}
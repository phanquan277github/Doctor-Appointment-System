#!/bin/sh

# Dừng script nếu có bất kỳ lệnh nào bị lỗi trong quá trình thực thi
set -e

# Hệ thống sử dụng AWS RDS nên luôn ở trạng thái Available, tiến hành Migrate trực tiếp
echo "AWS RDS is ready! Applying Database Migrations..."

# --- 2 LỆNH TỰ ĐỘNG ĐỒNG BỘ CẤU TRÚC DATABASE ---
python manage.py makemigrations
python manage.py migrate
# ------------------------------------------------

echo "Migrations completed! Starting Django Server..."

# Chạy lệnh khởi động máy chủ Web thực sự (gunicorn...) được truyền từ docker-compose
exec "$@"
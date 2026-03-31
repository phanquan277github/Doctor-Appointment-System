#!/bin/sh

# Dừng script nếu có bất kỳ lệnh nào bị lỗi
set -e

echo "AWS RDS is ready! Applying Database Migrations..."

# --- 2 LỆNH TỰ ĐỘNG ĐỒNG BỘ CẤU TRÚC DATABASE ---
python manage.py makemigrations
python manage.py migrate

echo "Migrations completed! Starting Django Server..."

# Chạy lệnh thực sự khởi tạo Gunicorn
exec "$@"
from pathlib import Path
import os

# Xây dựng đường dẫn gốc của project, ví dụ: BASE_DIR / 'thư_mục_con'
BASE_DIR = Path(__file__).resolve().parent.parent

# CẢNH BÁO BẢO MẬT: Giữ SECRET_KEY bí mật khi deploy production
SECRET_KEY = 'django-insecure-=u!!em!u$#9d=ew1uzeq&=90w(%62nx5b)9j66kbhh2*ee__il'

# CẢNH BÁO BẢO MẬT: Không bật DEBUG khi chạy trên môi trường production
DEBUG = True

# Cho phép tất cả các host truy cập (cần thiết khi chạy trong Docker hoặc môi trường test)
ALLOWED_HOSTS = ['*']

# Định nghĩa các ứng dụng được cài đặt trong project
INSTALLED_APPS = [
    'django.contrib.admin',          # Trang quản trị Django
    'django.contrib.auth',           # Hệ thống xác thực người dùng
    'django.contrib.contenttypes',   # Quản lý kiểu dữ liệu nội dung
    'django.contrib.sessions',       # Quản lý session người dùng
    'django.contrib.messages',       # Hệ thống thông báo
    'django.contrib.staticfiles',    # Quản lý file tĩnh (CSS, JS, Images)
    'dasapp',                       # App chính của hệ thống
    'storages'                      # Thư viện AWS S3
]

# Danh sách middleware xử lý request/response
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',         # Middleware bảo mật
    'whitenoise.middleware.WhiteNoiseMiddleware',            # Middleware xử lý folder static 
    'django.contrib.sessions.middleware.SessionMiddleware',  # Middleware quản lý session
    'django.middleware.common.CommonMiddleware',             # Middleware xử lý chung
    'django.middleware.csrf.CsrfViewMiddleware',             # Middleware chống tấn công CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Middleware xác thực người dùng
    'django.contrib.messages.middleware.MessageMiddleware',  # Middleware xử lý message
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Middleware chống clickjacking
]

# File cấu hình URL gốc của project
ROOT_URLCONF = 'docappsystem.urls'

# Cấu hình hệ thống template
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        # Thư mục chứa template chung của project
        'DIRS': [os.path.join(BASE_DIR,'templates')],

        # Cho phép Django tự động tìm template trong từng app
        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',      # Cung cấp biến debug cho template
                'django.template.context_processors.request',    # Cung cấp object request
                'django.contrib.auth.context_processors.auth',   # Cung cấp thông tin user
                'django.contrib.messages.context_processors.messages', # Cung cấp message
            ],
        },
    },
]

# Cấu hình WSGI để deploy ứng dụng
WSGI_APPLICATION = 'docappsystem.wsgi.application'

# Cấu hình cơ sở dữ liệu
# Sử dụng kết nối luân chuyển lấy từ két sắt .env để kết nối tới AWS RDS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('RDS_DB_NAME', 'docaspythondb'),
        'USER': os.environ.get('RDS_USERNAME', 'admin'),
        'PASSWORD': os.environ.get('RDS_PASSWORD', 'Banhmi4o'),
        'HOST': os.environ.get('RDS_ENDPOINT'),  # Trỏ về AWS RDS Endpoint
        'PORT': os.environ.get('RDS_PORT', '3306'),
    }
}

# Cấu hình kiểm tra độ mạnh của mật khẩu
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Cấu hình ngôn ngữ mặc định của hệ thống
LANGUAGE_CODE = 'en-us'

# QUAN TRỌNG: Cấu hình múi giờ Việt Nam để lưu đúng thời gian vào database
TIME_ZONE = 'Asia/Ho_Chi_Minh'

# Bật hệ thống quốc tế hóa (internationalization)
USE_I18N = True

# Đặt False để Django lưu thời gian đúng theo giờ hệ thống (không chuyển sang UTC)
USE_TZ = False

# Cấu hình đường dẫn file tĩnh (CSS, JS, Images)
STATIC_URL = 'static/'

# Thư mục chứa file tĩnh trong project
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR,'static')]

# Cấu hình file media (ảnh upload, file người dùng upload)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Kiểu khóa chính mặc định cho model
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Sử dụng CustomUser model thay vì User mặc định của Django
AUTH_USER_MODEL = 'dasapp.CustomUser'

# Khai báo động các biến môi trường cấu hình AWS S3
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'ap-southeast-1')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_DEFAULT_ACL = 'public-read'

# Cấu hình phân tách rành mạch cơ chế lưu trữ File: Static giữ nguyên, Media ném thẳng lên S3
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    STORAGES = {
        "default": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    }
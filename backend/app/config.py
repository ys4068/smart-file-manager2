"""Flask 应用配置"""
import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # MySQL
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'smart_file_manager')
    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}'
        f'@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 文件上传
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {
        'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif',
        'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
        'zip', 'rar', '7z', 'md', 'json', 'xml',
        'py', 'js', 'html', 'css', 'java', 'cpp', 'c',
    }

    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/test_{Config.MYSQL_DB}?charset=utf8mb4'


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}

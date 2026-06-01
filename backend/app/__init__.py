"""Flask 应用工厂"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .config import config_map

db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'].split(','))

    # 注册蓝图
    from .routes.auth import auth_bp
    from .routes.files import files_bp
    from .routes.bookmarks import bookmarks_bp
    from .routes.tags import tags_bp
    from .routes.stats import stats_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(files_bp, url_prefix='/api/files')
    app.register_blueprint(bookmarks_bp, url_prefix='/api/bookmarks')
    app.register_blueprint(tags_bp, url_prefix='/api/tags')
    app.register_blueprint(stats_bp, url_prefix='/api/stats')

    return app

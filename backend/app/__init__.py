from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from .config import config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, supports_credentials=True)
    jwt.init_app(app)

    # Ensure upload folder
    import os

    # Serve frontend static files
    frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "../frontend/dist")
    frontend_dist = os.path.abspath(frontend_dist)
    app.static_folder = os.path.join(frontend_dist, "assets")
    app.static_url_path = "/assets"

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Serve index.html for all non-API routes (SPA)
    from flask import send_from_directory, abort
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        # Skip API routes
        if path.startswith("api/"):
            abort(404)
        # Try to serve the requested file, fall back to index.html (SPA routing)
        if path and os.path.isfile(os.path.join(frontend_dist, path)):
            return send_from_directory(frontend_dist, path)
        return send_from_directory(frontend_dist, "index.html")

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.files import files_bp
    from .routes.bookmarks import bookmarks_bp
    from .routes.dashboard import dashboard_bp
    from .routes.search import search_bp
    from .routes.folders import folders_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(files_bp, url_prefix="/api/files")
    app.register_blueprint(bookmarks_bp, url_prefix="/api/bookmarks")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(search_bp, url_prefix="/api/search")
    app.register_blueprint(folders_bp, url_prefix="/api/folders")

    # Health check
    @app.route("/api/health")
    def health():
        return {"status": "ok", "message": "Smart File Manager API is running"}

    return app

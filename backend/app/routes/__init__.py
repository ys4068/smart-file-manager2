from .auth import auth_bp
from .files import files_bp
from .bookmarks import bookmarks_bp
from .dashboard import dashboard_bp
from .search import search_bp

__all__ = ["auth_bp", "files_bp", "bookmarks_bp", "dashboard_bp", "search_bp"]

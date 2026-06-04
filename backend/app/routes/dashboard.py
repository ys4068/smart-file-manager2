from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.file import File
from app.models.bookmark import Bookmark
from app.models.folder import Folder

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("", methods=["GET"])
@jwt_required()
def get_dashboard():
    user_id = int(get_jwt_identity())

    total_files = File.query.filter_by(user_id=user_id).count()
    total_bookmarks = Bookmark.query.filter_by(user_id=user_id).count()
    total_size = db.session.query(db.func.sum(File.file_size)).filter_by(user_id=user_id).scalar() or 0
    recent_files = File.query.filter_by(user_id=user_id).order_by(File.created_at.desc()).limit(5).all()
    recent_bookmarks = Bookmark.query.filter_by(user_id=user_id).order_by(Bookmark.created_at.desc()).limit(5).all()
    favorite_files = File.query.filter_by(user_id=user_id, is_favorite=True).count()
    read_later_bookmarks = Bookmark.query.filter_by(user_id=user_id, is_read_later=True).count()
    total_folders = Folder.query.filter_by(user_id=user_id).count()
    public_files = File.query.filter_by(user_id=user_id, is_public=True).count()

    # File type distribution
    file_types = (
        db.session.query(File.file_type, db.func.count(File.id))
        .filter_by(user_id=user_id)
        .group_by(File.file_type)
        .all()
    )

    return jsonify({
        "stats": {
            "total_files": total_files,
            "total_bookmarks": total_bookmarks,
            "total_size": total_size,
            "favorite_files": favorite_files,
            "read_later_bookmarks": read_later_bookmarks,
            "total_folders": total_folders,
            "public_files": public_files,
        },
        "file_types": [{"type": t[0], "count": t[1]} for t in file_types],
        "recent_files": [f.to_dict() for f in recent_files],
        "recent_bookmarks": [b.to_dict() for b in recent_bookmarks],
    })

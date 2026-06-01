"""统计路由"""
from datetime import datetime, timedelta
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from .. import db
from ..models.file import FileItem
from ..models.bookmark import Bookmark
from ..models.tag import Tag

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    """仪表盘统计"""
    user_id = int(get_jwt_identity())

    total_files = FileItem.query.filter_by(user_id=user_id).count()
    total_bookmarks = Bookmark.query.filter_by(user_id=user_id).count()
    total_tags = Tag.query.filter_by(user_id=user_id).count()
    total_storage = db.session.query(func.sum(FileItem.file_size)) \
        .filter_by(user_id=user_id).scalar() or 0

    # 最近7天新增统计
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_files = FileItem.query.filter(
        FileItem.user_id == user_id,
        FileItem.created_at >= week_ago
    ).count()
    recent_bookmarks = Bookmark.query.filter(
        Bookmark.user_id == user_id,
        Bookmark.created_at >= week_ago
    ).count()

    # 文件类型分布
    type_dist = db.session.query(
        FileItem.file_type, func.count(FileItem.id)
    ).filter(FileItem.user_id == user_id, FileItem.file_type != '') \
        .group_by(FileItem.file_type).all()

    # 热门标签
    top_tags_source = db.session.query(
        Tag.name, Tag.color, func.count(file_tags.c.file_id).label('count')
    ).join(file_tags, Tag.id == file_tags.c.tag_id) \
        .join(FileItem, FileItem.id == file_tags.c.file_id) \
        .filter(FileItem.user_id == user_id) \
        .group_by(Tag.id).order_by(func.count(file_tags.c.file_id).desc()).limit(10).all()

    return jsonify({
        'code': 200,
        'data': {
            'total_files': total_files,
            'total_bookmarks': total_bookmarks,
            'total_tags': total_tags,
            'total_storage_bytes': total_storage,
            'recent_files': recent_files,
            'recent_bookmarks': recent_bookmarks,
            'file_type_distribution': {t: c for t, c in type_dist},
            'top_tags': [{'name': n, 'color': c, 'count': ct} for n, c, ct in top_tags_source],
        }
    })

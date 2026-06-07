from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.file import File
from app.models.bookmark import Bookmark
from app.services.suggestion import suggest_from_url, suggest

search_bp = Blueprint("search", __name__)


@search_bp.route("", methods=["GET"])
@jwt_required()
def global_search():
    user_id = int(get_jwt_identity())
    keyword = request.args.get("q", "").strip()
    if not keyword:
        return jsonify({"error": "请输入搜索关键词"}), 400

    # Search files
    files = (
        File.query.filter_by(user_id=user_id)
        .filter(
            db.or_(
                File.original_name.ilike(f"%{keyword}%"),
                File.description.ilike(f"%{keyword}%"),
                File.tags.ilike(f"%{keyword}%"),
                File.category.ilike(f"%{keyword}%"),
            )
        )
        .limit(20)
        .all()
    )

    # Search bookmarks
    bookmarks = (
        Bookmark.query.filter_by(user_id=user_id)
        .filter(
            db.or_(
                Bookmark.title.ilike(f"%{keyword}%"),
                Bookmark.url.ilike(f"%{keyword}%"),
                Bookmark.description.ilike(f"%{keyword}%"),
                Bookmark.tags.ilike(f"%{keyword}%"),
                Bookmark.category.ilike(f"%{keyword}%"),
            )
        )
        .limit(20)
        .all()
    )

    return jsonify({
        "keyword": keyword,
        "files": [f.to_dict() for f in files],
        "bookmarks": [b.to_dict() for b in bookmarks],
        "total": len(files) + len(bookmarks),
    })


@search_bp.route("/suggest", methods=["POST"])
@jwt_required()
def smart_suggest():
    """智能建议 - 支持文本+URL综合输入"""
    data = request.get_json()
    text = data.get("text", "")
    url = data.get("url", "")

    if not text and not url:
        return jsonify({"error": "请输入文本或URL"}), 400

    result = suggest(text=text, url=url)
    return jsonify(result)


@search_bp.route("/suggest-url", methods=["POST"])
@jwt_required()
def suggest_url():
    """URL 智能提取 - 根据URL推荐分类和标签"""
    data = request.get_json()
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"error": "请输入URL"}), 400

    result = suggest_from_url(url)
    return jsonify(result)

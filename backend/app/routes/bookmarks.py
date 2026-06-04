from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.bookmark import Bookmark

bookmarks_bp = Blueprint("bookmarks", __name__)


@bookmarks_bp.route("", methods=["GET"])
@jwt_required()
def list_bookmarks():
    user_id = int(get_jwt_identity())
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    category = request.args.get("category")
    search = request.args.get("search")
    favorite = request.args.get("favorite")
    read_later = request.args.get("read_later")

    query = Bookmark.query.filter_by(user_id=user_id)
    if category:
        query = query.filter_by(category=category)
    if favorite == "1":
        query = query.filter_by(is_favorite=True)
    if read_later == "1":
        query = query.filter_by(is_read_later=True)
    if search:
        query = query.filter(
            db.or_(
                Bookmark.title.ilike(f"%{search}%"),
                Bookmark.url.ilike(f"%{search}%"),
                Bookmark.description.ilike(f"%{search}%"),
                Bookmark.tags.ilike(f"%{search}%"),
            )
        )

    pagination = query.order_by(Bookmark.updated_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        "bookmarks": [b.to_dict() for b in pagination.items],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages,
    })


@bookmarks_bp.route("", methods=["POST"])
@jwt_required()
def create_bookmark():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    title = data.get("title", "").strip()
    url = data.get("url", "").strip()
    if not title or not url:
        return jsonify({"error": "标题和URL不能为空"}), 400

    bookmark = Bookmark(
        title=title,
        url=url,
        description=data.get("description", ""),
        tags=",".join(data["tags"]) if isinstance(data.get("tags"), list) else data.get("tags", ""),
        category=data.get("category", "未分类"),
        is_read_later=data.get("is_read_later", False),
        user_id=user_id,
    )
    db.session.add(bookmark)
    db.session.commit()
    return jsonify({"message": "书签添加成功", "bookmark": bookmark.to_dict()}), 201


@bookmarks_bp.route("/<int:bookmark_id>", methods=["GET"])
@jwt_required()
def get_bookmark(bookmark_id):
    user_id = int(get_jwt_identity())
    bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=user_id).first()
    if not bookmark:
        return jsonify({"error": "书签不存在"}), 404
    return jsonify({"bookmark": bookmark.to_dict()})


@bookmarks_bp.route("/<int:bookmark_id>", methods=["PUT"])
@jwt_required()
def update_bookmark(bookmark_id):
    user_id = int(get_jwt_identity())
    bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=user_id).first()
    if not bookmark:
        return jsonify({"error": "书签不存在"}), 404

    data = request.get_json()
    if "title" in data:
        bookmark.title = data["title"]
    if "url" in data:
        bookmark.url = data["url"]
    if "description" in data:
        bookmark.description = data["description"]
    if "tags" in data:
        bookmark.tags = ",".join(data["tags"]) if isinstance(data["tags"], list) else data["tags"]
    if "category" in data:
        bookmark.category = data["category"]
    if "is_favorite" in data:
        bookmark.is_favorite = data["is_favorite"]
    if "is_read_later" in data:
        bookmark.is_read_later = data["is_read_later"]

    db.session.commit()
    return jsonify({"message": "更新成功", "bookmark": bookmark.to_dict()})


@bookmarks_bp.route("/<int:bookmark_id>", methods=["DELETE"])
@jwt_required()
def delete_bookmark(bookmark_id):
    user_id = int(get_jwt_identity())
    bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=user_id).first()
    if not bookmark:
        return jsonify({"error": "书签不存在"}), 404

    db.session.delete(bookmark)
    db.session.commit()
    return jsonify({"message": "删除成功"})


@bookmarks_bp.route("/<int:bookmark_id>/visit", methods=["POST"])
@jwt_required()
def visit_bookmark(bookmark_id):
    user_id = int(get_jwt_identity())
    bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=user_id).first()
    if not bookmark:
        return jsonify({"error": "书签不存在"}), 404

    bookmark.visit_count += 1
    db.session.commit()
    return jsonify({"message": "已记录访问", "visit_count": bookmark.visit_count})


@bookmarks_bp.route("/categories", methods=["GET"])
@jwt_required()
def get_categories():
    user_id = int(get_jwt_identity())
    categories = (
        db.session.query(Bookmark.category, db.func.count(Bookmark.id))
        .filter_by(user_id=user_id)
        .group_by(Bookmark.category)
        .all()
    )
    return jsonify({
        "categories": [{"name": c[0], "count": c[1]} for c in categories]
    })

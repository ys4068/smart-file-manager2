import os
import uuid
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db
from app.models.file import File

files_bp = Blueprint("files", __name__)

ALLOWED_EXTENSIONS = {
    "txt", "pdf", "png", "jpg", "jpeg", "gif", "webp", "svg",
    "doc", "docx", "xls", "xlsx", "ppt", "pptx",
    "zip", "rar", "7z", "tar", "gz",
    "mp3", "mp4", "avi", "mov",
    "py", "js", "html", "css", "json", "xml", "md", "csv",
}

TYPE_MAP = {
    "png": "image", "jpg": "image", "jpeg": "image", "gif": "image",
    "webp": "image", "svg": "image",
    "pdf": "document", "doc": "document", "docx": "document",
    "xls": "document", "xlsx": "document", "ppt": "document", "pptx": "document",
    "txt": "document", "md": "document", "csv": "document",
    "mp4": "video", "avi": "video", "mov": "video",
    "mp3": "audio", "zip": "archive", "rar": "archive", "7z": "archive",
}


def get_file_type(ext):
    return TYPE_MAP.get(ext, "other")


@files_bp.route("", methods=["GET"])
@jwt_required()
def list_files():
    user_id = int(get_jwt_identity())
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    category = request.args.get("category")
    file_type = request.args.get("file_type")
    search = request.args.get("search")
    favorite = request.args.get("favorite")

    query = File.query.filter_by(user_id=user_id)
    if category:
        query = query.filter_by(category=category)
    if file_type:
        query = query.filter_by(file_type=file_type)
    if favorite == "1":
        query = query.filter_by(is_favorite=True)
    if search:
        query = query.filter(
            db.or_(
                File.original_name.ilike(f"%{search}%"),
                File.description.ilike(f"%{search}%"),
                File.tags.ilike(f"%{search}%"),
            )
        )

    pagination = query.order_by(File.updated_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        "files": [f.to_dict() for f in pagination.items],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages,
    })


@files_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_file():
    user_id = int(get_jwt_identity())
    if "file" not in request.files:
        return jsonify({"error": "请选择文件"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "请选择文件"}), 400

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": f"不支持的文件类型: .{ext}"}), 400

    original_name = secure_filename(file.filename)
    stored_name = f"{uuid.uuid4().hex}.{ext}"
    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], stored_name)
    file.save(upload_path)

    file_size = os.path.getsize(upload_path)
    file_type = get_file_type(ext)
    category = request.form.get("category", "未分类")
    description = request.form.get("description", "")
    tags = request.form.get("tags", "")

    file_record = File(
        filename=stored_name,
        original_name=original_name,
        file_size=file_size,
        file_type=file_type,
        mime_type=file.content_type,
        description=description,
        tags=tags,
        category=category,
        user_id=user_id,
    )
    db.session.add(file_record)
    db.session.commit()

    return jsonify({"message": "上传成功", "file": file_record.to_dict()}), 201


@files_bp.route("/<int:file_id>", methods=["GET"])
@jwt_required()
def get_file(file_id):
    user_id = int(get_jwt_identity())
    file = File.query.filter_by(id=file_id, user_id=user_id).first()
    if not file:
        return jsonify({"error": "文件不存在"}), 404
    return jsonify({"file": file.to_dict()})


@files_bp.route("/<int:file_id>/download", methods=["GET"])
@jwt_required()
def download_file(file_id):
    user_id = int(get_jwt_identity())
    file = File.query.filter_by(id=file_id, user_id=user_id).first()
    if not file:
        return jsonify({"error": "文件不存在"}), 404

    file.download_count += 1
    db.session.commit()

    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        file.filename,
        as_attachment=True,
        download_name=file.original_name,
    )


@files_bp.route("/<int:file_id>", methods=["PUT"])
@jwt_required()
def update_file(file_id):
    user_id = int(get_jwt_identity())
    file = File.query.filter_by(id=file_id, user_id=user_id).first()
    if not file:
        return jsonify({"error": "文件不存在"}), 404

    data = request.get_json()
    if "description" in data:
        file.description = data["description"]
    if "tags" in data:
        file.tags = ",".join(data["tags"]) if isinstance(data["tags"], list) else data["tags"]
    if "category" in data:
        file.category = data["category"]
    if "is_favorite" in data:
        file.is_favorite = data["is_favorite"]

    db.session.commit()
    return jsonify({"message": "更新成功", "file": file.to_dict()})


@files_bp.route("/<int:file_id>", methods=["DELETE"])
@jwt_required()
def delete_file(file_id):
    user_id = int(get_jwt_identity())
    file = File.query.filter_by(id=file_id, user_id=user_id).first()
    if not file:
        return jsonify({"error": "文件不存在"}), 404

    # Remove physical file
    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], file.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(file)
    db.session.commit()
    return jsonify({"message": "删除成功"})


@files_bp.route("/categories", methods=["GET"])
@jwt_required()
def get_categories():
    user_id = int(get_jwt_identity())
    categories = (
        db.session.query(File.category, db.func.count(File.id))
        .filter_by(user_id=user_id)
        .group_by(File.category)
        .all()
    )
    return jsonify({
        "categories": [{"name": c[0], "count": c[1]} for c in categories]
    })

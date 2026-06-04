import os
import uuid
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db
from app.models.file import File, generate_share_token
from app.services.file_permission import FilePermissionService
from app.utils.file_utils import FileUtils

files_bp = Blueprint("files", __name__)


# ==================== CRUD ====================

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
    folder_id = request.args.get("folder_id", type=int)

    query = File.query.filter_by(user_id=user_id)
    if category:
        query = query.filter_by(category=category)
    if file_type:
        query = query.filter_by(file_type=file_type)
    if favorite == "1":
        query = query.filter_by(is_favorite=True)
    if folder_id is not None:
        query = query.filter_by(folder_id=folder_id if folder_id > 0 else None)
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
    if not FileUtils.is_allowed(ext):
        return jsonify({"error": f"不支持的文件类型: .{ext}"}), 400

    original_name = secure_filename(file.filename)
    stored_name = f"{uuid.uuid4().hex}.{ext}"
    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], stored_name)
    file.save(upload_path)

    file_size = os.path.getsize(upload_path)
    file_type = FileUtils.get_file_type(ext)
    category = request.form.get("category", "未分类")
    description = request.form.get("description", "")
    tags = request.form.get("tags", "")
    folder_id = request.form.get("folder_id", type=int)

    # 验证文件夹归属
    if folder_id:
        from app.models.folder import Folder
        folder = Folder.query.filter_by(id=folder_id, user_id=user_id).first()
        if not folder:
            return jsonify({"error": "文件夹不存在"}), 404

    file_record = File(
        filename=stored_name,
        original_name=original_name,
        file_size=file_size,
        file_type=file_type,
        mime_type=file.content_type,
        description=description,
        tags=tags,
        category=category,
        folder_id=folder_id,
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
    if "folder_id" in data:
        fid = data["folder_id"]
        if fid:
            from app.models.folder import Folder
            folder = Folder.query.filter_by(id=fid, user_id=user_id).first()
            if not folder:
                return jsonify({"error": "目标文件夹不存在"}), 404
        file.folder_id = fid

    db.session.commit()
    return jsonify({"message": "更新成功", "file": file.to_dict()})


@files_bp.route("/<int:file_id>", methods=["DELETE"])
@jwt_required()
def delete_file(file_id):
    user_id = int(get_jwt_identity())
    file = File.query.filter_by(id=file_id, user_id=user_id).first()
    if not file:
        return jsonify({"error": "文件不存在"}), 404

    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], file.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(file)
    db.session.commit()
    return jsonify({"message": "删除成功"})


# ==================== 分享与权限 ====================

@files_bp.route("/<int:file_id>/share", methods=["POST"])
@jwt_required()
def generate_share(file_id):
    """生成分享链接"""
    user_id = int(get_jwt_identity())
    file = File.query.filter_by(id=file_id, user_id=user_id).first()
    if not file:
        return jsonify({"error": "文件不存在"}), 404

    token = FilePermissionService.generate_share_link(file)
    return jsonify({
        "message": "分享链接已生成",
        "share_token": token,
        "share_url": f"/api/files/share/{token}",
    })


@files_bp.route("/<int:file_id>/share", methods=["DELETE"])
@jwt_required()
def revoke_share(file_id):
    """撤销分享"""
    user_id = int(get_jwt_identity())
    file = File.query.filter_by(id=file_id, user_id=user_id).first()
    if not file:
        return jsonify({"error": "文件不存在"}), 404

    FilePermissionService.revoke_share(file)
    return jsonify({"message": "分享已撤销"})


@files_bp.route("/<int:file_id>/public", methods=["POST"])
@jwt_required()
def toggle_public(file_id):
    """切换公有/私有"""
    user_id = int(get_jwt_identity())
    file = File.query.filter_by(id=file_id, user_id=user_id).first()
    if not file:
        return jsonify({"error": "文件不存在"}), 404

    data = request.get_json()
    is_public = data.get("is_public", False)
    FilePermissionService.set_public(file, is_public)
    return jsonify({
        "message": "已设为公有" if is_public else "已设为私有",
        "file": file.to_dict(),
    })


# ==================== 公开分享（无需登录） ====================

@files_bp.route("/share/<token>", methods=["GET"])
def access_shared(token):
    """通过分享链接访问文件"""
    file = File.query.filter_by(share_token=token).first()
    if not file:
        return jsonify({"error": "分享链接无效或已失效"}), 404

    return jsonify({"file": file.to_dict()})


@files_bp.route("/share/<token>/download", methods=["GET"])
def download_shared(token):
    """通过分享链接下载文件"""
    file = File.query.filter_by(share_token=token).first()
    if not file:
        return jsonify({"error": "分享链接无效或已失效"}), 404

    file.download_count += 1
    db.session.commit()

    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        file.filename,
        as_attachment=True,
        download_name=file.original_name,
    )


# ==================== 移动文件 ====================

@files_bp.route("/<int:file_id>/move", methods=["POST"])
@jwt_required()
def move_file(file_id):
    """移动文件到指定文件夹"""
    user_id = int(get_jwt_identity())
    file = File.query.filter_by(id=file_id, user_id=user_id).first()
    if not file:
        return jsonify({"error": "文件不存在"}), 404

    data = request.get_json()
    target_folder_id = data.get("folder_id")  # None 表示移动到根目录

    if target_folder_id:
        from app.models.folder import Folder
        folder = Folder.query.filter_by(id=target_folder_id, user_id=user_id).first()
        if not folder:
            return jsonify({"error": "目标文件夹不存在"}), 404
        file.folder_id = target_folder_id
    else:
        file.folder_id = None

    db.session.commit()
    return jsonify({"message": "移动成功", "file": file.to_dict()})


# ==================== 分类 ====================

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

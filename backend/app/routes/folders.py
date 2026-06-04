from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.folder import Folder

folders_bp = Blueprint("folders", __name__)


@folders_bp.route("", methods=["GET"])
@jwt_required()
def get_folders():
    """获取文件夹树"""
    user_id = int(get_jwt_identity())
    folders = (
        Folder.query.filter_by(user_id=user_id, parent_id=None)
        .order_by(Folder.name)
        .all()
    )
    return jsonify({"folders": [f.to_tree() for f in folders]})


@folders_bp.route("/flat", methods=["GET"])
@jwt_required()
def get_folders_flat():
    """获取扁平文件夹列表（下拉选择用）"""
    user_id = int(get_jwt_identity())
    folders = (
        Folder.query.filter_by(user_id=user_id)
        .order_by(Folder.level, Folder.name)
        .all()
    )
    return jsonify({"folders": [
        {**f.to_dict(), "prefix": "　" * f.level if f.level else ""}
        for f in folders
    ]})


@folders_bp.route("", methods=["POST"])
@jwt_required()
def create_folder():
    """创建文件夹"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    name = data.get("name", "").strip()
    parent_id = data.get("parent_id")

    if not name:
        return jsonify({"error": "文件夹名称不能为空"}), 400

    # 检查同级重名
    existing = Folder.query.filter_by(
        user_id=user_id, parent_id=parent_id, name=name
    ).first()
    if existing:
        return jsonify({"error": "同级文件夹已存在同名"}), 409

    # 计算层级
    level = 0
    if parent_id:
        parent = Folder.query.filter_by(id=parent_id, user_id=user_id).first()
        if not parent:
            return jsonify({"error": "父文件夹不存在"}), 404
        level = parent.level + 1
        if level > 5:
            return jsonify({"error": "文件夹层级不能超过5层"}), 400

    folder = Folder(name=name, parent_id=parent_id, level=level, user_id=user_id)
    db.session.add(folder)
    db.session.commit()

    return jsonify({"message": "创建成功", "folder": folder.to_dict()}), 201


@folders_bp.route("/<int:folder_id>", methods=["PUT"])
@jwt_required()
def rename_folder(folder_id):
    """重命名文件夹"""
    user_id = int(get_jwt_identity())
    folder = Folder.query.filter_by(id=folder_id, user_id=user_id).first()
    if not folder:
        return jsonify({"error": "文件夹不存在"}), 404

    data = request.get_json()
    new_name = data.get("name", "").strip()
    if not new_name:
        return jsonify({"error": "名称不能为空"}), 400

    # 检查同级重名
    dup = Folder.query.filter(
        Folder.id != folder_id,
        Folder.user_id == user_id,
        Folder.parent_id == folder.parent_id,
        Folder.name == new_name,
    ).first()
    if dup:
        return jsonify({"error": "同级文件夹已存在同名"}), 409

    folder.name = new_name
    db.session.commit()
    return jsonify({"message": "重命名成功", "folder": folder.to_dict()})


@folders_bp.route("/<int:folder_id>", methods=["DELETE"])
@jwt_required()
def delete_folder(folder_id):
    """删除文件夹（级联删除子文件夹，文件移至根目录）"""
    user_id = int(get_jwt_identity())
    folder = Folder.query.filter_by(id=folder_id, user_id=user_id).first()
    if not folder:
        return jsonify({"error": "文件夹不存在"}), 404

    # 收集所有子文件夹ID
    def collect_ids(f):
        ids = [f.id]
        for child in f.children.all():
            ids.extend(collect_ids(child))
        return ids

    all_ids = collect_ids(folder)

    # 将受影响文件移至根目录
    from app.models.file import File

    File.query.filter(
        File.user_id == user_id,
        File.folder_id.in_(all_ids),
    ).update({File.folder_id: None}, synchronize_session=False)

    # 删除文件夹
    Folder.query.filter(Folder.id.in_(all_ids)).delete(synchronize_session=False)
    db.session.commit()

    return jsonify({"message": f"已删除文件夹及其 {len(all_ids) - 1} 个子文件夹"})


@folders_bp.route("/<int:folder_id>/files", methods=["GET"])
@jwt_required()
def get_folder_files(folder_id):
    """获取文件夹内的文件"""
    user_id = int(get_jwt_identity())
    folder = Folder.query.filter_by(id=folder_id, user_id=user_id).first()
    if not folder:
        return jsonify({"error": "文件夹不存在"}), 404

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    from app.models.file import File

    pagination = (
        File.query.filter_by(user_id=user_id, folder_id=folder_id)
        .order_by(File.updated_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return jsonify({
        "folder": folder.to_dict(),
        "files": [f.to_dict() for f in pagination.items],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages,
    })

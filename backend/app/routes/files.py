"""文件管理路由"""
import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from .. import db
from ..models.file import FileItem
from ..models.tag import Tag, file_tags

files_bp = Blueprint('files', __name__)


def allowed_file(filename):
    """检查文件类型是否允许"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return ext in current_app.config['ALLOWED_EXTENSIONS']


def generate_unique_filename(original_name):
    """生成唯一文件名"""
    ext = original_name.rsplit('.', 1)[1] if '.' in original_name else ''
    return f"{uuid.uuid4().hex}.{ext}"


@files_bp.route('', methods=['GET'])
@jwt_required()
def list_files():
    """获取文件列表（分页 + 搜索 + 筛选）"""
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)
    search = request.args.get('search', '').strip()
    file_type = request.args.get('file_type', '').strip()
    tag_id = request.args.get('tag_id', type=int)
    favorite = request.args.get('favorite', type=int)
    sort = request.args.get('sort', 'newest')

    query = FileItem.query.filter_by(user_id=user_id)

    if search:
        query = query.filter(
            (FileItem.original_name.contains(search)) |
            (FileItem.description.contains(search))
        )
    if file_type:
        query = query.filter_by(file_type=file_type)
    if tag_id:
        query = query.filter(FileItem.tags.any(Tag.id == tag_id))
    if favorite == 1:
        query = query.filter_by(is_favorite=True)

    # 排序
    sort_map = {
        'newest': FileItem.created_at.desc(),
        'oldest': FileItem.created_at.asc(),
        'name': FileItem.original_name.asc(),
        'size': FileItem.file_size.desc(),
        'views': FileItem.view_count.desc(),
    }
    query = query.order_by(sort_map.get(sort, FileItem.created_at.desc()))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'code': 200,
        'data': {
            'items': [f.to_dict() for f in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages,
        }
    })


@files_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """上传文件"""
    user_id = int(get_jwt_identity())

    if 'file' not in request.files:
        return jsonify({'code': 400, 'msg': '请选择文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 400, 'msg': '请选择文件'}), 400

    if not allowed_file(file.filename):
        return jsonify({'code': 400, 'msg': '不支持的文件类型'}), 400

    original_name = secure_filename(file.filename)
    unique_name = generate_unique_filename(original_name)
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, unique_name)
    file.save(file_path)

    file_size = os.path.getsize(file_path)
    file_type = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else ''
    mime_type = file.content_type or ''

    file_item = FileItem(
        filename=unique_name,
        original_name=original_name,
        file_path=file_path,
        file_size=file_size,
        file_type=file_type,
        mime_type=mime_type,
        user_id=user_id,
    )
    db.session.add(file_item)
    db.session.commit()

    return jsonify({'code': 200, 'msg': '上传成功', 'data': file_item.to_dict()}), 201


@files_bp.route('/<int:file_id>', methods=['GET'])
@jwt_required()
def get_file(file_id):
    """获取文件详情"""
    user_id = int(get_jwt_identity())
    file_item = FileItem.query.filter_by(id=file_id, user_id=user_id).first_or_404()

    # 增加浏览次数
    file_item.view_count += 1
    db.session.commit()

    return jsonify({'code': 200, 'data': file_item.to_dict()})


@files_bp.route('/<int:file_id>/download', methods=['GET'])
@jwt_required()
def download_file(file_id):
    """下载文件"""
    user_id = int(get_jwt_identity())
    file_item = FileItem.query.filter_by(id=file_id, user_id=user_id).first_or_404()

    file_item.download_count += 1
    db.session.commit()

    dir_path = os.path.dirname(file_item.file_path)
    return send_from_directory(
        dir_path, file_item.filename,
        as_attachment=True,
        download_name=file_item.original_name
    )


@files_bp.route('/<int:file_id>', methods=['PUT'])
@jwt_required()
def update_file(file_id):
    """更新文件信息"""
    user_id = int(get_jwt_identity())
    file_item = FileItem.query.filter_by(id=file_id, user_id=user_id).first_or_404()
    data = request.get_json()

    if 'description' in data:
        file_item.description = data['description']
    if 'is_favorite' in data:
        file_item.is_favorite = data['is_favorite']

    db.session.commit()
    return jsonify({'code': 200, 'msg': '更新成功', 'data': file_item.to_dict()})


@files_bp.route('/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    """删除文件"""
    user_id = int(get_jwt_identity())
    file_item = FileItem.query.filter_by(id=file_id, user_id=user_id).first_or_404()

    # 删除物理文件
    if os.path.exists(file_item.file_path):
        os.remove(file_item.file_path)

    db.session.delete(file_item)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '删除成功'})


@files_bp.route('/<int:file_id>/tags', methods=['PUT'])
@jwt_required()
def update_file_tags(file_id):
    """更新文件标签"""
    user_id = int(get_jwt_identity())
    file_item = FileItem.query.filter_by(id=file_id, user_id=user_id).first_or_404()
    data = request.get_json()
    tag_ids = data.get('tag_ids', [])

    tags = Tag.query.filter(Tag.id.in_(tag_ids), Tag.user_id == user_id).all()
    file_item.tags = tags
    db.session.commit()

    return jsonify({'code': 200, 'msg': '标签更新成功', 'data': file_item.to_dict()})


@files_bp.route('/types', methods=['GET'])
@jwt_required()
def file_types():
    """获取用户的文件类型列表"""
    user_id = int(get_jwt_identity())
    types = db.session.query(FileItem.file_type) \
        .filter(FileItem.user_id == user_id, FileItem.file_type != '') \
        .distinct().all()
    return jsonify({'code': 200, 'data': [t[0] for t in types]})

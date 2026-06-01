"""标签管理路由"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models.tag import Tag

tags_bp = Blueprint('tags', __name__)


@tags_bp.route('', methods=['GET'])
@jwt_required()
def list_tags():
    """获取用户的所有标签"""
    user_id = int(get_jwt_identity())
    tags = Tag.query.filter_by(user_id=user_id).order_by(Tag.created_at.desc()).all()
    return jsonify({'code': 200, 'data': [t.to_dict() for t in tags]})


@tags_bp.route('', methods=['POST'])
@jwt_required()
def create_tag():
    """创建标签"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    name = data.get('name', '').strip()
    color = data.get('color', '#409EFF')

    if not name:
        return jsonify({'code': 400, 'msg': '标签名不能为空'}), 400

    existing = Tag.query.filter_by(user_id=user_id, name=name).first()
    if existing:
        return jsonify({'code': 409, 'msg': '标签名已存在', 'data': existing.to_dict()}), 409

    tag = Tag(name=name, color=color, user_id=user_id)
    db.session.add(tag)
    db.session.commit()

    return jsonify({'code': 200, 'msg': '创建成功', 'data': tag.to_dict()}), 201


@tags_bp.route('/<int:tag_id>', methods=['PUT'])
@jwt_required()
def update_tag(tag_id):
    """更新标签"""
    user_id = int(get_jwt_identity())
    tag = Tag.query.filter_by(id=tag_id, user_id=user_id).first_or_404()
    data = request.get_json()

    if 'name' in data:
        name = data['name'].strip()
        if name and name != tag.name:
            existing = Tag.query.filter_by(user_id=user_id, name=name).first()
            if existing:
                return jsonify({'code': 409, 'msg': '标签名已存在'}), 409
            tag.name = name
    if 'color' in data:
        tag.color = data['color']

    db.session.commit()
    return jsonify({'code': 200, 'msg': '更新成功', 'data': tag.to_dict()})


@tags_bp.route('/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def delete_tag(tag_id):
    """删除标签"""
    user_id = int(get_jwt_identity())
    tag = Tag.query.filter_by(id=tag_id, user_id=user_id).first_or_404()

    db.session.delete(tag)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '删除成功'})

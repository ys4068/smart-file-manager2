"""书签管理路由"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models.bookmark import Bookmark
from ..models.tag import Tag

bookmarks_bp = Blueprint('bookmarks', __name__)


@bookmarks_bp.route('', methods=['GET'])
@jwt_required()
def list_bookmarks():
    """获取书签列表（分页 + 搜索 + 筛选）"""
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    tag_id = request.args.get('tag_id', type=int)
    favorite = request.args.get('favorite', type=int)
    sort = request.args.get('sort', 'newest')

    query = Bookmark.query.filter_by(user_id=user_id)

    if search:
        query = query.filter(
            (Bookmark.title.contains(search)) |
            (Bookmark.url.contains(search)) |
            (Bookmark.description.contains(search))
        )
    if category:
        query = query.filter_by(category=category)
    if tag_id:
        query = query.filter(Bookmark.tags.any(Tag.id == tag_id))
    if favorite == 1:
        query = query.filter_by(is_favorite=True)

    sort_map = {
        'newest': Bookmark.created_at.desc(),
        'oldest': Bookmark.created_at.asc(),
        'title': Bookmark.title.asc(),
        'visits': Bookmark.visit_count.desc(),
    }
    query = query.order_by(sort_map.get(sort, Bookmark.created_at.desc()))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'code': 200,
        'data': {
            'items': [b.to_dict() for b in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages,
        }
    })


@bookmarks_bp.route('', methods=['POST'])
@jwt_required()
def create_bookmark():
    """添加书签"""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    title = data.get('title', '').strip()
    url = data.get('url', '').strip()

    if not title or not url:
        return jsonify({'code': 400, 'msg': '标题和URL不能为空'}), 400

    bookmark = Bookmark(
        title=title,
        url=url,
        description=data.get('description', ''),
        category=data.get('category', '未分类'),
        user_id=user_id,
    )
    db.session.add(bookmark)
    db.session.commit()

    return jsonify({'code': 200, 'msg': '添加成功', 'data': bookmark.to_dict()}), 201


@bookmarks_bp.route('/import', methods=['POST'])
@jwt_required()
def import_bookmarks():
    """批量导入书签（浏览器导出的 HTML 格式）"""
    from bs4 import BeautifulSoup
    user_id = int(get_jwt_identity())

    if 'file' not in request.files:
        return jsonify({'code': 400, 'msg': '请上传书签文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 400, 'msg': '请选择文件'}), 400

    try:
        content = file.read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(content, 'html.parser')
        imported = 0

        for link in soup.find_all('a'):
            title = link.get_text(strip=True)
            url = link.get('href', '')
            if title and url:
                # 检查是否已存在
                existing = Bookmark.query.filter_by(user_id=user_id, url=url).first()
                if not existing:
                    bookmark = Bookmark(
                        title=title[:256],
                        url=url[:2048],
                        user_id=user_id,
                    )
                    db.session.add(bookmark)
                    imported += 1

        db.session.commit()
        return jsonify({'code': 200, 'msg': f'成功导入 {imported} 条书签', 'data': {'imported': imported}})
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'导入失败: {str(e)}'}), 500


@bookmarks_bp.route('/<int:bookmark_id>', methods=['GET'])
@jwt_required()
def get_bookmark(bookmark_id):
    """获取书签详情"""
    user_id = int(get_jwt_identity())
    bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=user_id).first_or_404()

    bookmark.visit_count += 1
    bookmark.last_visited = datetime.utcnow()
    db.session.commit()

    return jsonify({'code': 200, 'data': bookmark.to_dict()})


@bookmarks_bp.route('/<int:bookmark_id>', methods=['PUT'])
@jwt_required()
def update_bookmark(bookmark_id):
    """更新书签"""
    user_id = int(get_jwt_identity())
    bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=user_id).first_or_404()
    data = request.get_json()

    for field in ['title', 'url', 'description', 'category']:
        if field in data:
            setattr(bookmark, field, data[field].strip() if isinstance(data[field], str) else data[field])
    if 'is_favorite' in data:
        bookmark.is_favorite = data['is_favorite']

    db.session.commit()
    return jsonify({'code': 200, 'msg': '更新成功', 'data': bookmark.to_dict()})


@bookmarks_bp.route('/<int:bookmark_id>', methods=['DELETE'])
@jwt_required()
def delete_bookmark(bookmark_id):
    """删除书签"""
    user_id = int(get_jwt_identity())
    bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=user_id).first_or_404()

    db.session.delete(bookmark)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '删除成功'})


@bookmarks_bp.route('/<int:bookmark_id>/tags', methods=['PUT'])
@jwt_required()
def update_bookmark_tags(bookmark_id):
    """更新书签标签"""
    user_id = int(get_jwt_identity())
    bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=user_id).first_or_404()
    data = request.get_json()
    tag_ids = data.get('tag_ids', [])

    tags = Tag.query.filter(Tag.id.in_(tag_ids), Tag.user_id == user_id).all()
    bookmark.tags = tags
    db.session.commit()

    return jsonify({'code': 200, 'msg': '标签更新成功', 'data': bookmark.to_dict()})


@bookmarks_bp.route('/categories', methods=['GET'])
@jwt_required()
def categories():
    """获取用户的书签分类列表"""
    user_id = int(get_jwt_identity())
    cats = db.session.query(Bookmark.category) \
        .filter(Bookmark.user_id == user_id) \
        .distinct().all()
    return jsonify({'code': 200, 'data': [c[0] for c in cats]})

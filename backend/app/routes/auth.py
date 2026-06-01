"""认证路由"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
)
from .. import db
from ..models.user import User
from ..models.tag import Tag

auth_bp = Blueprint('auth', __name__)

# 黑名单（生产环境应使用 Redis）
_token_blocklist = set()


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'msg': '请提供注册信息'}), 400

    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'code': 400, 'msg': '用户名、邮箱和密码不能为空'}), 400
    if len(password) < 6:
        return jsonify({'code': 400, 'msg': '密码长度不能少于6位'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'code': 409, 'msg': '用户名已存在'}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({'code': 409, 'msg': '邮箱已被注册'}), 409

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    # 创建默认标签
    default_tags = [
        Tag(name='工作', color='#409EFF', user_id=user.id),
        Tag(name='学习', color='#67C23A', user_id=user.id),
        Tag(name='个人', color='#E6A23C', user_id=user.id),
        Tag(name='重要', color='#F56C6C', user_id=user.id),
    ]
    db.session.add_all(default_tags)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'code': 200,
        'msg': '注册成功',
        'data': {
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token,
        }
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'msg': '请提供登录信息'}), 400

    login_id = data.get('username', '').strip()
    password = data.get('password', '')

    if not login_id or not password:
        return jsonify({'code': 400, 'msg': '用户名和密码不能为空'}), 400

    # 支持用户名或邮箱登录
    user = User.query.filter(
        (User.username == login_id) | (User.email == login_id)
    ).first()

    if not user or not user.check_password(password):
        return jsonify({'code': 401, 'msg': '用户名或密码错误'}), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'code': 200,
        'msg': '登录成功',
        'data': {
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token,
        }
    })


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新令牌"""
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify({'code': 200, 'data': {'access_token': access_token}})


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """退出登录"""
    jti = get_jwt()['jti']
    _token_blocklist.add(jti)
    return jsonify({'code': 200, 'msg': '退出成功'})


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户信息"""
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    return jsonify({'code': 200, 'data': user.to_dict()})


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新用户信息"""
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if 'username' in data:
        username = data['username'].strip()
        if username and username != user.username:
            if User.query.filter_by(username=username).first():
                return jsonify({'code': 409, 'msg': '用户名已存在'}), 409
            user.username = username
    if 'email' in data:
        email = data['email'].strip()
        if email and email != user.email:
            if User.query.filter_by(email=email).first():
                return jsonify({'code': 409, 'msg': '邮箱已被注册'}), 409
            user.email = email
    if 'password' in data:
        if len(data['password']) < 6:
            return jsonify({'code': 400, 'msg': '密码长度不能少于6位'}), 400
        user.set_password(data['password'])
    if 'avatar' in data:
        user.avatar = data['avatar']

    db.session.commit()
    return jsonify({'code': 200, 'msg': '更新成功', 'data': user.to_dict()})

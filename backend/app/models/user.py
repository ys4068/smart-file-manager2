"""用户模型"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar = db.Column(db.String(256), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    files = db.relationship('FileItem', backref='owner', lazy='dynamic',
                            cascade='all, delete-orphan')
    bookmarks = db.relationship('Bookmark', backref='owner', lazy='dynamic',
                                cascade='all, delete-orphan')
    tags = db.relationship('Tag', backref='owner', lazy='dynamic',
                           cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar': self.avatar or '',
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

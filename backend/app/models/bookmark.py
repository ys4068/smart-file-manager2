"""书签模型"""
from datetime import datetime
from .. import db


class Bookmark(db.Model):
    __tablename__ = 'bookmarks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(256), nullable=False)
    url = db.Column(db.String(2048), nullable=False)
    description = db.Column(db.Text, default='')
    favicon = db.Column(db.String(512), default='')
    screenshot = db.Column(db.String(512), default='')
    is_favorite = db.Column(db.Boolean, default=False)
    visit_count = db.Column(db.Integer, default=0)
    category = db.Column(db.String(100), default='未分类')
    last_visited = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # 多对多关系：标签
    tags = db.relationship('Tag', secondary='bookmark_tags', backref='bookmarks', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'description': self.description,
            'favicon': self.favicon,
            'is_favorite': self.is_favorite,
            'visit_count': self.visit_count,
            'category': self.category,
            'last_visited': self.last_visited.isoformat() if self.last_visited else None,
            'tags': [tag.to_dict() for tag in self.tags],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

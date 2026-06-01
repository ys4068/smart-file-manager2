"""标签模型"""
from datetime import datetime
from .. import db

# 多对多中间表
file_tags = db.Table(
    'file_tags',
    db.Column('file_id', db.Integer, db.ForeignKey('files.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
)

bookmark_tags = db.Table(
    'bookmark_tags',
    db.Column('bookmark_id', db.Integer, db.ForeignKey('bookmarks.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
)


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20), default='#409EFF')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'name', name='uq_user_tag_name'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'created_at': self.created_at.isoformat(),
        }

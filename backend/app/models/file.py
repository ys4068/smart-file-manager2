"""文件模型"""
from datetime import datetime
from .. import db


class FileItem(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(256), nullable=False)
    original_name = db.Column(db.String(256), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.BigInteger, default=0)
    file_type = db.Column(db.String(50), default='')
    mime_type = db.Column(db.String(128), default='')
    description = db.Column(db.Text, default='')
    is_favorite = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    download_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # 多对多关系：标签
    tags = db.relationship('Tag', secondary='file_tags', backref='files', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_name': self.original_name,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'mime_type': self.mime_type,
            'description': self.description,
            'is_favorite': self.is_favorite,
            'view_count': self.view_count,
            'download_count': self.download_count,
            'tags': [tag.to_dict() for tag in self.tags],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

import secrets
from app import db


class Folder(db.Model):
    __tablename__ = "folders"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("folders.id"), nullable=True)
    level = db.Column(db.Integer, default=0)  # 深度层级
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    owner = db.relationship("User", backref="folders")

    children = db.relationship(
        "Folder", backref=db.backref("parent", remote_side=[id]), lazy="dynamic"
    )
    files = db.relationship("File", back_populates="folder", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "parent_id": self.parent_id,
            "level": self.level,
            "user_id": self.user_id,
            "file_count": self.files.count(),
            "children_count": self.children.count(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def to_tree(self):
        """递归生成文件夹树"""
        return {
            **self.to_dict(),
            "children": [c.to_tree() for c in self.children.order_by(Folder.name).all()],
        }

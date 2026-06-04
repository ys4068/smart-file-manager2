import uuid
from app import db


class File(db.Model):
    __tablename__ = "files"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(64), unique=True, default=lambda: str(uuid.uuid4()))
    filename = db.Column(db.String(256), nullable=False)
    original_name = db.Column(db.String(256), nullable=False)
    file_size = db.Column(db.BigInteger, default=0)
    file_type = db.Column(db.String(20), nullable=False)  # document, image, video, other
    mime_type = db.Column(db.String(128))
    description = db.Column(db.Text, default="")
    tags = db.Column(db.String(500), default="")  # comma-separated
    category = db.Column(db.String(50), default="未分类")
    download_count = db.Column(db.Integer, default=0)
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    owner = db.relationship("User", back_populates="files")

    def to_dict(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "filename": self.filename,
            "original_name": self.original_name,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "mime_type": self.mime_type,
            "description": self.description,
            "tags": self.tags.split(",") if self.tags else [],
            "category": self.category,
            "download_count": self.download_count,
            "is_favorite": self.is_favorite,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

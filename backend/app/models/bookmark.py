from app import db


class Bookmark(db.Model):
    __tablename__ = "bookmarks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(256), nullable=False)
    url = db.Column(db.String(2048), nullable=False)
    description = db.Column(db.Text, default="")
    tags = db.Column(db.String(500), default="")  # comma-separated
    category = db.Column(db.String(50), default="未分类")
    favicon = db.Column(db.String(512), default="")
    visit_count = db.Column(db.Integer, default=0)
    is_favorite = db.Column(db.Boolean, default=False)
    is_read_later = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    owner = db.relationship("User", back_populates="bookmarks")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "description": self.description,
            "tags": self.tags.split(",") if self.tags else [],
            "category": self.category,
            "favicon": self.favicon,
            "visit_count": self.visit_count,
            "is_favorite": self.is_favorite,
            "is_read_later": self.is_read_later,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

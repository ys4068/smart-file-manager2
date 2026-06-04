import os
import secrets
from app import db
from app.models.file import File, generate_share_token


class FilePermissionService:
    """文件权限管理服务"""

    @staticmethod
    def set_public(file: File, is_public: bool = True):
        """设为公有/私有"""
        file.is_public = is_public
        file.access_level = "public" if is_public else "private"
        if is_public:
            file.share_token = file.share_token or generate_share_token()
        db.session.commit()

    @staticmethod
    def generate_share_link(file: File):
        """生成分享链接"""
        if not file.share_token:
            file.share_token = generate_share_token()
            file.access_level = "shared"
        db.session.commit()
        return file.share_token

    @staticmethod
    def revoke_share(file: File):
        """撤销分享"""
        file.share_token = None
        file.access_level = "private"
        file.is_public = False
        db.session.commit()

    @staticmethod
    def can_access(file: File, user_id: int) -> bool:
        """检查用户是否有权访问"""
        if file.is_public or file.access_level == "public":
            return True
        if file.user_id == user_id:
            return True
        return False

    @staticmethod
    def verify_share_token(file: File, token: str) -> bool:
        """验证分享令牌"""
        return file.share_token is not None and file.share_token == token

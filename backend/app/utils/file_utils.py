import os
import re


class FileUtils:
    """文件工具类"""

    TYPE_MAP = {
        "png": "image", "jpg": "image", "jpeg": "image", "gif": "image",
        "webp": "image", "svg": "image", "bmp": "image",
        "pdf": "document", "doc": "document", "docx": "document",
        "xls": "document", "xlsx": "document", "ppt": "document", "pptx": "document",
        "txt": "document", "md": "document", "csv": "document",
        "mp4": "video", "avi": "video", "mov": "video", "mkv": "video",
        "mp3": "audio", "wav": "audio", "flac": "audio",
        "zip": "archive", "rar": "archive", "7z": "archive", "tar": "archive", "gz": "archive",
    }

    ALLOWED_EXTENSIONS = set(TYPE_MAP.keys()) | {
        "py", "js", "ts", "html", "css", "json", "xml", "yaml", "yml", "sql",
    }

    @classmethod
    def get_file_type(cls, ext: str) -> str:
        return cls.TYPE_MAP.get(ext.lower(), "other")

    @classmethod
    def is_allowed(cls, ext: str) -> bool:
        return ext.lower() in cls.ALLOWED_EXTENSIONS

    @staticmethod
    def format_size(bytes_val: int) -> str:
        if not bytes_val:
            return "0 B"
        units = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(bytes_val)
        while size >= 1024 and i < len(units) - 1:
            size /= 1024
            i += 1
        return f"{size:.1f} {units[i]}"

    @staticmethod
    def safe_filename(filename: str) -> str:
        """安全文件名，移除危险字符"""
        # 保留中文、英文、数字、常用符号
        filename = re.sub(r'[\\/:*?"<>|]', "_", filename)
        return filename.strip()

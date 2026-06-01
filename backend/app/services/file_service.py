"""文件服务层（可扩展的业务逻辑）"""
import os
import magic  # python-magic
from typing import Optional


def detect_mime_type(file_path: str) -> Optional[str]:
    """检测文件的 MIME 类型"""
    try:
        mime = magic.Magic(mime=True)
        return mime.from_file(file_path)
    except Exception:
        return None


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def get_file_icon(file_type: str) -> str:
    """根据文件类型返回图标名称"""
    icon_map = {
        'pdf': 'pdf',
        'doc': 'word', 'docx': 'word',
        'xls': 'excel', 'xlsx': 'excel',
        'ppt': 'powerpoint', 'pptx': 'powerpoint',
        'png': 'image', 'jpg': 'image', 'jpeg': 'image', 'gif': 'image',
        'zip': 'archive', 'rar': 'archive', '7z': 'archive',
        'txt': 'text', 'md': 'text',
        'py': 'code', 'js': 'code', 'html': 'code', 'css': 'code',
        'json': 'code', 'xml': 'code',
        'java': 'code', 'cpp': 'code', 'c': 'code',
    }
    return icon_map.get(file_type, 'file')

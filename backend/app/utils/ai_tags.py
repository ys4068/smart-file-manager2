"""
AI 智能标签服务（预留扩展）

毕设答辩时可以展示：
- 基于文件内容/书签标题自动生成标签
- 可以使用简单的 TF-IDF + 关键词提取
- 或接入大模型 API（如 OpenAI / 文心一言）进行智能分类

当前实现：基于关键词匹配的简单标签建议
"""

import re
from typing import List

# 关键词 -> 标签映射
KEYWORD_TAG_MAP = {
    r'python|flask|django|fastapi|pytorch|tensorflow|numpy|pandas': 'Python',
    r'javascript|js|vue|react|angular|node|typescript|ts|前端|frontend': '前端',
    r'java|spring|maven|gradle|后端|backend': 'Java',
    r'docker|kubernetes|k8s|devops|ci|cd|jenkins|nginx|linux': '运维',
    r'mysql|mongodb|redis|postgresql|sql|数据库|database': '数据库',
    r'设计|design|figma|sketch|ps|photoshop|配色|ui|ux': '设计',
    r'算法|algorithm|leetcode|数据结构|机器学习|深度学习|ai': '算法/AI',
    r'面试|interview|简历|resume|求职': '求职面试',
    r'论文|paper|research|学术|arxiv': '学术研究',
    r'项目|project|开源|github|开源项目': '开源项目',
    r'效率|productivity|工具|tool|效率工具': '效率工具',
    r'读书|阅读|书籍|book|reading': '阅读',
}


def suggest_tags(text: str) -> List[str]:
    """根据文本内容建议标签"""
    text_lower = text.lower()
    suggested = []

    for pattern, tag in KEYWORD_TAG_MAP.items():
        if re.search(pattern, text_lower):
            suggested.append(tag)

    return suggested[:5]  # 最多返回5个

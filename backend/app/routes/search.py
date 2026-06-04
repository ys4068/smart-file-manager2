from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.file import File
from app.models.bookmark import Bookmark

search_bp = Blueprint("search", __name__)


@search_bp.route("", methods=["GET"])
@jwt_required()
def global_search():
    user_id = int(get_jwt_identity())
    keyword = request.args.get("q", "").strip()
    if not keyword:
        return jsonify({"error": "请输入搜索关键词"}), 400

    # Search files
    files = (
        File.query.filter_by(user_id=user_id)
        .filter(
            db.or_(
                File.original_name.ilike(f"%{keyword}%"),
                File.description.ilike(f"%{keyword}%"),
                File.tags.ilike(f"%{keyword}%"),
                File.category.ilike(f"%{keyword}%"),
            )
        )
        .limit(20)
        .all()
    )

    # Search bookmarks
    bookmarks = (
        Bookmark.query.filter_by(user_id=user_id)
        .filter(
            db.or_(
                Bookmark.title.ilike(f"%{keyword}%"),
                Bookmark.url.ilike(f"%{keyword}%"),
                Bookmark.description.ilike(f"%{keyword}%"),
                Bookmark.tags.ilike(f"%{keyword}%"),
                Bookmark.category.ilike(f"%{keyword}%"),
            )
        )
        .limit(20)
        .all()
    )

    return jsonify({
        "keyword": keyword,
        "files": [f.to_dict() for f in files],
        "bookmarks": [b.to_dict() for b in bookmarks],
        "total": len(files) + len(bookmarks),
    })


@search_bp.route("/suggest", methods=["POST"])
@jwt_required()
def smart_suggest():
    """智能分类建议 - 根据文件名/标题推荐分类和标签"""
    import jieba

    data = request.get_json()
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "请输入文本"}), 400

    # 关键词提取
    words = list(jieba.cut(text))
    keywords = [w for w in words if len(w) > 1]

    # 预定义分类规则
    category_rules = {
        "技术文档": ["代码", "编程", "开发", "API", "文档", "技术", "Python", "Java", "前端", "后端", "数据库"],
        "学习资料": ["教程", "学习", "课程", "笔记", "考试", "习题", "讲义", "教材"],
        "图片素材": ["图片", "照片", "截图", "设计", "素材", "logo", "icon", "背景"],
        "音视频": ["视频", "音乐", "录音", "音频", "歌曲", "电影"],
        "个人文档": ["简历", "合同", "证件", "报告", "总结", "计划"],
        "工具软件": ["软件", "工具", "安装包", "插件", "驱动"],
    }

    tag_rules = {
        "代码": ["python", "javascript", "vue", "react", "java", "git", "docker"],
        "文档": ["pdf", "word", "excel", "ppt", "markdown"],
        "设计": ["psd", "sketch", "figma", "ui", "ux"],
    }

    # 匹配分类
    matched_category = "未分类"
    max_score = 0
    for cat, rule_words in category_rules.items():
        score = sum(1 for w in keywords if w in rule_words)
        if score > max_score:
            max_score = score
            matched_category = cat

    # 匹配标签
    suggested_tags = []
    for tag_group, tags in tag_rules.items():
        for t in tags:
            if t.lower() in text.lower() and t not in suggested_tags:
                suggested_tags.append(t)

    # 添加关键词作为标签
    for kw in keywords[:3]:
        if kw.lower() not in suggested_tags:
            suggested_tags.append(kw.lower())

    return jsonify({
        "suggested_category": matched_category,
        "suggested_tags": suggested_tags[:5],
        "keywords": keywords[:10],
    })

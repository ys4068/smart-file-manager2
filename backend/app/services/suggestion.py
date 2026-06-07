"""
智能建议引擎 - URL提取 + 分类推荐 + 标签生成
"""
from urllib.parse import urlparse
import re


# ============================================================
# 域名 → 分类 映射库
# ============================================================
DOMAIN_CATEGORY_MAP = {
    # 技术开发
    "github.com": "技术开发",
    "gitlab.com": "技术开发",
    "gitee.com": "技术开发",
    "stackoverflow.com": "技术开发",
    "stackexchange.com": "技术开发",
    "csdn.net": "技术开发",
    "juejin.cn": "技术开发",
    "segmentfault.com": "技术开发",
    "v2ex.com": "技术开发",
    "infoq.cn": "技术开发",
    "oschina.net": "技术开发",
    "51cto.com": "技术开发",
    "dev.to": "技术开发",
    "hackerrank.com": "技术开发",
    "leetcode.com": "技术开发",
    "leetcode.cn": "技术开发",
    "nowcoder.com": "技术开发",
    "huggingface.co": "技术开发",
    "modelscope.cn": "技术开发",
    "pypi.org": "技术开发",
    "npmjs.com": "技术开发",
    "crates.io": "技术开发",
    "docker.com": "技术开发",
    "hub.docker.com": "技术开发",
    # 文档/教程
    "docs.python.org": "技术文档",
    "developer.mozilla.org": "技术文档",
    "mdn.dev": "技术文档",
    "runoob.com": "技术文档",
    "w3schools.com": "技术文档",
    "w3school.com.cn": "技术文档",
    "tutorialspoint.com": "技术文档",
    "geeksforgeeks.org": "技术文档",
    "postman.com": "技术文档",
    "swagger.io": "技术文档",
    "readthedocs.io": "技术文档",
    "readthedocs.org": "技术文档",
    "devdocs.io": "技术文档",
    "wiki.archlinux.org": "技术文档",
    # 视频平台
    "youtube.com": "音视频",
    "youtu.be": "音视频",
    "bilibili.com": "音视频",
    "b23.tv": "音视频",
    "youku.com": "音视频",
    "iqiyi.com": "音视频",
    "vimeo.com": "音视频",
    "twitch.tv": "音视频",
    "douyin.com": "音视频",
    "tiktok.com": "音视频",
    "netflix.com": "音视频",
    "qq.com/tv": "音视频",
    "v.qq.com": "音视频",
    "music.163.com": "音视频",
    "y.qq.com": "音视频",
    "kugou.com": "音视频",
    "spotify.com": "音视频",
    # 在线教育
    "coursera.org": "学习资料",
    "udemy.com": "学习资料",
    "udacity.com": "学习资料",
    "edx.org": "学习资料",
    "khanacademy.org": "学习资料",
    "xuexi.cn": "学习资料",
    "icourse163.org": "学习资料",
    "xuetangx.com": "学习资料",
    "imooc.com": "学习资料",
    "shiyanlou.com": "学习资料",
    "liaoxuefeng.com": "学习资料",
    "freecodecamp.org": "学习资料",
    "codecademy.com": "学习资料",
    "pluralsight.com": "学习资料",
    # 设计资源
    "dribbble.com": "设计素材",
    "behance.net": "设计素材",
    "figma.com": "设计素材",
    "pinterest.com": "设计素材",
    "zcool.com.cn": "设计素材",
    "huaban.com": "设计素材",
    "unsplash.com": "设计素材",
    "pexels.com": "设计素材",
    "iconfont.cn": "设计素材",
    "flaticon.com": "设计素材",
    "fontawesome.com": "设计素材",
    "canva.com": "设计素材",
    "gaoding.com": "设计素材",
    "sketch.com": "设计素材",
    "invisionapp.com": "设计素材",
    # 工具/协作
    "notion.so": "工具资源",
    "feishu.cn": "工具资源",
    "yuque.com": "工具资源",
    "trello.com": "工具资源",
    "mubu.com": "工具资源",
    "processon.com": "工具资源",
    "draw.io": "工具资源",
    "excalidraw.com": "工具资源",
    "miro.com": "工具资源",
    "figma.com/figjam": "工具资源",
    "aistudio.google.com": "工具资源",
    "colab.research.google.com": "工具资源",
    "replit.com": "工具资源",
    "codesandbox.io": "工具资源",
    "codepen.io": "工具资源",
    "jsfiddle.net": "工具资源",
    # 新闻资讯
    "news.qq.com": "新闻资讯",
    "news.163.com": "新闻资讯",
    "thepaper.cn": "新闻资讯",
    "bbc.com": "新闻资讯",
    "cnn.com": "新闻资讯",
    "reuters.com": "新闻资讯",
    "huxiu.com": "新闻资讯",
    "36kr.com": "新闻资讯",
    "geekpark.net": "新闻资讯",
    "ifanr.com": "新闻资讯",
    "sspai.com": "新闻资讯",
    # 社交媒体
    "twitter.com": "社交网络",
    "x.com": "社交网络",
    "weibo.com": "社交网络",
    "douban.com": "社交网络",
    "reddit.com": "社交网络",
    "zhihu.com": "社交网络",
    "linkedin.com": "社交网络",
    "t.me": "社交网络",
    "discord.com": "社交网络",
    # 购物/电商
    "taobao.com": "购物消费",
    "jd.com": "购物消费",
    "amazon.com": "购物消费",
    "amazon.cn": "购物消费",
    "pinduoduo.com": "购物消费",
    "smzdm.com": "购物消费",
    "aliexpress.com": "购物消费",
    # 学术
    "scholar.google.com": "学术论文",
    "cnki.net": "学术论文",
    "arxiv.org": "学术论文",
    "ieee.org": "学术论文",
    "acm.org": "学术论文",
    "sci-hub.se": "学术论文",
    "sci-hub.ru": "学术论文",
    "nature.com": "学术论文",
    "science.org": "学术论文",
    "springer.com": "学术论文",
    "wiley.com": "学术论文",
    "elsevier.com": "学术论文",
    # AI/大模型
    "chat.openai.com": "AI工具",
    "chatgpt.com": "AI工具",
    "claude.ai": "AI工具",
    "gemini.google.com": "AI工具",
    "bard.google.com": "AI工具",
    "poe.com": "AI工具",
    "copilot.microsoft.com": "AI工具",
    "kimi.moonshot.cn": "AI工具",
    "tongyi.aliyun.com": "AI工具",
    "doubao.com": "AI工具",
    "yiyan.baidu.com": "AI工具",
    "deepseek.com": "AI工具",
    "perplexity.ai": "AI工具",
}

# ============================================================
# 路径关键词 → 标签 映射
# ============================================================
PATH_TAG_MAP = {
    # 编程语言 / 框架
    "python": "python",
    "javascript": "javascript",
    "typescript": "typescript",
    "java": "java",
    "golang": "go",
    "rust": "rust",
    "cpp": "c++",
    "csharp": "c#",
    "ruby": "ruby",
    "php": "php",
    "swift": "swift",
    "kotlin": "kotlin",
    "scala": "scala",
    "vue": "vue",
    "react": "react",
    "angular": "angular",
    "svelte": "svelte",
    "django": "django",
    "flask": "flask",
    "fastapi": "fastapi",
    "spring": "spring",
    "express": "express",
    "nextjs": "next.js",
    "nuxt": "nuxt",
    "nestjs": "nestjs",
    "tensorflow": "tensorflow",
    "pytorch": "pytorch",
    "keras": "keras",
    "docker": "docker",
    "kubernetes": "k8s",
    "nginx": "nginx",
    "linux": "linux",
    "sql": "sql",
    "mysql": "mysql",
    "postgresql": "postgresql",
    "mongodb": "mongodb",
    "redis": "redis",
    "graphql": "graphql",
    "restful": "rest-api",
    "api": "api",
    # 文档 / 格式
    "tutorial": "教程",
    "guide": "教程",
    "doc": "文档",
    "docs": "文档",
    "manual": "手册",
    "reference": "参考",
    "cheatsheet": "速查表",
    "examples": "示例",
    "sample": "示例",
    "quickstart": "快速入门",
    "getting-started": "入门",
    "best-practices": "最佳实践",
    "awesome": "资源合集",
    "roadmap": "路线图",
    "changelog": "更新日志",
    # 设计
    "design": "设计",
    "ui": "UI设计",
    "ux": "UX设计",
    "icon": "图标",
    "font": "字体",
    "color": "配色",
    "template": "模板",
    "wireframe": "线框图",
    "prototype": "原型",
    # 测试/部署
    "testing": "测试",
    "debug": "调试",
    "devops": "devops",
    "ci": "CI/CD",
    "cd": "CI/CD",
    "deploy": "部署",
    "monitoring": "监控",
    # 其他
    "blog": "博客",
    "article": "文章",
    "news": "新闻",
    "video": "视频",
    "podcast": "播客",
    "course": "课程",
    "book": "书籍",
    "paper": "论文",
    "project": "项目",
    "tool": "工具",
    "library": "库",
    "framework": "框架",
    "plugin": "插件",
    "extension": "扩展",
    "opensource": "开源",
    "github": "github",
    "interview": "面试",
    "algorithm": "算法",
    "datastructure": "数据结构",
    "leetcode": "刷题",
    "security": "安全",
    "performance": "性能优化",
}

# 停用词（路径中忽略）
STOP_WORDS = {
    "www", "com", "cn", "org", "net", "io", "html", "htm", "index",
    "page", "pages", "main", "home", "default", "en", "zh", "cn",
    "the", "a", "an", "is", "are", "of", "in", "to", "for", "and",
    "this", "that", "with", "from", "php", "asp", "jsp", "aspx",
    "search", "query", "login", "signin", "signup", "register",
    "about", "contact", "help", "faq", "terms", "privacy",
}


def extract_domain(url: str) -> str:
    """提取纯域名（去掉 www 前缀）"""
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc
    except Exception:
        return ""


def suggest_from_url(url: str) -> dict:
    """
    根据 URL 智能推荐分类和标签

    返回: {"suggested_category": str, "suggested_tags": list[str], "domain": str, "path_keywords": list[str]}
    """
    if not url:
        return {"suggested_category": "未分类", "suggested_tags": [], "domain": "", "path_keywords": []}

    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception:
        return {"suggested_category": "未分类", "suggested_tags": [], "domain": "", "path_keywords": []}

    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]

    # 1. 域名 → 分类
    matched_category = "未分类"
    # 精确匹配
    if domain in DOMAIN_CATEGORY_MAP:
        matched_category = DOMAIN_CATEGORY_MAP[domain]
    else:
        # 模糊匹配：检查子域名
        for known_domain, category in DOMAIN_CATEGORY_MAP.items():
            if domain.endswith("." + known_domain) or domain == known_domain.split("/")[0]:
                matched_category = category
                break
        # 如果还没匹配到，尝试去掉一级子域再匹配
        if matched_category == "未分类":
            parts = domain.split(".")
            if len(parts) >= 3:
                shorter = ".".join(parts[1:])
                if shorter in DOMAIN_CATEGORY_MAP:
                    matched_category = DOMAIN_CATEGORY_MAP[shorter]

    # 2. 路径 → 标签
    path = parsed.path.lower().rstrip("/")
    # 分词：按 / - _ . 分割
    path_tokens = []
    for segment in path.split("/"):
        for token in re.split(r"[-_.]", segment):
            token = token.strip()
            if token and token not in STOP_WORDS and len(token) >= 2:
                path_tokens.append(token)

    suggested_tags = []
    path_keywords = []
    seen_tags = set()
    for token in path_tokens:
        path_keywords.append(token)
        if token in PATH_TAG_MAP and PATH_TAG_MAP[token] not in seen_tags:
            suggested_tags.append(PATH_TAG_MAP[token])
            seen_tags.add(PATH_TAG_MAP[token])
        elif token not in seen_tags and 2 <= len(token) <= 20:
            suggested_tags.append(token)
            seen_tags.add(token)

    # 3. 根据域名补充标签
    domain_tags = {
        "github.com": ["github", "开源"],
        "gitlab.com": ["git", "开源"],
        "gitee.com": ["gitee", "开源"],
        "bilibili.com": ["b站", "视频"],
        "youtube.com": ["youtube", "视频"],
        "zhihu.com": ["知乎"],
        "juejin.cn": ["掘金", "前端"],
        "csdn.net": ["csdn"],
        "stackoverflow.com": ["stackoverflow", "问答"],
    }
    extra_tags = domain_tags.get(domain, [])
    for t in extra_tags:
        if t not in seen_tags:
            suggested_tags.append(t)
            seen_tags.add(t)

    return {
        "suggested_category": matched_category,
        "suggested_tags": suggested_tags[:8],
        "domain": domain,
        "path_keywords": path_keywords[:10],
    }


def suggest(text: str = "", url: str = "") -> dict:
    """
    综合智能建议：支持文本 + URL 双重输入
    """
    result = {
        "suggested_category": "未分类",
        "suggested_tags": [],
        "keywords": [],
        "domain": "",
    }

    # URL 分析
    if url:
        url_result = suggest_from_url(url)
        result["suggested_category"] = url_result["suggested_category"]
        result["suggested_tags"].extend(url_result["suggested_tags"])
        result["domain"] = url_result["domain"]
        result["path_keywords"] = url_result["path_keywords"]

    # 文本分析（jieba 分词）
    if text:
        try:
            import jieba

            words = list(jieba.cut(text))
            keywords = [w for w in words if len(w) > 1]
            result["keywords"] = keywords[:10]

            # 如果 URL 没给出分类，用文本匹配
            if not url or result["suggested_category"] == "未分类":
                cat = _classify_by_text(keywords)
                if cat != "未分类":
                    result["suggested_category"] = cat

            # 把文本关键词补充为标签
            seen = set(result["suggested_tags"])
            for kw in keywords[:5]:
                if kw.lower() not in seen and 2 <= len(kw) <= 15:
                    result["suggested_tags"].append(kw.lower())
                    seen.add(kw.lower())

        except ImportError:
            pass

    # 去重、限制数量
    result["suggested_tags"] = list(dict.fromkeys(result["suggested_tags"]))[:8]
    return result


def _classify_by_text(keywords: list[str]) -> str:
    """基于文本关键词的分类匹配（保留原有的规则引擎增强版）"""
    category_rules = {
        "技术开发": ["代码", "编程", "开发", "API", "接口", "算法", "架构", "运维", "部署",
                    "python", "java", "javascript", "golang", "rust", "react", "vue",
                    "docker", "kubernetes", "linux", "git", "数据库", "后端", "前端",
                    "机器学习", "深度学习", "人工智能", "ai", "模型", "神经网络"],
        "技术文档": ["文档", "手册", "README", "参考", "教程", "指南", "说明", "API文档",
                    "接口文档", "规格", "规范"],
        "学习资料": ["教程", "学习", "课程", "笔记", "考试", "习题", "讲义", "教材",
                    "入门", "进阶", "实战", "练习", "面试", "题目"],
        "设计素材": ["图片", "照片", "截图", "设计", "素材", "logo", "icon", "背景",
                    "ui", "ux", "插画", "图标", "配色", "字体", "海报", "banner"],
        "音视频": ["视频", "音乐", "录音", "音频", "歌曲", "电影", "直播", "播客",
                    "mv", "演唱会", "纪录片", "vlog"],
        "个人文档": ["简历", "合同", "证件", "报告", "总结", "计划", "申请", "证明",
                    "笔记", "日记"],
        "工具资源": ["软件", "工具", "插件", "扩展", "脚本", "自动化", "效率",
                    "实用", "在线工具", "生成器"],
        "学术论文": ["论文", "研究", "学术", "期刊", "文献", "引用", "实验",
                    "博士", "硕士", "学位", "preprint"],
        "新闻资讯": ["新闻", "资讯", "快讯", "日报", "周报", "热点", "头条"],
        "AI工具": ["chatgpt", "ai", "claude", "大模型", "gpt", "llm", "prompt",
                   "对话", "生成", "智能"],
    }

    best_category = "未分类"
    best_score = 0
    for cat, rule_words in category_rules.items():
        score = sum(1 for kw in keywords if kw.lower() in [w.lower() for w in rule_words])
        if score > best_score:
            best_score = score
            best_category = cat

    return best_category

"""书签服务层"""
import re
from urllib.parse import urlparse
from typing import Optional


def extract_domain(url: str) -> str:
    """从 URL 提取域名"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except Exception:
        return ''


def validate_url(url: str) -> bool:
    """验证 URL 格式"""
    pattern = re.compile(
        r'^https?://'
        r'[^\s/$.?#].[^\s]*$',
        re.IGNORECASE
    )
    return bool(pattern.match(url))


def suggest_category(url: str, title: str) -> str:
    """根据 URL 和标题智能建议分类"""
    domain = extract_domain(url).lower()
    title_lower = title.lower()

    category_rules = [
        (['github.com', 'gitlab.com', 'gitee.com', 'stackoverflow.com', 'csdn.net', 'juejin.cn',
          'zhihu.com', 'medium.com', 'dev.to', 'w3schools.com', 'mdn', 'runoob.com'],
         '技术学习'),
        (['bilibili.com', 'youtube.com', 'youku.com', 'douyin.com', 'iqiyi.com',
          'v.qq.com', 'netflix.com', 'spotify.com'],
         '影音娱乐'),
        (['taobao.com', 'jd.com', 'pinduoduo.com', 'amazon.com', 'tmall.com', 'smzdm.com'],
         '购物'),
        (['weibo.com', 'twitter.com', 'facebook.com', 'instagram.com', 'reddit.com',
          'tieba.baidu.com', 'douban.com'],
         '社交'),
        (['mail.google.com', 'mail.qq.com', 'outlook.com', '163.com'],
         '邮箱'),
        (['docs.google.com', 'notion.so', 'yuque.com', 'shimo.im', 'feishu.cn'],
         '文档协作'),
    ]

    for domains, category in category_rules:
        if any(d in domain for d in domains):
            return category

    # 根据标题关键字猜测
    title_keywords = {
        '编程|代码|开发|python|java|算法|前端|后端|api|框架': '技术学习',
        '新闻|资讯|日报|头条': '新闻资讯',
        '设计|ui|ux|配色|字体': '设计资源',
        '工具|在线|转换|生成|格式': '在线工具',
    }
    for keywords, category in title_keywords.items():
        if re.search(keywords, title_lower):
            return category

    return '未分类'

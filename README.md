# 智能文件/书签管理系统

> 毕业设计项目 — 基于 Flask + Vue3 的智能文件与书签管理平台

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus + Pinia |
| 后端 | Python Flask + SQLAlchemy + JWT |
| 数据库 | MySQL |
| 智能功能 | jieba 分词 + 关键词提取 + 智能分类推荐 |

## 功能特性

- 📁 **文件管理** — 上传、下载、分类、标签、搜索、收藏
- 🔖 **书签管理** — 添加、分类、标签、收藏、待读列表
- 🔍 **智能搜索** — 全文检索文件与书签
- 💡 **智能推荐** — 基于关键词自动推荐分类与标签
- 📊 **仪表盘** — 数据统计、类型分布、最近记录
- 🔐 **用户系统** — JWT 注册/登录认证

## 项目结构

```
smart-file-manager/
├── backend/                 # Flask 后端
│   ├── app/
│   │   ├── models/          # 数据模型
│   │   ├── routes/          # API 路由
│   │   ├── config.py        # 配置
│   │   └── __init__.py      # 应用工厂
│   ├── uploads/             # 文件存储
│   ├── requirements.txt
│   └── run.py               # 启动入口
├── frontend/                # Vue3 前端
│   ├── src/
│   │   ├── views/           # 页面组件
│   │   ├── router/          # 路由
│   │   ├── stores/          # Pinia 状态
│   │   ├── api/             # API 封装
│   │   └── assets/          # 静态资源
│   ├── package.json
│   └── vite.config.js
└── database/
    └── init.sql             # 数据库初始化
```

## 快速开始

### 1. 创建数据库

```bash
mysql -u root -p < database/init.sql
```

### 2. 启动后端

```bash
cd backend
cp .env.example .env          # 编辑 .env 填写数据库信息
pip install -r requirements.txt
python run.py
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 注册 |
| POST | /api/auth/login | 登录 |
| GET | /api/auth/me | 获取当前用户 |
| GET | /api/files | 文件列表 |
| POST | /api/files/upload | 上传文件 |
| GET | /api/files/:id/download | 下载文件 |
| PUT | /api/files/:id | 更新文件信息 |
| DELETE | /api/files/:id | 删除文件 |
| GET | /api/bookmarks | 书签列表 |
| POST | /api/bookmarks | 添加书签 |
| PUT | /api/bookmarks/:id | 更新书签 |
| DELETE | /api/bookmarks/:id | 删除书签 |
| POST | /api/bookmarks/:id/visit | 记录访问 |
| GET | /api/search?q= | 全局搜索 |
| POST | /api/search/suggest | 智能建议 |
| GET | /api/dashboard | 仪表盘数据 |

## License

MIT

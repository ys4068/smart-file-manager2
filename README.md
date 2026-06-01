# 📁 智能文件/书签管理系统

> 毕设项目 — 基于 Flask + Vue3 + MySQL 的个人知识管理平台

## 🎯 功能特性

### 文件管理
- 📤 多格式文件上传（支持 30+ 文件类型）
- 🔍 全文搜索、按类型/标签/收藏筛选
- 📥 文件下载（记录下载次数）
- ⭐ 收藏夹 & 浏览统计
- 🏷️ 多标签分类

### 书签管理
- 🔗 手动添加书签（智能分类建议）
- 📥 浏览器书签 HTML 导入
- 🔍 多维度搜索（标题/URL/描述）
- 📊 访问统计
- 🏷️ 多标签 & 分类管理

### 标签系统
- 🎨 自定义标签颜色
- 📎 文件和书签共用标签
- 🔗 多对多关联

### 数据面板
- 📊 存储空间统计
- 📈 文件类型分布
- 🏷️ 热门标签排行

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Python 3.10 + Flask 3.0 |
| 数据库 | MySQL 8.0 + SQLAlchemy |
| 认证 | JWT (Flask-JWT-Extended) |
| 前端框架 | Vue 3 + Vite |
| UI 组件库 | Element Plus |
| 状态管理 | Pinia |
| 路由 | Vue Router 4 |

## 📦 项目结构

```
smart-file-bookmark-manager/
├── backend/                 # Flask 后端
│   ├── app/
│   │   ├── models/         # 数据模型 (User, File, Bookmark, Tag)
│   │   ├── routes/         # API 路由 (auth/files/bookmarks/tags/stats)
│   │   ├── services/       # 业务逻辑 (文件处理/书签智能分类)
│   │   ├── utils/          # 工具 (AI 标签建议)
│   │   └── config.py       # 配置
│   ├── migrations/         # 数据库迁移
│   ├── requirements.txt
│   └── run.py              # 入口
├── frontend/               # Vue3 前端
│   ├── src/
│   │   ├── api/            # API 请求封装
│   │   ├── components/     # 公共组件
│   │   ├── views/          # 页面 (Dashboard/Files/Bookmarks/Tags)
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # Pinia 状态
│   │   └── assets/         # 样式资源
│   ├── package.json
│   └── vite.config.js      # Vite 配置 (含 API 代理)
├── database/
│   └── init.sql            # 数据库初始化脚本
└── docs/
    └── 毕设说明.md
```

## 🚀 快速启动

### 1. 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0+

### 2. 数据库配置

```bash
# 创建数据库
mysql -u root -p < database/init.sql
```

### 3. 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，修改数据库密码等

# 启动（开发模式）
python run.py
# 访问 http://localhost:5000
```

### 4. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
# 访问 http://localhost:5173
```

### 5. 生产部署

```bash
# 构建前端
cd frontend && npm run build

# 后端使用 gunicorn
cd backend && gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## 📡 API 路由一览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 |
| GET | `/api/auth/profile` | 获取用户信息 |
| GET | `/api/files` | 文件列表（分页+搜索） |
| POST | `/api/files/upload` | 上传文件 |
| GET | `/api/files/:id/download` | 下载文件 |
| DELETE | `/api/files/:id` | 删除文件 |
| GET | `/api/bookmarks` | 书签列表 |
| POST | `/api/bookmarks` | 添加书签 |
| POST | `/api/bookmarks/import` | 导入书签 |
| GET/POST/PUT/DELETE | `/api/tags` | 标签 CRUD |
| GET | `/api/stats/dashboard` | 仪表盘统计 |

## 👤 作者

- GitHub: [ys4068](https://github.com/ys4068)
- 邮箱: ys4068@gmail.com

## 📄 许可

MIT License — 仅供学习交流

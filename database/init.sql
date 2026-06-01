-- ============================================
-- 智能文件/书签管理系统 - 数据库初始化脚本
-- 数据库: MySQL 5.7+
-- ============================================

CREATE DATABASE IF NOT EXISTS smart_file_manager
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE smart_file_manager;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    avatar VARCHAR(256) DEFAULT '',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 标签表
CREATE TABLE IF NOT EXISTS tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(20) DEFAULT '#409EFF',
    user_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uq_user_tag_name (user_id, name),
    INDEX idx_tag_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 文件表
CREATE TABLE IF NOT EXISTS files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(256) NOT NULL,
    original_name VARCHAR(256) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    file_size BIGINT DEFAULT 0,
    file_type VARCHAR(50) DEFAULT '',
    mime_type VARCHAR(128) DEFAULT '',
    description TEXT,
    is_favorite TINYINT(1) DEFAULT 0,
    view_count INT DEFAULT 0,
    download_count INT DEFAULT 0,
    user_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_file_user (user_id),
    INDEX idx_file_type (file_type),
    INDEX idx_file_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 书签表
CREATE TABLE IF NOT EXISTS bookmarks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(256) NOT NULL,
    url VARCHAR(2048) NOT NULL,
    description TEXT,
    favicon VARCHAR(512) DEFAULT '',
    screenshot VARCHAR(512) DEFAULT '',
    is_favorite TINYINT(1) DEFAULT 0,
    visit_count INT DEFAULT 0,
    category VARCHAR(100) DEFAULT '未分类',
    last_visited DATETIME,
    user_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_bookmark_user (user_id),
    INDEX idx_bookmark_category (category),
    INDEX idx_bookmark_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 文件-标签中间表
CREATE TABLE IF NOT EXISTS file_tags (
    file_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (file_id, tag_id),
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 书签-标签中间表
CREATE TABLE IF NOT EXISTS bookmark_tags (
    bookmark_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (bookmark_id, tag_id),
    FOREIGN KEY (bookmark_id) REFERENCES bookmarks(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

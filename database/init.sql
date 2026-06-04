CREATE DATABASE IF NOT EXISTS smart_file_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smart_file_manager;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    avatar VARCHAR(256),
    created_at DATETIME,
    updated_at DATETIME,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS folders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    parent_id INT,
    level INT DEFAULT 0,
    created_at DATETIME,
    updated_at DATETIME,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES folders(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_parent_id (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(64) NOT NULL UNIQUE,
    filename VARCHAR(256) NOT NULL,
    original_name VARCHAR(256) NOT NULL,
    file_size BIGINT DEFAULT 0,
    file_type VARCHAR(20) NOT NULL,
    mime_type VARCHAR(128),
    description TEXT,
    tags VARCHAR(500),
    category VARCHAR(50),
    download_count INT DEFAULT 0,
    is_favorite TINYINT(1) DEFAULT 0,
    is_public TINYINT(1) DEFAULT 0,
    share_token VARCHAR(64) UNIQUE,
    access_level VARCHAR(16) DEFAULT 'private',
    folder_id INT,
    created_at DATETIME,
    updated_at DATETIME,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_category (category),
    INDEX idx_folder_id (folder_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS bookmarks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(256) NOT NULL,
    url VARCHAR(2048) NOT NULL,
    description TEXT,
    tags VARCHAR(500),
    category VARCHAR(50),
    favicon VARCHAR(512),
    visit_count INT DEFAULT 0,
    is_favorite TINYINT(1) DEFAULT 0,
    is_read_later TINYINT(1) DEFAULT 0,
    created_at DATETIME,
    updated_at DATETIME,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

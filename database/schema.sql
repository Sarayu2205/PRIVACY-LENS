-- PrivacyLens Database Schema
-- MySQL 8.0+
-- Run: mysql -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS privacylens CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE privacylens;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(120) NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active   TINYINT(1) NOT NULL DEFAULT 1,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_email (email)
) ENGINE=InnoDB;

-- Scans table
CREATE TABLE IF NOT EXISTS scans (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id         INT UNSIGNED NOT NULL,
    file_name       VARCHAR(255) NOT NULL,
    scan_type       ENUM('file','text') NOT NULL DEFAULT 'file',
    risk_score      FLOAT NOT NULL DEFAULT 0,
    risk_level      ENUM('LOW','MEDIUM','HIGH','CRITICAL') NOT NULL DEFAULT 'LOW',
    finding_count   INT NOT NULL DEFAULT 0,
    categories      JSON,
    is_masked       TINYINT(1) NOT NULL DEFAULT 0,
    scan_date       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_scans_user (user_id),
    INDEX idx_scans_date (scan_date)
) ENGINE=InnoDB;

-- Findings table
CREATE TABLE IF NOT EXISTS findings (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    scan_id         INT UNSIGNED NOT NULL,
    type            VARCHAR(50) NOT NULL,
    masked_value    VARCHAR(500),
    confidence      FLOAT NOT NULL DEFAULT 0,
    location        VARCHAR(100),
    severity        ENUM('LOW','MEDIUM','HIGH','CRITICAL') NOT NULL DEFAULT 'LOW',
    context_snippet VARCHAR(500),
    FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE,
    INDEX idx_findings_scan (scan_id),
    INDEX idx_findings_type (type)
) ENGINE=InnoDB;

-- Reports table
CREATE TABLE IF NOT EXISTS reports (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    scan_id     INT UNSIGNED NOT NULL UNIQUE,
    file_path   VARCHAR(500) NOT NULL,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE
) ENGINE=InnoDB;

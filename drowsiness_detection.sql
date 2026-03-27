-- phpMyAdmin SQL Dump
-- Drowsiness Detection Database
-- Version: 1.0
-- Generated: March 9, 2026

-- Create Database
CREATE DATABASE IF NOT EXISTS `drowsiness_detection` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `drowsiness_detection`;

-- Drop table if exists
DROP TABLE IF EXISTS `users`;
DROP TABLE IF EXISTS `drowsiness_history`;

-- Create users table
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `last_login` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create drowsiness history table
CREATE TABLE `drowsiness_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `duration` int(11) DEFAULT 0,
  `severity` varchar(20) DEFAULT 'low',
  `ear_value` decimal(5,4) DEFAULT 0.0000,
  `alert_triggered` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `drowsiness_history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default admin user (optional)
-- Username: admin
-- Password: admin123 (change this immediately!)
INSERT INTO `users` (`id`, `username`, `password`, `created_at`) 
VALUES (1, 'admin', 'admin123', NOW());

-- Grant privileges (adjust as needed)
-- GRANT ALL PRIVILEGES ON drowsiness_detection.* TO 'your_username'@'localhost' IDENTIFIED BY 'your_password';
-- FLUSH PRIVILEGES;

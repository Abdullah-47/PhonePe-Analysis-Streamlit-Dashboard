-- Drop database if exists (use with caution in production)
DROP DATABASE IF EXISTS `test_db`;
CREATE DATABASE `test_db`;
USE `test_db`;

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS `aggregated_user_device`;
DROP TABLE IF EXISTS `top_user`;
DROP TABLE IF EXISTS `top_insurance`;
DROP TABLE IF EXISTS `top_transaction`;
DROP TABLE IF EXISTS `aggregated_user`;
DROP TABLE IF EXISTS `aggregated_insurance`;
DROP TABLE IF EXISTS `aggregated_transaction`;
DROP TABLE IF EXISTS `map_user_hover`;
DROP TABLE IF EXISTS `map_insurance_hover`;
DROP TABLE IF EXISTS `map_transaction_hover`;

-- Create tables
CREATE TABLE `map_transaction_hover` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `year` INT,
    `quarter` INT,
    `name` VARCHAR(100),
    `metric_type` VARCHAR(50),
    `count` BIGINT,
    `amount` DOUBLE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `map_insurance_hover` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `year` INT,
    `quarter` INT,
    `name` VARCHAR(100),
    `metric_type` VARCHAR(50),
    `count` BIGINT,
    `amount` DOUBLE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `map_user_hover` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `year` INT,
    `quarter` INT,
    `name` VARCHAR(100),
    `registered_users` BIGINT,
    `app_opens` BIGINT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `aggregated_transaction` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `year` INT,
    `quarter` INT,
    `from_ts` BIGINT,
    `to_ts` BIGINT,
    `category` VARCHAR(100),
    `instrument_type` VARCHAR(50),
    `count` BIGINT,
    `amount` DOUBLE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `aggregated_insurance` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `year` INT,
    `quarter` INT,
    `from_ts` BIGINT,
    `to_ts` BIGINT,
    `category` VARCHAR(100),
    `instrument_type` VARCHAR(50),
    `count` BIGINT,
    `amount` DOUBLE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `aggregated_user` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `year` INT,
    `quarter` INT,
    `registered_users` BIGINT,
    `app_opens` BIGINT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `aggregated_user_device` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT,
    `brand` VARCHAR(100),
    `count` BIGINT,
    `percentage` DOUBLE,
    FOREIGN KEY (`user_id`) REFERENCES `aggregated_user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `top_transaction` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `year` INT,
    `quarter` INT,
    `entity_level` ENUM('state', 'district', 'pincode'),
    `entity_name` VARCHAR(100),
    `metric_type` VARCHAR(20),
    `count` BIGINT,
    `amount` DOUBLE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `top_insurance` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `year` INT,
    `quarter` INT,
    `entity_level` ENUM('state', 'district', 'pincode'),
    `entity_name` VARCHAR(100),
    `metric_type` VARCHAR(20),
    `count` BIGINT,
    `amount` DOUBLE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `top_user` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `year` INT,
    `quarter` INT,
    `entity_level` ENUM('state', 'district', 'pincode'),
    `entity_name` VARCHAR(100),
    `registered_users` BIGINT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
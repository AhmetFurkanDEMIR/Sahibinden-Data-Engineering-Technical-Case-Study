CREATE DATABASE IF NOT EXISTS testdb;
USE testdb;

ALTER DATABASE testdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sahibinden (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    price INT NOT NULL,
    seller VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS sahibinden_target_table (
    id INT PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    price INT,
    seller VARCHAR(255),
    created_at DATETIME
);

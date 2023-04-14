CREATE USER 'spip'@'localhost' IDENTIFIED BY 'password';
CREATE DATABASE IF NOT EXISTS spip CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
GRANT ALL PRIVILEGES ON spip.* TO 'spip'@'localhost';
FLUSH PRIVILEGES;

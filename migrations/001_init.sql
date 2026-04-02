-- MySQL: инициализация схемы под текущие SQLModel-модели приложения
-- Запускать на пустой (или заранее очищенной) базе.

SET NAMES utf8mb4;

-- users
CREATE TABLE IF NOT EXISTS `users` (
  `id_user` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NULL,
  `surname` VARCHAR(100) NULL,
  `age` INT NULL,
  `email` VARCHAR(255) NOT NULL,
  `hashed_pass` VARCHAR(255) NOT NULL,
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `is_admin` TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id_user`),
  UNIQUE KEY `uq_users_email` (`email`),
  KEY `idx_users_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- hall
CREATE TABLE IF NOT EXISTS `hall` (
  `id_hall` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(200) NOT NULL,
  `address` VARCHAR(255) NULL,
  `phone` VARCHAR(50) NOT NULL,
  `seatsAmount` INT NULL,
  PRIMARY KEY (`id_hall`),
  KEY `idx_hall_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- tickettypes
CREATE TABLE IF NOT EXISTS `tickettypes` (
  `id_type` INT NOT NULL AUTO_INCREMENT,
  `type` VARCHAR(200) NOT NULL,
  PRIMARY KEY (`id_type`),
  KEY `idx_tickettypes_type` (`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- genre
CREATE TABLE IF NOT EXISTS `genre` (
  `id_genre` INT NOT NULL AUTO_INCREMENT,
  `genre_name` VARCHAR(200) NOT NULL,
  PRIMARY KEY (`id_genre`),
  KEY `idx_genre_name` (`genre_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- musicgroups
CREATE TABLE IF NOT EXISTS `musicgroups` (
  `id_group` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(200) NOT NULL,
  `albumCount` INT NOT NULL DEFAULT 0,
  `site` VARCHAR(255) NOT NULL,
  `id_genre` INT NOT NULL,
  PRIMARY KEY (`id_group`),
  KEY `idx_musicgroups_genre` (`id_genre`),
  CONSTRAINT `fk_musicgroups_genre`
    FOREIGN KEY (`id_genre`) REFERENCES `genre` (`id_genre`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- concert
CREATE TABLE IF NOT EXISTS `concert` (
  `id_concert` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `date` DATETIME NOT NULL,
  `description` TEXT NULL,
  `sales_paused` TINYINT(1) NOT NULL DEFAULT 0,
  `id_hall` INT NULL,
  PRIMARY KEY (`id_concert`),
  KEY `idx_concert_name` (`name`),
  KEY `idx_concert_date` (`date`),
  CONSTRAINT `fk_concert_hall`
    FOREIGN KEY (`id_hall`) REFERENCES `hall` (`id_hall`)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- hall_zone
CREATE TABLE IF NOT EXISTS `hall_zone` (
  `id_hall_zone` INT NOT NULL AUTO_INCREMENT,
  `amount` INT NOT NULL,
  `id_hall` INT NOT NULL,
  `id_type` INT NOT NULL,
  PRIMARY KEY (`id_hall_zone`),
  KEY `idx_hall_zone_hall` (`id_hall`),
  KEY `idx_hall_zone_type` (`id_type`),
  CONSTRAINT `fk_hall_zone_hall`
    FOREIGN KEY (`id_hall`) REFERENCES `hall` (`id_hall`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_hall_zone_type`
    FOREIGN KEY (`id_type`) REFERENCES `tickettypes` (`id_type`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- tickets
CREATE TABLE IF NOT EXISTS `tickets` (
  `id_ticket` INT NOT NULL AUTO_INCREMENT,
  `id_concert` INT NOT NULL,
  `id_hall_zone` INT NOT NULL,
  `price` INT NOT NULL,
  `remains` INT NOT NULL,
  PRIMARY KEY (`id_ticket`),
  KEY `idx_tickets_concert` (`id_concert`),
  KEY `idx_tickets_hall_zone` (`id_hall_zone`),
  CONSTRAINT `fk_tickets_concert`
    FOREIGN KEY (`id_concert`) REFERENCES `concert` (`id_concert`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_tickets_hall_zone`
    FOREIGN KEY (`id_hall_zone`) REFERENCES `hall_zone` (`id_hall_zone`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- sales
CREATE TABLE IF NOT EXISTS `sales` (
  `id_sale` INT NOT NULL AUTO_INCREMENT,
  `id_user` INT NOT NULL,
  `id_ticket` INT NOT NULL,
  `count` INT NOT NULL DEFAULT 1,
  `total_price` INT NOT NULL DEFAULT 0,
  `sale_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_sale`),
  KEY `idx_sales_user` (`id_user`),
  KEY `idx_sales_ticket` (`id_ticket`),
  CONSTRAINT `fk_sales_user`
    FOREIGN KEY (`id_user`) REFERENCES `users` (`id_user`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_sales_ticket`
    FOREIGN KEY (`id_ticket`) REFERENCES `tickets` (`id_ticket`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- watchlist
CREATE TABLE IF NOT EXISTS `watchlist` (
  `id_watch` INT NOT NULL AUTO_INCREMENT,
  `id_user` INT NOT NULL,
  `id_concert` INT NOT NULL,
  PRIMARY KEY (`id_watch`),
  UNIQUE KEY `uq_watch_user_concert` (`id_user`, `id_concert`),
  KEY `idx_watch_user` (`id_user`),
  KEY `idx_watch_concert` (`id_concert`),
  CONSTRAINT `fk_watch_user`
    FOREIGN KEY (`id_user`) REFERENCES `users` (`id_user`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_watch_concert`
    FOREIGN KEY (`id_concert`) REFERENCES `concert` (`id_concert`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


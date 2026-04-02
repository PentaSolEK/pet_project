-- MySQL: добавление полей для веб-интерфейса (если таблица concert уже существует без них)

-- Описание
SET @has_description := (
  SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'concert'
    AND COLUMN_NAME = 'description'
);
SET @sql := IF(@has_description = 0,
  'ALTER TABLE concert ADD COLUMN description TEXT NULL',
  'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Пауза продаж
SET @has_sales_paused := (
  SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'concert'
    AND COLUMN_NAME = 'sales_paused'
);
SET @sql := IF(@has_sales_paused = 0,
  'ALTER TABLE concert ADD COLUMN sales_paused TINYINT(1) NOT NULL DEFAULT 0',
  'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

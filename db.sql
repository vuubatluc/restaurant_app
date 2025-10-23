-- MySQL schema for Restaurant Order Manager
-- Contains tables, triggers, and stored procedures.

DROP DATABASE IF EXISTS restaurant_app;
CREATE DATABASE restaurant_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE restaurant_app;

CREATE TABLE categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE menu_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  category_id INT,
  price DECIMAL(12,2) NOT NULL,
  is_available TINYINT(1) NOT NULL DEFAULT 1,
  description TEXT,
  CONSTRAINT fk_menu_cat FOREIGN KEY (category_id) REFERENCES categories(id)
    ON UPDATE RESTRICT ON DELETE SET NULL
);

CREATE TABLE dining_tables (
  id INT AUTO_INCREMENT PRIMARY KEY,
  label VARCHAR(255) NOT NULL UNIQUE,
  seats INT DEFAULT 4
);

CREATE TABLE orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  table_id INT,
  created_at DATETIME NOT NULL,
  subtotal DECIMAL(14,2) NOT NULL DEFAULT 0,
  tax DECIMAL(14,2) NOT NULL DEFAULT 0,
  service DECIMAL(14,2) NOT NULL DEFAULT 0,
  total DECIMAL(14,2) NOT NULL DEFAULT 0,
  status ENUM('OPEN','PAID','CANCELLED') NOT NULL,
  note TEXT,
  CONSTRAINT fk_orders_table FOREIGN KEY (table_id) REFERENCES dining_tables(id)
    ON UPDATE RESTRICT ON DELETE SET NULL
);

CREATE TABLE order_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT NOT NULL,
  item_id INT NOT NULL,
  item_name VARCHAR(255) NOT NULL,
  quantity INT NOT NULL,
  unit_price DECIMAL(12,2) NOT NULL,
  line_total DECIMAL(14,2) NOT NULL DEFAULT 0,
  CONSTRAINT fk_oi_order FOREIGN KEY (order_id) REFERENCES orders(id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_oi_item FOREIGN KEY (item_id) REFERENCES menu_items(id)
    ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE TABLE settings (
  `key` VARCHAR(64) PRIMARY KEY,
  `value` VARCHAR(128)
);

CREATE TABLE order_audit(
  id INT AUTO_INCREMENT PRIMARY KEY,
  action VARCHAR(64) NOT NULL,
  order_id INT NOT NULL,
  changed_at DATETIME NOT NULL,
  note TEXT
);

-- Default data
INSERT INTO settings(`key`,`value`) VALUES ('tax_rate','0.10')
  ON DUPLICATE KEY UPDATE value=VALUES(value);
INSERT INTO settings(`key`,`value`) VALUES ('service_rate','0.05')
  ON DUPLICATE KEY UPDATE value=VALUES(value);

INSERT INTO categories(name) VALUES ('Khai vị'),('Món chính'),('Đồ uống'),('Tráng miệng')
  ON DUPLICATE KEY UPDATE name=VALUES(name);

INSERT INTO dining_tables(label, seats)
SELECT CONCAT('Bàn ', n), 4
FROM (
  SELECT 1 AS n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
  UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10
) AS t
ON DUPLICATE KEY UPDATE seats=VALUES(seats);

INSERT INTO menu_items(name, category_id, price, is_available)
SELECT 'Gỏi cuốn tôm', c.id, 35000, 1 FROM categories c WHERE c.name='Khai vị'
UNION ALL SELECT 'Chả giò', c.id, 40000, 1 FROM categories c WHERE c.name='Khai vị'
UNION ALL SELECT 'Bò lúc lắc', c.id, 120000, 1 FROM categories c WHERE c.name='Món chính'
UNION ALL SELECT 'Cơm gà xối mỡ', c.id, 70000, 1 FROM categories c WHERE c.name='Món chính'
UNION ALL SELECT 'Phở bò tái', c.id, 65000, 1 FROM categories c WHERE c.name='Món chính'
UNION ALL SELECT 'Nước cam', c.id, 30000, 1 FROM categories c WHERE c.name='Đồ uống'
UNION ALL SELECT 'Trà chanh', c.id, 20000, 1 FROM categories c WHERE c.name='Đồ uống'
UNION ALL SELECT 'Bánh flan', c.id, 25000, 1 FROM categories c WHERE c.name='Tráng miệng';

-- Triggers and Procedures
DELIMITER $$

CREATE TRIGGER bi_menu_items_price
BEFORE INSERT ON menu_items
FOR EACH ROW
BEGIN
  IF NEW.price < 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Giá phải >= 0';
  END IF;
END$$

CREATE TRIGGER bu_menu_items_price
BEFORE UPDATE ON menu_items
FOR EACH ROW
BEGIN
  IF NEW.price < 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Giá phải >= 0';
  END IF;
END$$

CREATE TRIGGER bi_order_items_guard
BEFORE INSERT ON order_items
FOR EACH ROW
BEGIN
  IF NEW.quantity <= 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Số lượng phải > 0';
  END IF;
  IF NEW.unit_price < 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Đơn giá phải >= 0';
  END IF;
END$$

CREATE TRIGGER bu_order_items_guard
BEFORE UPDATE ON order_items
FOR EACH ROW
BEGIN
  IF NEW.quantity <= 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Số lượng phải > 0';
  END IF;
  IF NEW.unit_price < 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Đơn giá phải >= 0';
  END IF;
END$$

-- Fix 1442 by computing line_total in BEFORE triggers instead of updating same table in AFTER triggers
CREATE TRIGGER bi_order_items_calc_line_total
BEFORE INSERT ON order_items
FOR EACH ROW
BEGIN
  SET NEW.line_total = NEW.quantity * NEW.unit_price;
END$$

CREATE TRIGGER bu_order_items_calc_line_total
BEFORE UPDATE ON order_items
FOR EACH ROW
BEGIN
  SET NEW.line_total = NEW.quantity * NEW.unit_price;
END$$

CREATE PROCEDURE sp_recalc_order_totals(IN p_order_id INT)
BEGIN
  DECLARE v_sub DECIMAL(14,2);
  DECLARE v_tax_rate DECIMAL(8,4);
  DECLARE v_service_rate DECIMAL(8,4);

  SELECT IFNULL(SUM(line_total),0) INTO v_sub FROM order_items WHERE order_id=p_order_id;
  SELECT CAST(value AS DECIMAL(8,4)) INTO v_tax_rate FROM settings WHERE `key`='tax_rate';
  SELECT CAST(value AS DECIMAL(8,4)) INTO v_service_rate FROM settings WHERE `key`='service_rate';

  UPDATE orders
  SET subtotal=v_sub,
      tax=v_sub*v_tax_rate,
      service=v_sub*v_service_rate,
      total=v_sub + v_sub*v_tax_rate + v_sub*v_service_rate
  WHERE id=p_order_id;
END$$

CREATE TRIGGER ai_order_items_recalc
AFTER INSERT ON order_items
FOR EACH ROW
BEGIN
  CALL sp_recalc_order_totals(NEW.order_id);
END$$

CREATE TRIGGER au_order_items_recalc
AFTER UPDATE ON order_items
FOR EACH ROW
BEGIN
  CALL sp_recalc_order_totals(NEW.order_id);
END$$

CREATE TRIGGER ad_order_items_recalc
AFTER DELETE ON order_items
FOR EACH ROW
BEGIN
  CALL sp_recalc_order_totals(OLD.order_id);
END$$

-- Removed discount trigger as discount feature is deprecated

CREATE TRIGGER au_orders_status_audit
AFTER UPDATE ON orders
FOR EACH ROW
BEGIN
  IF NEW.status <> OLD.status THEN
    INSERT INTO order_audit(action, order_id, changed_at, note)
    VALUES ('STATUS_CHANGED', NEW.id, NOW(), NEW.status);
  END IF;
END$$

CREATE PROCEDURE sp_revenue_by_month(IN p_year INT, IN p_month INT)
BEGIN
  SELECT DATE(created_at) AS ngay,
         COUNT(*) AS so_don,
         SUM(subtotal) AS subtotal,
         SUM(tax) AS tax,
         SUM(service) AS service,
         SUM(total) AS total
  FROM orders
  WHERE status='PAID'
    AND YEAR(created_at)=p_year AND MONTH(created_at)=p_month
  GROUP BY DATE(created_at)
  ORDER BY DATE(created_at);
END$$

-- Optional: daily revenue procedure aligned with app (no discount)
CREATE PROCEDURE sp_revenue_by_date(IN p_date DATE)
BEGIN
  -- Totals row
  SELECT DATE(created_at) AS ngay,
         COUNT(*) AS so_don,
         SUM(subtotal) AS subtotal,
         SUM(tax) AS tax,
         SUM(service) AS service,
         SUM(total) AS total
  FROM orders
  WHERE DATE(created_at)=p_date AND status='PAID';

  -- Detail rows
  SELECT id AS order_id, created_at, table_id, subtotal, tax, service, total
  FROM orders
  WHERE DATE(created_at)=p_date AND status='PAID'
  ORDER BY created_at;
END$$
DELIMITER ;

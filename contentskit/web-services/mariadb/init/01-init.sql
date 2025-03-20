-- WordPress 사용자 추가
CREATE USER IF NOT EXISTS 'wordpress'@'%' IDENTIFIED BY 'wordpress123';
GRANT ALL PRIVILEGES ON wordpress.* TO 'wordpress'@'%';

-- 건강 체크용 사용자 추가
CREATE USER IF NOT EXISTS 'healthchecker'@'localhost' IDENTIFIED BY 'healthcheckpass';
GRANT USAGE ON *.* TO 'healthchecker'@'localhost';

FLUSH PRIVILEGES; 
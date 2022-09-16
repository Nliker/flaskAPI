## mysql 명령어

### 실행
cd /usr/local/mysql/bin
./mysql -u codakcodak -p 
비밀번호 입력

### 테이블 조회
SHOW DATABASES;DESC slow_log;  
(생성되어있는 DATABASE를 조회한다.)
SELECT DATABASE(); 
(현재 사용중인 DATABASE를 확인한다.) 
SHOW TABLES;  
DESC slow_log;  
### 테이블 선택
USE test;  
### READ 
SELECT
    id,
    name,
    age,
    gender
FROM users 
WHERE name="서정현"

### CREATE
INSERT INTO users (
    id,
    name,
    age,
    gender
) VALUES(
    1,
    "서정현",
    26
    "남자"
),(
    2,
    "한상욱",
    26
    "남자"
)

### UPDATE

UPDATE users SET age=25 WHERE name="서정현"

### DELETE 
DELETE FROM users WHERE age <20

### JOIN
SELETE 
    users.name,
    user_address.address
FROM users
JOIN user_address ON users.id=user_address.user_id

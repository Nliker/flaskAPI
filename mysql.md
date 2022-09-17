## mysql 명령어

### 실행
cd /usr/local/mysql/bin
./mysql -u codakcodak -p 
비밀번호 입력

### 테이블 조회
SHOW DATABASES;
(생성되어있는 DATABASE를 조회한다.)
SELECT DATABASE(); 
(현재 사용중인 DATABASE를 확인한다.) 
SHOW TABLES;  
DESC slow_log;  

## 데이터베이스 선택
CREATE DATABASE miniter;

### 데이터베이스 선택
USE test; 

### 컬럼 추가
ALTER TABLE `테이블명` ADD `새컬럼명` 자료형 FIRST

### 컬럼 삭제
ALTER TABLE table name
DROP COLUMN column name

### unique 속성추가
alter table users add email unique;

### foreign key 속성 추가
alter table users_follow_list add constraint users_follow_list_follow_user_id_fkey foreign key(follow_user_id) references users(id);
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

### NOT NULL + DEFAULT
NOT NULL만 있는 경우: NULL을 직접 입력하든, 아무 것도 입력하지 않아서 NULL 값이 넘어가든 두 경우에 대해서 모두 오류를 생성한다.

DEFAULT만 있는 경우: 사용자가 값을 입력하지 않는 경우에 알아서 해당 칼럼에 값을 부여한다. 만약 사용자가 NULL을 입력한다고 해도, 값을 입력한 것으로 보기 때문에, DEFAULT는 활성화되지 않는다.

NOT NULL, DEFAULT 모두 있는 경우: 둘다 있는 경우에는 사용자가 값을 입력하지 않는 경우에는 알아서 DEFAULT가 활성화되고, NULL을 입력하는 경우 NOT NULL이 활성화되어 오류가 발생하게 됩니다.

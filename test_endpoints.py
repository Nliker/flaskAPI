import config

from sqlalchemy import create_engine,text

#config.py 의 변수를 불러올땐 .을 이용한다!
print(config.test)

database=create_engine(config.test_config['DB_URL'],encoding='utf-8',max_overflow=9)
print("DB 연결성공")



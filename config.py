db={
    "user":"root",
    "password":"dkdrmaghEl83!",
    "host":"localhost",
    "port":3306,
    "database":"miniter"
}
JWT_SECRET_KEY="codak"

DB_URL=f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"
test="andg"
test_db={
    'user':'codakcodak',
    'password':'dkdrmaghEl83!',
    'host':'localhost',
    'port':3307,
    'database':'test_miniter'
}
test_config={
    'DB_URL':f"mysql+mysqlconnector://{test_db['user']}:{test_db['password']}@{test_db['host']}:{test_db['port']}/{test_db['database']}?charset=utf8"
}
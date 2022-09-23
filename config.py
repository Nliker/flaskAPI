db={
    "user":"root",
    "password":"dkdrmaghEl83!",
    "host":"localhost",
    "port":3306,
    "database":"miniter"
}
JWT_SECRET_KEY="codak"

DB_URL=f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"

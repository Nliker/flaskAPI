from flask import Flask,jsonify,request,current_app
from sqlalchemy import create_engine,text

def create_app(test_config=None):
    app=Flask(__name__)
    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.update(test_config)
        
    database=create_engine(app.config['DB_URL'],encoding='utf-8',max_overflow=0)
    print("DB 연결 성공!")
    app.database=database
    
    @app.route("/sign-up",methods=["POST"])
    def sign_up():
        new_user=request.json
        new_user_id=app.database.execute(text("""
            insert into users(
                name,
                email,
                profile,
                hashed_password
            ) values(
                :name,
                :email,
                :profile,
                :password
            )
            """),new_user). lastrowid
        
        print("id:",new_user_id)

        row=app.database.execute(text("""
            select 
                id,
                name,
                email,
                profile
            from users
            where id=:user_id
            """),{'user_id':new_user_id}).fetchone()

        created_user={
            'id':row['id'],
            'name':row['name'],
            'email':row['email'],
            'profile':row['profile']
        } if row else None
        
        return jsonify(created_user)
    @app.route("/tweet",methods=["POST"])
    def tweet():
        user_tweet=request.json
        tweet=user_tweet[tweet]
        if len(tweet)>300:
            return "300자를 초과하였습니다.",400
        app.database.execute(test("""
            insert into tweets(
                tweet,
                user_id
            ) values(
                :tweet,
                :user_id
            )
            """),user_tweet)
        return '트윗성공',200
    return app
    
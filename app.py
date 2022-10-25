from flask import Flask,jsonify,request,current_app,g
from sqlalchemy import create_engine,text
from sqlalchemy.exc import IntegrityError
from collections import deque
import bcrypt
import jwt
from functools import wraps
from datetime import datetime, timedelta

jwtExpireTime=  timedelta(seconds=60)

def insert_user(user):
    
    return current_app.database.execute(text("""
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
            """),user).lastrowid

def get_user(user_id):
    #select 는 해당 조건에 만족하는 데이터가 없으면 none으로 준다!
    user=current_app.database.execute(text("""
            select 
                id,
                name,
                email,
                profile
            from users
            where id=:user_id
            """),{'user_id':user_id}).fetchone()
    ## 출력에 불필요한 요소들은 없애기 위해 직접 하나하나 뽑아서 객체로 만든다.
    user={
            'id':user['id'],
            'name':user['name'],
            'email':user['email'],
            'profile':user['profile']
        } if user else None
    return user
    
def insert_tweet(user_tweet):
    return current_app.database.execute(text("""
            insert into tweets(
                tweet,
                user_id
            ) values(
                :tweet,
                :id
            )
            """),user_tweet).rowcount

def get_timeline(user_id):
    rows=current_app.database.execute(text("""
            select t.user_id,
            t.tweet
            from tweets as t
            left join users_follow_list ufl on ufl.user_id=:user_id
            where t.user_id=:user_id
            or t.user_id=ufl.follow_user_id
            """),{'user_id':user_id}).fetchall()
    print(rows)
    data=[  {"tweet":row['tweet'], "user_id":row['user_id']} for row in rows]

    data=deque(data)
    sub=deque()
    
    for tweet in data:
        if tweet not in sub:
            sub.append(tweet)
        else:
            continue
    data=list(sub)
    
    return jsonify({
            'user_id':user_id,
            'timeline':data
        })
    
def insert_follow(payload):
        result=current_app.database.execute(text("""
                insert into users_follow_list(
                    user_id,
                    follow_user_id
                ) values(
                    :user_id,
                    :follow_user_id
                )
            """),{'user_id':payload['id'],'follow_user_id':payload['follow']})
        return result.rowcount
 
def insert_unfollow(payload):
    result=current_app.database.execute(text("""
        delete from users_follow_list
        where user_id=:user_id and follow_user_id=:unfollow_user_id
    """),{'user_id':payload['id'],'unfollow_user_id':payload['unfollow']})
    return result.rowcount

def get_user_id_and_password(email):
    row=current_app.database.execute(text("""
        select id,hashed_password
        from users
        where email=:email                          
    """),{"email":email}).fetchone()
    return {"id":row['id'],"hashed_password":row['hashed_password']} if row else None


def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kargs):
        access_token=request.headers.get('Authorization')
        if access_token is not None:
            print(access_token)
            try:
                payload=jwt.decode(access_token,current_app.config['JWT_SECRET_KEY'],'HS256')
                print(payload['iat'])
                print(datetime.fromtimestamp(payload['iat']))
            except:
                return jsonify({"message":"유효하지 않은 토큰이거나 토큰 검증과정에서 에러가 났습니다."}),404
            if 'user_id' in payload and payload['user_id'] is not None:
                user_id=payload['user_id']
                g.user_id=user_id
                user=get_user(user_id)
                if user is not None:
                    g.user=user
                else:
                    return ({"message":"해당 유저를 찾을 수 없습니다."}),404
            else:
                return jsonify({"message":"필수정보가 없는 토큰입니다."}),401
                
        else:
            return jsonify({"message":"토큰이 없습니다."}),401
        print("================")
        print(g)
        return f(*args,**kargs)
    return decorated_function

def create_app(test_config=None):
    app=Flask(__name__)

    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.update(test_config)
    
    database=create_engine(app.config['DB_URL'],encoding='utf-8',max_overflow=0)
    print("app과 DB 연결 성공!")
    app.database=database
    
    # @app.errorhandler(404)
    # def error_handling_404(error):
    #     return jsonify({'result':'duplicated'}),400   

    @app.route("/ping",methods=["GET"])
    def ping():
        return jsonify({'data':"pong"})
    
    @app.route("/sign-up",methods=["POST"])
    def sign_up():
        new_user=request.json
        new_user['password']=bcrypt.hashpw(new_user['password'].encode('UTF-8'),bcrypt.gensalt())
        print(new_user['password'])
        new_user_id=insert_user(new_user)  
        print("id:",new_user_id)
        new_user=get_user(new_user_id)
        
        return jsonify(new_user)
    
    @app.route("/",methods=["GET"])
    def default():
        return "Welcome To codacodak's miniter"
    
    @app.route("/tweet",methods=["POST"])
    @login_required
    def tweet():    
        user_tweet=request.json
        tweet=user_tweet['tweet']
        user_tweet['id']=g.user_id
        
        if len(tweet)>300:
            return "300자를 초과하였습니다.",400
        
        result=insert_tweet(user_tweet)
        print(result)
        
        return '트윗성공',200
    
    @app.route("/timeline/<int:user_id>",methods=["GET"])
    def timeline(user_id):
        return get_timeline(user_id)
    
    @app.route("/test/<int:user_id>",methods=["GET"])
    def test(user_id):
        row=app.database.execute(text("""
            select email,id
            from users
            where id=:user_id
        """),{'user_id':user_id}).fetchone()
        if row is not None:
            data={'email':row['email'],'user_id':row['id']}
            return jsonify(data)
        else:
            message={"message":"해당 유저를 찾을 수 없습니다."}
            return jsonify(message),404
    
    
    @app.route("/user/<int:user_id>",methods=["GET"])
    def getInfo(user_id):
        row=get_user(user_id)
        print(row)
        print(type(row))
        return jsonify(row)
    
    @app.route("/follow",methods=["POST"])
    @login_required
    def follow():
        payload=request.json
        payload['id']=g.user_id
        try:
           insert_follow(payload)
           return "저장성공",200
        except IntegrityError as e: 
            return jsonify({"message":"pri중복"}),402
    
    @app.route("/unfollow",methods=["POST"])
    @login_required
    def unfollow():
        payload=request.json
        payload['id']=g.user_id
        result=insert_unfollow(payload)
        print(result)
        
        return "저장성공",200
        
    @app.route("/login",methods=["GET","POST"])
    def login():
        credential=request.json
        user_credential=get_user_id_and_password(credential['email'])
        if user_credential and bcrypt.checkpw(credential['password'].encode('UTF-8'),user_credential['hashed_password'].encode('UTF-8')):
            print('비밀번호 일치')
            user_id=user_credential['id']
            payload={
                'user_id':user_id,
                'exp':datetime.utcnow()+jwtExpireTime,
                'iat':datetime.utcnow()
            }
            print(payload)
            token=jwt.encode(payload,app.config['JWT_SECRET_KEY'],'HS256')
            return jsonify({'access_token':token})
        elif user_credential is None:
            return jsonify({"message":"해당 이메일의 유저는 이미 삭제되었습니다."}),404
        else:
            return jsonify({"message":"비밀번호가 일치하지 않습니다."}),404
    return app
    
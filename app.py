from flask import Flask,jsonify,request,current_app,g
from sqlalchemy import create_engine,text
from sqlalchemy.exc import IntegrityError
from collections import deque
import bcrypt
import jwt
from functools import wraps

def insert_user(user):
    user['password']=bcrypt.hashpw(user['password'].encode('UTF-8'),bcrypt.gensalt())
    
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
    created_user={
            'id':user['id'],
            'name':user['name'],
            'email':user['email'],
            'profile':user['profile']
        } if user else None
    return created_user
    
def insert_tweet(user_tweet):
    current_app.database.execute(text("""
            insert into tweets(
                tweet,
                user_id
            ) values(
                :tweet,
                :id
            )
            """),user_tweet)

def get_timeline(user_id):
    rows=current_app.database.execute(text("""
            select t.user_id,
            t.tweet
            from tweets as t
            left join users_follow_list ufl on ufl.user_id=:user_id
            where t.user_id=:user_id
            or t.user_id=ufl.follow_user_id
            """),{'user_id':user_id}).fetchall()
    data=[ {"tweet":row['tweet'],"user_id":row['user_id']} for row in rows]
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

def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kargs):
        access_token=request.headers.get('Authorization')
        if access_token is not None:
            print(access_token)
            try:
                payload=jwt.decode(access_token,current_app.config['JWT_SECRET_KEY'],'HS256')
            except:
                return jsonify({"message":"유효하지 않은 토큰이거나 토큰 검증과정에서 에러가 났습니다."}),404
            user_id=payload['user_id']
            g.user_id=user_id
            
            g.user=get_user(user_id) if user_id else None
                
        else:
            return jsonify({"message":"토큰이 없습니다."}),401
        return f(*args,**kargs)
    return decorated_function

def create_app(test_config=None):
    app=Flask(__name__)

    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.update(test_config)
    
    database=create_engine(app.config['DB_URL'],encoding='utf-8',max_overflow=0)
    print("DB 연결 성공!")
    app.database=database
    
    @app.errorhandler(404)
    def error_handling_404(error):
        return jsonify({'result':'duplicated'}),400   

    @app.route("/sign-up",methods=["POST"])
    def sign_up():
        new_user=request.json
        new_user_id=insert_user(new_user)  
        print("id:",new_user_id)
        new_user=get_user(new_user_id)
        
        return jsonify(new_user)
    
    @app.route("/tweet",methods=["POST"])
    @login_required
    def tweet():    
        user_tweet=request.json
        tweet=user_tweet['tweet']
        user_tweet['id']=g.user_id
        
        if len(tweet)>300:
            return "300자를 초과하였습니다.",400
        
        insert_tweet(user_tweet)
        return '트윗성공',200
    
    @app.route("/timeline/<int:user_id>",methods=["GET"])
    def timeline(user_id):
        return get_timeline(user_id)
    
    @app.route("/test/<int:user_id>",methods=["GET"])
    def test(user_id):
        rows=app.database.execute(text("""
            select u.id,
            u.email
            from users as u
            left join tweets as t on t.user_id=:user_id
            where u.id=:user_id
        """),{'user_id':user_id}).fetchall()
        data=[ {"email":row['email'],"user_id":row['id']} for row in rows]
        return jsonify({'datas':data})
    
    @app.route("/follow",methods=["POST"])
    def follow():
        payload=request.json
        try:
           insert_follow(payload)
           return "저장성공",200
        except IntegrityError as e: 
            return jsonify({"message":"pri중복"}),402
    
    @app.route("/unfollow",methods=["POST"])
    def unfollow():
        payload=request.json
        insert_unfollow(payload)
        return "저장성공",200
        
    @app.route("/login",methods=["GET","POST"])
    def login():
        credential=request.json

        email=credential['email']
        password=credential['password']
        
        row=app.database.execute(text("""
            select id,hashed_password
            from users
            where email=:email                
        """),{'email':email}).fetchone()
        
        if row and bcrypt.checkpw(password.encode('UTF-8'),row['hashed_password'].encode('UTF-8')):
            user_id=row['id']
            payload={
                'user_id':user_id,
                # 'exp':datetime.utcnow()+timedelta(seconds=60*60*24)
            }
            token=jwt.encode(payload,app.config['JWT_SECRET_KEY'],'HS256')
            return jsonify({'access_token':token})
        else:
            return '',401
    return app
    
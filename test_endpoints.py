import config
from app import create_app
from sqlalchemy import create_engine,text
import pytest
import json
import bcrypt

message="im testing"
#config.py 의 변수를 불러올땐 .을 이용한다!
print(config.test)

database=create_engine(config.test_config['DB_URL'],encoding='utf-8',max_overflow=9)
print("DB 연결성공")


@pytest.fixture
def api():
    app=create_app(config.test_config)
    app.config['TEST']=True
    api=app.test_client()
    
    return api

def setup_function():
    print("======setup function======")
    print("데이터베이스 저장중")
    hashed_password1=bcrypt.hashpw(
        b"test1password",
        bcrypt.gensalt()
    )
    hashed_password2=bcrypt.hashpw(
        b"test2password",
        bcrypt.gensalt()
    )
    new_users={
        'id' :1,
        'name':'test1',
        'email':'test1@naver.com',
        'profile':'testuser1',
        'hashed_password':hashed_password1
    },{
        'id' :2,
        'name':'test2',
        'email':'test2@naver.com',
        'profile':'testuser2',
        'hashed_password':hashed_password2
    }
    
    database.execute(text("""
        insert into users (
            id,name,email,profile,hashed_password
        ) values(
            :id,:name,:email,:profile,:hashed_password
        )
    """),new_users)
    database.execute(text("""
        insert into tweets (
            user_id,tweet 
        ) value (
            :user_id,:tweet
        )
    """),{'user_id':2,'tweet':"im testing a tweet"})
    print("데이터베이스 저장성공!!!")
    print("==========================")
    
    
def teardown_function():
    print("======teardown_function======")
    print("테이블 삭초기화중")
    database.execute(text("""
        set foreign_key_checks=0
    """))
    database.execute(text("""
        truncate users
    """))
    database.execute(text("""
        truncate tweets
    """))
    database.execute(text("""
        truncate users_follow_list
    """))
    database.execute(text("""
        set foreign_key_checks=1
    """))
    print("테이블 초기화 완료!!!")
    print("==========================")
    
def test_ping(api):
    resp=api.get('/ping')
    print("ASdasdasd")
    print(resp.data)
    assert b'pong' in resp.data
    
def test_tweet(api):
    resp=api.post(
        '/login',
        data=json.dumps({'email':'test1@naver.com','password':"test1password"}),
        content_type='application/json'
    )
    
    assert resp.status_code==200
    
    #웹에서 받아온 데이터들은 utf-8모드로 인코딩 된 상태로 온다.
    resp_json=json.loads(resp.data.decode('utf-8'))

    access_token=resp_json['access_token']

    resp=api.post(
        '/tweet',
        data=json.dumps({'tweet':message}),
        content_type='application/json',
        headers={'Authorization':access_token}
    )
    
    assert resp.status_code==200
    
    resp= api.get(f'/timeline/1')
    tweets=json.loads(resp.data.decode('utf-8'))

    assert resp.status_code==200
    
    assert tweets =={
        'user_id':1,
        'timeline':[
            {
                'user_id':1,
                'tweet':message
            }
        ]
    }
    
def test_login(api):
    resp=api.post('/login',
        data=json.dumps({'email':'test1@naver.com','password':'test1password'}),
        content_type='application/json'
    )
    assert resp.status_code ==200
    assert 'access_token' in json.loads(resp.data.decode('utf-8'))
    
def test_unauthorized(api):
    resp=api.post('/tweet',
        data=json.dumps({'tweet':'this test tweet'}),
        content_type='application/json'
    )
    
    assert resp.status_code ==401 

    resp=api.post('/follow',
        data=json.dumps({'follow':2}),
        content_type='application/json'
    )
    
    assert resp.status_code==401
    
    resp=api.post('/unfollow',
        data=json.dumps({'unfollow':2}),
        content_type='application/json'
    )
    
    assert resp.status_code==401

def test_follow(api):
    resp=api.post('/login',
        data=json.dumps({'email':'test1@naver.com','password':'test1password'}),
        content_type='application/json'
    )
    
    assert resp.status_code==200
    resp_json=json.loads(resp.data.decode('utf-8'))
    access_token=resp_json['access_token']

    resp=api.get('/timeline/1')
    assert resp.status_code==200
    
    tweets=json.loads(resp.data.decode('utf-8'))
    assert tweets=={
        'user_id':1,
        'timeline':[]
    }

    resp=api.post('/follow',
        data=json.dumps({'follow':2}),
        content_type='application/json',
        headers={'Authorization':access_token}
    )
    
    assert resp.status_code==200

    resp=api.get('/timeline/1')
    tweets=json.loads(resp.data.decode('utf-8'))
    assert resp.status_code==200
    assert tweets=={
        'user_id':1,
        'timeline':[
            {
                'user_id':2,
                'tweet':'im testing a tweet'
            }
        ]
    }

def test_unfollow(api):
    resp=api.post('/login',
        data=json.dumps({'email':'test1@naver.com','password':'test1password'}),
        content_type='application/json'
    )
    
    assert resp.status_code==200
    resp_json=json.loads(resp.data.decode('utf-8'))
    access_token=resp_json['access_token']

    resp=api.post('/follow',
        data=json.dumps({'follow':2}),
        content_type='application/json',
        headers={'Authorization':access_token}
    )
    
    assert resp.status_code==200

    resp=api.get('/timeline/1')
    
    assert resp.status_code==200
    tweets=json.loads(resp.data.decode('utf-8'))
    assert tweets=={
        'user_id':1,
        'timeline':[
            {
                'user_id':2,
                'tweet':'im testing a tweet'
            }
        ]
    }
    
    resp=api.post('/unfollow',
        data=json.dumps({'unfollow':2}),
        content_type='application/json',
        headers={'Authorization':access_token}
    )
    assert resp.status_code==200
    
    resp=api.get('/timeline/1')
    assert resp.status_code==200
    tweets=json.loads(resp.data.decode('utf-8'))
    assert tweets=={
        'user_id':1,
        'timeline':[]
    }

    
    

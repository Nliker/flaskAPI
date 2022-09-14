from flask import Flask,jsonify,request
from flask.json import JSONEncoder

app=Flask(__name__)

class CustomJSONEncoder(JSONEncoder):
    def default(self,obj):
        if isinstance(obj,set):
            return list(obj)
        
        return JSONEncoder.default(self,obj)
app.json_encoder=CustomJSONEncoder


app.users={}
app.id_count=1
app.tweets=[]

@app.route("/ping",methods=["GET"])
def ping():
    return "pong" 

@app.route("/sign-up",methods=["POST"])
def sign_up():
    new_user=request.json   
    print(new_user["nick"])
    new_user["id"]=app.id_count
    app.users[app.id_count]=new_user
    print(app.users)
    app.id_count=app.id_count+1
    
    return jsonify(new_user)


@app.route("/tweet",methods=["POST"])
def tweet():
    payload=request.json
    user_id=int(payload["id"])
    tweet=payload["tweet"]
    
    if user_id not in app.users:
        return "사용자가 존재하지않습니다.",400
    if len(tweet)>300:
        return "글자수 제한을 초과하였습니다,",400
    app.tweets.append({
        "user_id":user_id,
        "tweet":tweet
    })
    print(app.tweets)
    return '',200
    
@app.route("/follow",methods=["POST"])
def follow():
    payload=request.json
    user_id=int(payload["id"])
    follow_id=int(payload["follow"])
    if user_id not in app.users or follow_id not in app.users:
        return "사용자가 존재하지 않습니다.",400
    
    user=app.users[user_id]
    user.setdefault("follow",set()).add(follow_id)
    print(app.users)
    return jsonify(user),200

@app.route("/unfollow",methods=["POST"])
def unfollow():
    payload=request.json
    user_id=int(payload["id"])
    unfollow_id=int(payload["unfollow"])
    
    if user_id not in app.users or unfollow_id not in app.users:
        return "사용자가 존재하지 않습니다.",400

    user=app.users[user_id]
    user.setdefault("follow",set()).discard(unfollow_id)
    
    return jsonify(user),200

@app.route("/user/<int:id>",methods=["GET"])
def user(id):
    if id not in app.users:
        return "사용자를 찾을수가 없습니다.",400
    user=app.users[id]
    
    return jsonify(user),200
    
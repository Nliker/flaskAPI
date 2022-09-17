from flask import Flask,jsonify,request
from sqlalchemy import create_engine,text

def create_app(test_config=None):
    app=Flask(__name__)
    if test_config is None:
        app.config.from_pyfile("confi.py")
    else:
        app.config.update(test_config)
        
    database=create_engine(app.config['DB_URL'],encoding='utf-8',max_overflow=0)
    app.database=database
    
    return app

@app.route("/sign-up",methods=["POST"])
def sign_up():
    new_user=request.json
    new_user_id=app.database.execute(text)
    
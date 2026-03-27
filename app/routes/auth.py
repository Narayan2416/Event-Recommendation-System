import os
from flask import Flask,jsonify,request,render_template,redirect,url_for,session, Blueprint
from db.data_base import user_insert,user_exists,get_userid
from google.oauth2 import id_token
from google.auth.transport import requests
from dotenv import load_dotenv

load_dotenv()

bp = Blueprint("auth", __name__)

CLIENT_ID = os.getenv("CLIENT_ID")


@bp.route("/",methods=['GET','POST'])
def home():
    if request.method=='POST':
        name=request.form.get('username')
        email=request.form.get('email')
        uid=get_userid(name,email)
        if(uid is None):
            return render_template("home.html", error="User not found",CLIENT_ID=CLIENT_ID)
        if(user_exists(uid)):
            session['uid'] = uid
            return redirect(url_for("search",uid=session['uid']))
        else:
            return render_template("home.html", error="Sign In Required",CLIENT_ID=CLIENT_ID)
    return render_template("home.html",CLIENT_ID=CLIENT_ID)


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    token = data["token"]
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            CLIENT_ID
        )

        email = idinfo["email"]
        name = idinfo["name"]
        uid = idinfo["sub"]
        if not user_exists(uid):
            user_insert(uid,name, email)
        session["uid"] = uid
        return jsonify({
            "success": True,
            "email": email,
            "name": name,
            "uid": uid
        })
    except ValueError:
        return jsonify({"success": False})
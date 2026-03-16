import os
from flask import Flask,jsonify,request,render_template,redirect,url_for,session
from data_base import user_insert, load_data,get_event,save_search,save_user_interaction,get_clicked_events,user_exists,get_userid
from recommendation import recommend_by_query,recommend_similar_event,recommend_based_on_prevSearches,recommend_based_on_user_interaction,popular_event_list
from scrappers.scrapper2 import add_new_Event
import time
from google.oauth2 import id_token
from google.auth.transport import requests
from dotenv import load_dotenv

load_dotenv()

app=Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
CLIENT_ID = os.getenv("CLIENT_ID")

# home-------------------------------------------------------------------------

@app.route("/",methods=['GET','POST'])
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


@app.route("/login", methods=["POST"])
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

# helper routes-----------------------------------------------------------------

@app.route("/load_data")
def load_data_route():
    data = load_data()
    #print(data[14])
    return jsonify(data)

@app.route("/<uid>/clicked_event/<event_id>", methods=['GET','POST'])
def clicked_event(uid, event_id):
    save_user_interaction(uid, event_id, action="click")
    return redirect(get_event(event_id)['url'])

@app.route("/api/recommendation", methods=['GET','POST'])
def api_recommendation():
    uid = session.get('uid')
    if uid is None:
        return jsonify({"error": "User ID is required"}), 400
    st=time.time()
    rec_search=recommend_based_on_prevSearches(uid)
    rec_interaction=recommend_based_on_user_interaction(uid)
    #print(rec_interaction[0])
    rec_popular=popular_event_list()
    #print(f"Recommendation time: {time.time() - st} seconds")
    return jsonify({"searches": rec_search, "interests": rec_interaction, "popular": rec_popular})

# main pages---------------------------------------------------------------------

@app.route("/admin", methods=['GET','POST'])
def admin():
    return render_template("admin.html")

@app.route("/admin/add_event",methods=['GET','POST'])
def add_event():
    events=[]
    if request.method == 'POST':
        events=add_new_Event()
        return redirect(url_for("add_event"),events=events)
    return render_template("add_event.html", events=events) #admin adding event page

@app.route("/<uid>/search",methods=['GET','POST'])
def search(uid):
    return render_template("search.html",uid=uid)

@app.route("/semantic_search", methods=['POST'])
def semantic_search():
    query=request.json.get('query', '')
    if not query:
        return jsonify([])
    save_search(session['uid'], query)
    results = recommend_by_query(query, 100)
    return jsonify(results)

@app.route("/<uid>/event/<event_id>", methods=['GET'])
def event_details(uid, event_id):
    # Fetch user-specific events from the database
    event = get_event(event_id)
    save_user_interaction(uid, event_id,action="view")
    suggestions = recommend_similar_event(event_id)
    return render_template("event_details.html",uid=uid, event=event, suggestions=suggestions)

@app.route("/<uid>/recommender",methods=['GET','POST'])
def recommender(uid):
    return render_template("recommender.html",uid=uid)

@app.route("/<uid>/view", methods=['GET'])
def view(uid):
    clicked_events = get_clicked_events(uid)   
    return render_template("my_events.html", uid=uid, my_events=clicked_events)

app.run(debug=True)

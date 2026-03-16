from flask import Flask,jsonify,request,render_template,redirect,url_for,session
from data_base import user_insert, load_data,get_event,save_search,save_user_interaction,get_clicked_events,user_exists
from recommendation import recommend_by_query,recommend_similar_event,recommend_based_on_prevSearches,recommend_based_on_user_interaction,popular_event_list
from scrappers.scrapper2 import add_new_Event
import time
from google.oauth2 import id_token
from google.auth.transport import requests

app=Flask(__name__)
app.secret_key = "my_secret_key"
CLIENT_ID = "738347502101-dspntc69nqd1s1hevolbpgivlc5bttso.apps.googleusercontent.com"

# home-------------------------------------------------------------------------

@app.route("/",methods=['GET','POST'])
def home():
    if request.method=='POST':
        name=request.form.get('username')
        email=request.form.get('email')
        if(user_exists(name,email)):
            session['username'] = name
            return redirect(url_for("search",username=name))
        else:
            return render_template("home.html", error="Sign In Required")
    return render_template("home.html")


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
        user_insert(name, email)
        return jsonify({
            "success": True,
            "email": email,
            "name": name
        })
    except ValueError:
        return jsonify({"success": False})

# helper routes-----------------------------------------------------------------

@app.route("/load_data")
def load_data_route():
    data = load_data()
    #print(data[14])
    return jsonify(data)

@app.route("/<username>/clicked_event/<event_id>", methods=['GET','POST'])
def clicked_event(username, event_id):
    save_user_interaction(username, event_id, action="click")
    return redirect(get_event(event_id)['url'])

@app.route("/api/recommendation", methods=['GET','POST'])
def api_recommendation():
    username = session['username']
    if not username:
        return jsonify({"error": "Username is required"}), 400
    st=time.time()
    rec_search=recommend_based_on_prevSearches(username)
    rec_interaction=recommend_based_on_user_interaction(username)
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

@app.route("/<username>/search",methods=['GET','POST'])
def search(username):
    return render_template("search.html",username=username)

@app.route("/semantic_search", methods=['POST'])
def semantic_search():
    query=request.json.get('query', '')
    if not query:
        return jsonify([])
    save_search(session['username'], query)
    results = recommend_by_query(query, 100)
    return jsonify(results)

@app.route("/<username>/event/<event_id>", methods=['GET'])
def event_details(username, event_id):
    # Fetch user-specific events from the database
    event = get_event(event_id)
    save_user_interaction(session['username'], event_id,action="view")
    suggestions = recommend_similar_event(event_id)
    return render_template("event_details.html",username=username, event=event, suggestions=suggestions)

@app.route("/<username>/recommender",methods=['GET','POST'])
def recommender(username):
    return render_template("recommender.html",username=username)

@app.route("/<username>/view", methods=['GET'])
def view(username):
    clicked_events = get_clicked_events(username)   
    return render_template("my_events.html", username=username, my_events=clicked_events)

app.run(debug=True)

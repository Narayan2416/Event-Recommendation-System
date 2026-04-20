import os
from flask import jsonify,request,render_template,redirect,url_for,session, Blueprint,abort
from db.data_base import user_insert, load_data,get_event,save_search,save_user_interaction,get_clicked_events,user_exists,get_userid
from recommender.recommendation import recommend_by_query,recommend_similar_event,recommend_based_on_prevSearches,recommend_based_on_user_interaction,popular_event_list
from scrappers.scrapper2 import add_new_Event
import time
from dotenv import load_dotenv

load_dotenv()

bp = Blueprint("services", __name__)

CLIENT_ID = os.getenv("CLIENT_ID")

# helper routes-----------------------------------------------------------------

def is_local():
    return os.getenv("ENV","local") == "local"

@bp.route("/load_data")
def load_data_route():
    if not is_local():
        abort(403)
    data = load_data()
    #print(data[14])
    return jsonify(data)

@bp.route("/<uid>/clicked_event/<event_id>", methods=['GET','POST'])
def clicked_event(uid, event_id):
    save_user_interaction(uid, event_id, action="click")
    return redirect(get_event(event_id)['url'])

@bp.route("/api/recommendation", methods=['GET','POST'])
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

@bp.route("/admin", methods=['GET','POST'])
def admin():
    if not is_local():
        abort(403)
    return render_template("admin.html")

@bp.route("/admin/add_event",methods=['GET','POST'])
def add_event():
    if not is_local():
        abort(403)
    events=[]
    if request.method == 'POST':
        events=add_new_Event()
        return render_template("add_event.html", events=events)
    return render_template("add_event.html", events=events) #admin adding event page

@bp.route("/<uid>/search",methods=['GET','POST'])
def search(uid):
    return render_template("search.html",uid=uid)

@bp.route("/semantic_search", methods=['POST'])
def semantic_search():
    query=request.json.get('query', '')
    if not query:
        return jsonify([])
    save_search(session['uid'], query)
    results = recommend_by_query(query, 100)
    return jsonify(results)

@bp.route("/<uid>/event/<event_id>", methods=['GET'])
def event_details(uid, event_id):
    # Fetch user-specific events from the database
    event = get_event(event_id)
    save_user_interaction(uid, event_id,action="view")
    suggestions = recommend_similar_event(event_id)
    return render_template("event_details.html",uid=uid, event=event, suggestions=suggestions)

@bp.route("/<uid>/recommender",methods=['GET','POST'])
def recommender(uid):
    return render_template("recommender.html",uid=uid)

@bp.route("/<uid>/view", methods=['GET'])
def view(uid):
    clicked_events = get_clicked_events(uid)   
    return render_template("my_events.html", uid=uid, my_events=clicked_events)



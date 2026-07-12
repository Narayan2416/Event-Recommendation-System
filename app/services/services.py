import os
from flask import jsonify,request,session, Blueprint
from db.data_base import load_data,save_search
from recommender.recommendation import recommend_by_query,recommend_based_on_prevSearches,recommend_based_on_user_interaction,popular_event_list
import time
from dotenv import load_dotenv

load_dotenv()

bp = Blueprint("services", __name__)

CLIENT_ID = os.getenv("CLIENT_ID")

@bp.route("/api/events")
def load_data_route():

    data = load_data()
    return jsonify(data)

@bp.route("/api/recommendation/interests", methods=["POST","GET"])
def api_RecInterests():

    uid = session.get("uid")

    if uid is None:
        return jsonify({"error": "User ID is required"}), 400

    interactions = recommend_based_on_user_interaction(uid)

    return jsonify({
        "interests": interactions
    })

@bp.route("/api/recommendation/searches", methods=["POST","GET"])
def api_RecSearches():

    uid = session.get("uid")

    if uid is None:
        return jsonify({"error": "User ID is required"}), 400

    searches = recommend_based_on_prevSearches(uid)

    return jsonify({
        "searches": searches
    })

@bp.route("/api/events/popular", methods=["POST","GET"])
def api_RecPopular():

    popular = popular_event_list()

    return jsonify({
        "popular": popular
    })

@bp.route("/api/recommendation",methods=["GET"])
def api_recommendation():

    uid = session.get("uid")

    if uid is None:
        return jsonify({"error": "User ID is required"}), 400

    #st = time.time()

    rec_search = recommend_based_on_prevSearches(uid)

    rec_interaction = recommend_based_on_user_interaction(uid)

    rec_popular = popular_event_list()

    '''print(
        f"Recommendation time: "
        f"{time.time() - st} seconds"
    )'''

    return jsonify({
        "searches": rec_search,
        "interests": rec_interaction,
        "popular": rec_popular
    })


@bp.route("/api/events/semantic_search", methods=["POST","GET"])
def semantic_search():
    if request.method == "POST":
        query = request.json.get("query", "")
    else:
        query = request.args.get("query", "")

    if not query:
        return jsonify([])

    uid=session.get('uid')

    if(uid):
        save_search(uid,query)

    results = recommend_by_query(query,100)

    return jsonify(results)
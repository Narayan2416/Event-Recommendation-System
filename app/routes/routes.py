import os
from flask import render_template,redirect,Blueprint
from db.data_base import get_event,save_user_interaction,get_clicked_events
from recommender.recommendation import recommend_similar_event
from dotenv import load_dotenv

load_dotenv()

bp = Blueprint("routes", __name__)

CLIENT_ID = os.getenv("CLIENT_ID")

# ----------------------------------------
# PAGE ROUTES
# ----------------------------------------

@bp.route("/<uid>/search")
def search(uid):

    return render_template(
        "search.html",
        uid=uid
    )


@bp.route("/<uid>/recommender")
def recommender(uid):

    return render_template(
        "recommender.html",
        uid=uid
    )


@bp.route("/<uid>/event/<event_id>")
def event_details(uid, event_id):

    event = get_event(event_id)

    save_user_interaction(uid,event_id,action="view")

    suggestions = recommend_similar_event(event_id)

    return render_template(
        "event_details.html",
        uid=uid,
        event=event,
        suggestions=suggestions
    )


@bp.route("/<uid>/clicked_event/<event_id>")
def clicked_event(uid, event_id):

    save_user_interaction(uid,event_id,action="click")

    event = get_event(event_id)

    return redirect(event["url"])


@bp.route("/<uid>/view")
def view(uid):

    clicked_events = get_clicked_events(uid)

    return render_template(
        "my_events.html",
        uid=uid,
        my_events=clicked_events
    )
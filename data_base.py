import pandas as pd
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["event_recommendation"]
users = db["users"]
user_interaction=db["user_interaction"]
user_profile=db["user_profile"]
search_history=db["search_history"]

data=pd.read_csv("data/event_data.csv",keep_default_na=False)

def load_data():
    # Load your event data here
    return data[['id','title','mode','price_type','clean_desc','city']].to_dict(orient="records")


def format_datetime(dt_str):
    if not dt_str:
        return None

    dt_str = str(dt_str).strip().lower()
    if dt_str in ["not specified", "unknown", "n/a"]:
        return None
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%d %b %Y, %I:%M %p")
    except ValueError:
        return None

def get_event(id):
    event=data[data['id']==int(id)]
    ans=event.iloc[0][['id','title','mode','price_type','clean_desc','location','url']].to_dict()
    '''ans['start_datetime'] = format_datetime(event.iloc[0]['start_datetime'])
    ans['end_datetime'] = format_datetime(event.iloc[0]['end_datetime'])'''
    return ans

def save_search(uid,query):
    search_history.insert_one({
        "uid": uid,
        "query": query,
        "timestamp": datetime.now(timezone.utc)
    })

def save_user_interaction(uid, event_id, action):
    user_interaction.insert_one({
        "uid": uid,
        "event_id": event_id,
        "action": action,
        "timestamp": datetime.now(timezone.utc)
    })

def get_recent_interactions(uid, limit=4):
    return list(
        user_interaction
        .find({"uid": uid})
        .sort("timestamp", -1)
        .limit(limit)
    )

def get_recent_searches(uid, limit=4):
    return list(
        search_history
        .find({"uid": uid})
        .sort("timestamp", -1)
        .limit(limit)
    )

def get_top_interaction(top=10):
    pipeline = [
        {
            "$group": {
                "_id": "$event_id",
                "count": {"$sum": 1},
                "last_interaction": {"$max": "$timestamp"}
            }
        },
        {
            "$sort": {
                "count": -1,
                "last_interaction": -1
            }
        },
        {
            "$limit": top
        }
    ]
    return list(user_interaction.aggregate(pipeline))

def get_userid(username,email):
    user = users.find_one({
        "username": username,
        "email": email
    })
    return user['uid'] if user else None

def user_exists(uid):
    return users.find_one({
        "uid": uid
    }) is not None

def user_insert(uid, username, email):
    if not user_exists(uid):
        users.insert_one({
            "username": username,
            "email": email,
            "uid": uid,
            "timestamp": datetime.now(timezone.utc)
        })
    return True

def get_clicked_events(uid):
    l= list(
        user_interaction
        .find({"uid": uid, "action": "click"})
        .sort("timestamp", -1)
    )
    ans=[]
    visi=[]
    for i in l:
        if i['event_id'] in visi:
            continue
        event=data.loc[data['id']==int(i['event_id'])].to_dict(orient="records")
        '''event[0]['start_datetime'] = format_datetime(event[0]['start_datetime'])
        event[0]['end_datetime'] = format_datetime(event[0]['end_datetime'])'''
        ans.append(event[0])
        visi.append(i['event_id'])
    return ans



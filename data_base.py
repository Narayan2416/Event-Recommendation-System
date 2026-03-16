import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone
from pymongo import MongoClient


client = MongoClient("mongodb+srv://phnarayanamoorthy_db_user:SHL9fbveKeYZ2DAQ@cluster0.5ohobpv.mongodb.net/")
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

def save_search(username,query):
    search_history.insert_one({
        "username": username,
        "query": query,
        "timestamp": datetime.now(timezone.utc)
    })

def save_user_interaction(username, event_id, action):
    user_interaction.insert_one({
        "username": username,
        "event_id": event_id,
        "action": action,
        "timestamp": datetime.now(timezone.utc)
    })

def get_recent_interactions(username, limit=4):
    return list(
        user_interaction
        .find({"username": username})
        .sort("timestamp", -1)
        .limit(limit)
    )

def get_recent_searches(username, limit=4):
    return list(
        search_history
        .find({"username": username})
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


def user_exists(username, email):
    return users.find_one({
        "username": username,
        "email": email
    }) is not None

def user_insert(username, email):
    if not user_exists(username, email):
        users.insert_one({
            "username": username,
            "email": email,
            "timestamp": datetime.now(timezone.utc)
        })
    return True

def get_clicked_events(username):
    l= list(
        user_interaction
        .find({"username": username, "action": "click"})
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



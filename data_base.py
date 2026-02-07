import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone
from pymongo import MongoClient

import base64

client = MongoClient("mongodb://localhost:27017/")
db = client["event_recommendation"]
users = db["users"]
user_interaction=db["user_interaction"]
user_profile=db["user_profile"]
search_history=db["search_history"]

data=pd.read_csv("data/newevent_data.csv")

def load_data():
    # Load your event data here
    return data[['id','title','mode_clean','price_type','description','city']].to_dict(orient="records")


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
    ans=event.iloc[0][['id','title','mode_clean','price_type','description','location and city','url']].to_dict()
    ans['start_datetime'] = format_datetime(event.iloc[0]['start_datetime'])
    ans['end_datetime'] = format_datetime(event.iloc[0]['end_datetime'])
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
        event[0]['start_datetime'] = format_datetime(event[0]['start_datetime'])
        event[0]['end_datetime'] = format_datetime(event[0]['end_datetime'])
        ans.append(event[0])
        visi.append(i['event_id'])
    return ans



def send_registration_email(user_email, user_name, event_name,date):
    if event_insert(user_email,event_name):
        # Email credentials
        sender_email = r"projectexpo745@gmail.com"
        sender_password = r"btornwkiapiystcd"
        
        # Set up the SMTP server (using Gmail's SMTP server)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # Create the email content
        subject = "Event Registration Confirmation"
        body = f"""
        Hi {user_name},
    
        Thank you for registering for {event_name}! held on {date}!

        We're excited to have you join us. If you have any questions, feel free to reach out.

        Best regards,
        The Event Team
        """
        # Set up the MIME structure
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = user_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        try:
            # Connect to the SMTP server
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Enable TLS for security
            server.login(sender_email, sender_password)
            
            # Send the email
            server.sendmail(sender_email, user_email, message.as_string())
            print("Email sent successfully!")
            
        except Exception as e:
            print(f"Error: {e}")
            
        finally:
            server.quit()
        if st.session_state['current_page']=='page2':
            st.markdown('''<h3 style='font-size: 20px;'>Thank you for registering! 
                    Your registration for the event is successful,
                    and a confirmation message has been sent to your mail </h3>''', unsafe_allow_html=True)
        else:
            st.markdown('''<h3 style='font-size: 20px;'>Your registration for the event is successful,
                        and a confirmation message has been sent to your mail </h3>''', unsafe_allow_html=True)
    else:
        st.markdown('''<h3 style='font-size: 20px;'>You have already registered for this Event</h3>''', unsafe_allow_html=True)
    

def show_event_details():
            index=0
            for i in st.session_state['predictions']:
                a=st.session_state['final_event_dataset'][st.session_state['final_event_dataset']['Event Name']==i]
                for col in a.columns.tolist():
                    if a[col].dtype == 'object':  # Only process string columns
                        # Split the string by "Name"
                        split_vals = a[col].str.split('Name')
                        # Safely handle the splitting and remove '16'
                        if isinstance(split_vals.iloc[0], list):
                            val = split_vals.iloc[0][0].replace('16', '').strip()  # Remove '16' and strip spaces
                        else:
                            val = split_vals.iloc[0]
                    else:
                        val = a[col].iloc[0] 
                    st.write(f"{col} : {val}")
                if st.button("Register",key=f"button{index}"):
                    user_email =st.session_state['user_mail']
                    user_name =st.session_state['name']
                    event_name = a['Event Name']
                    date=a['Month']
                    send_registration_email(user_email, user_name, event_name.iloc[0],date)
                index+=1
                    #st.markdown("<h3 style='font-size: 20px;'>Email sent successfully to Your Mail id!</h3>", unsafe_allow_html=True)
                st.markdown("--------------------------------------------------------------------")

def show():
    add_bg_from_base64("pencil_yellow.jpg")
    # Add background image and styling
    st.markdown(
        """
        <style>

        .stTitle {
            color: #333333;
            font-family: 'MV Boli', serif;
            font-size: 3em;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
            display: inline-block;
            transition: transform 0.3s ease, color 0.3s ease, text-shadow 0.3s ease; /* Smooth transition for hover */
        }

        /* Title hover effect */
        .stTitle:hover {
            color: #555555;  /* Change to medium grey when hovered */
            transform: scale(1.1); /* Slight zoom on hover */
            text-shadow: 3px 3px 5px rgba(0, 0, 0, 0.3); /* Shadow effect */
        }

        .stSubtitle {
            color: #333333; /* Dark grey */
            font-size: 2em;
            font-weight: bold;
            text-align: center;
            margin-top: 10px;
            margin-bottom: 20px;
        }

        /* All text in white */
        .stText {
            color: white;
            font-size: 16px;
        }

        .stwrite {
            color: #333333;
        }

        /* Button styles */
        .stButton>button {
            background-color: #333333; /* Dark grey background */
            color: white;
            padding: 10px 25px;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: bold;
            transition: background-color 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease;
        }

        .stButton>button:hover {
            background-color: #555555; /* Lighter grey */
            transform: scale(1.05);
            box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.3);
        }
        </style>
        """,
        unsafe_allow_html=True)

    # Title for the event page
    if st.session_state['current_page']=='direct_reg':
        st.markdown('<h1 class="stTitle">THANK YOU FOR REGISTRATION!!</h1>', unsafe_allow_html=True)
        mail=st.session_state['user_mail']
        name=st.session_state['name']
        mon=st.session_state['Month']
        eve_name=st.session_state['event_name']
        send_registration_email(mail,name,eve_name,mon)
    else:
        # Display recommendations
        st.markdown('<h1 class="stTitle">WE RECOMMEND</h1>', unsafe_allow_html=True)
        st.write(", ".join(st.session_state['predictions']))
        st.markdown("<h3 style='font-size: 30px;'>Event Details</h3>", unsafe_allow_html=True)
        st.markdown("--------------------------------------------------------------------")
        show_event_details()
        if st.button("Previous"):
            st.session_state['current_page']='final_model'
            st.rerun()

    with st.sidebar:
        page=option_menu(
            menu_title='Menu',
            menu_icon='columns-gap',
            options=['Home','Register Events','Recommend','View Events'],
            icons=['house-fill','table','caret-right-fill','bullseye'],
            default_index=2,
            styles={
                    "container": {"padding": "0!important", "background-color": "#25252F"},
                    "icon": {"color": "white", "font-size": "20px"},
                    "nav-link": {
                        "font-size": "16px",
                        "text-align": "left",
                        "margin": "0px",
                        "--hover-color": "#add8e6",
                    },
                    "nav-link-selected": {"background-color": "orange"},
                },
            )
        if page=='Regsiter events':
            st.session_state['current_page']='search_bar'
            st.rerun()
        elif page=='Home':
            st.session_state['current_page']='page1'
            st.rerun()
        elif page=='Recommend':
            pass
        elif page=='View Events':
            st.session_state['current_page']='view'
            st.rerun()
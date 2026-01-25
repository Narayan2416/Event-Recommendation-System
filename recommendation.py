import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from data_base import get_recent_interactions,get_recent_searches
from pymongo import MongoClient

# ---------------- LOAD DATA ----------------
final_df = pd.read_csv("data/newevent_data.csv")

embeddings = np.load("data/event_embeddings.npy") 

assert len(final_df) == embeddings.shape[0], "Mismatch between CSV and embeddings"

model = SentenceTransformer("all-MiniLM-L6-v2")

client = MongoClient("mongodb://localhost:27017/")
db = client["event_recommendation"]
user = db["users"]

# helper functions-----------------------------------------------------------------------------------------------

def remove_duplicate_interactions(interactions):
    seen = set()
    unique_interactions = []
    for interaction in interactions:
        if interaction['event_id'] not in seen:
            unique_interactions.append(interaction)
            seen.add(interaction['event_id'])
    return unique_interactions

def remove_duplicate_searches(searches):
    seen = set()
    unique_searches = []
    for search in searches:
        if search['query'] not in seen:
            unique_searches.append(search)
            seen.add(search['query'])
    return unique_searches

def interaction_vector(username):
    interactions = get_recent_interactions(username)
    interactions = remove_duplicate_interactions(interactions)
    vec = np.zeros(embeddings.shape[1])  # same dimension as embedding
    divi=0
    for i,interaction in enumerate(interactions):
        idx = final_df.index[final_df['id'] == int(interaction['event_id'])]
        if len(idx) == 0:
            continue
        event_index = idx[0]
        val=embeddings[event_index]
        if(interaction['action']=='click'):
            weight=0.7
        else:
            weight=0.3
        recency_weight = 1 / (i + 1)
        vec+=val*weight*(recency_weight)
        divi+=(weight*recency_weight)
    if divi==0: return vec
    return vec/divi

def search_vector(username):
    searches = get_recent_searches(username)
    searches = remove_duplicate_searches(searches)
    vec = np.zeros(embeddings.shape[1])  # same dimension as embedding
    divi = 0
    for i, search in enumerate(searches):
        query_emb = model.encode([search['query']])
        query_emb = query_emb.squeeze()
        recency_weight = 1 / (i + 1)
        vec += query_emb * recency_weight
        divi += recency_weight
    if divi==0: return vec
    return vec / divi

#recommendation functions--------------------------------------------------------------------------------------

def recommend_by_query(query, top_k=100):
    query_emb = model.encode([query])
    sims = cosine_similarity(query_emb, embeddings)[0]

    valid_idx = np.where(sims > 0.25)[0]
    if len(valid_idx) == 0:
        return []

    top_idx = valid_idx[np.argsort(sims[valid_idx])[::-1][:top_k]]
    results = final_df.iloc[top_idx][['id','title','mode_clean','price_type','description','city']].copy()

    results["score"] = (sims[top_idx] * 100).round(2)

    return results.to_dict(orient="records")

#print(recommend_by_query("ai workshop", top_k=5))

def recommend_similar_event(event_index, top_k=10):
    idx = final_df.index[final_df['id'] == int(event_index)]
    if len(idx) == 0:
        return []
    event_index = idx[0]
    event_emb = embeddings[event_index].reshape(1, -1)
    sims = cosine_similarity(event_emb, embeddings)[0]

    top_idx = sims.argsort()[::-1][1:top_k+1]
    return final_df.iloc[top_idx][['id','title','mode_clean','price_type','description','city']].to_dict(orient="records")

def recommend_based_on_user_interaction(username, top_k=10):
    inter_vec = interaction_vector(username)
    search_vec = search_vector(username)

    vector = (0.7 * inter_vec + 0.3 * search_vec)
    if (np.linalg.norm(vector) == 0): return []

    score = cosine_similarity(vector.reshape(1, -1), embeddings)[0]
    threshold = np.percentile(score, 80)
    score[score < threshold] = -1
    #print(score)
    interactions = get_recent_interactions(username)
    seen_event_ids = set(int(i['event_id']) for i in interactions if i['action']=='click')
    # Penalize already seen events
    for idx, event_id in enumerate(final_df['id']):
        if int(event_id) in seen_event_ids:
            score[idx] = -1  # remove from recommendation

    top_idx = score.argsort()[::-1][:top_k]
    return final_df.iloc[top_idx][['id','title','mode_clean','price_type','description','city']].to_dict(orient="records")

def recommend_based_on_prevSearches(username):
    search_vec=search_vector(username)
    if np.linalg.norm(search_vec) == 0:
        return []
    
    score=cosine_similarity(search_vec.reshape(1,-1),embeddings)[0]

    threshold=np.percentile(score,85)
    score[score<threshold]=-1
    
    interactions = get_recent_interactions(username)
    seen_event_ids = set(int(i['event_id']) for i in interactions if i['action']=='click')
    for idx, event_id in enumerate(final_df['id']):
        if int(event_id) in seen_event_ids:
            score[idx] = -1  # remove from recommendation

    top_idx = score .argsort()[::-1][:10]
    return final_df.iloc[top_idx][['id','title','mode_clean','price_type','description','city']].to_dict(orient="records")

#print(recommend_based_on_user_interaction("naran"))

def build_user_profile(event_indices):
    return embeddings[event_indices].mean(axis=0).reshape(1, -1)


def recommend_personalized(user_interest):
    user_profile = build_user_profile(user_interest)

    scores = cosine_similarity(user_profile, embeddings)[0]
    top_idx = scores.argsort()[::-1][:5]

    return final_df.iloc[top_idx][["title", "datetime", "url"]]




#--------------------------------------------------------------------------------------------------------------------------------

# Function to encode the image to Base64
def get_base64_image(image_path):
    with open(image_path, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()
    return encoded

# Function to add a background image using Base64
def add_bg_from_base64(image_path):
    encoded_image = get_base64_image(image_path)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded_image}"); 
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            height: 100vh;
            display: flex;
            justify-content: flex-start; /* Align content to the left */
            align-items: flex-start; /* Align vertically to the top */
            flex-direction: column;
            padding-left: 50px; /* Left padding for alignment */
            padding-top: 50px; /* Top padding for alignment */
        }}
        </style>
        """,
        unsafe_allow_html=True,)


# Prediction function
def predict(models, X_test,label_encoders):
    predictions = []
    for model in models:
        pred = model.predict(X_test)
        s = label_encoders['Event Name'].inverse_transform(pred)[0]
        if s not in predictions:
             predictions.append(s)
    return predictions

# Function to store user input in the database
def store_user_input(name, dept, college, city, event_type):
    # Connect to MySQL database
    conn = mysql.connector.connect(
        host='localhost',           # e.g., 'localhost'
        user='root',                # your MySQL username
        password='nara@123',     # your MySQL password
        database='expo'       # your database name
    )
    
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO Users (name, dept, college, city, event_type) 
    VALUES (%s, %s, %s, %s, %s)
    ''', (name, dept, college, city, event_type))
    
    conn.commit()
    conn.close()
    cursor.close()


# Streamlit app
def recommend():
    event_data = st.session_state['event_dataset']
    student_data = st.session_state['students_dataset']
    new_events=pd.read_csv("newlyadded_events.csv")

    # Merge both datasets on 'Event Name' for complete feature information
    data = pd.merge(student_data, event_data, on='Event Name')
    # Combine 'College' and 'City' into a new feature
    data['College_City'] =data['College'] + '_' + data['City']
    # Encoding categorical columns
    label_encoders = {}
    for column in ['Dept', 'College', 'City', 'Domain', 'Event Name', 'College_City', 'Event Type','Month']:
        label_encoders[column] = LabelEncoder()
        data[column] = label_encoders[column].fit_transform(data[column])

    #---------------------------------------updated till encoding----------------------------------

# Create a mapping of valid city options based on the college selected
    college_city_mapping =data[['College', 'City']].drop_duplicates().set_index('College')['City'].to_dict()
    #st.title("Event Recommendation System")

    # Input fields in Streamlit with unique keys for selectboxes

    dept = st.selectbox("Enter Dept:", label_encoders['Dept'].classes_, key="dept_select")
    
    college = st.selectbox("Enter College:", label_encoders['College'].classes_, key="college_select")

    # Automatically select city based on the selected college
    if college in college_city_mapping:
        city = college_city_mapping[college]
        st.session_state['selected_city'] = city  # Store selected city in session state
    else:
        city = st.selectbox("Enter City:", label_encoders['City'].classes_, key="city_select")
        st.session_state['selected_city'] = city  # Allow manual city selection if college not mapped

    # Show selected city for confirmation
    #st.write(f"Selected City: {st.session_state['selected_city']}")

    domain_inst = st.selectbox("Enter Your Domain interest:", label_encoders['Domain'].classes_, key="domain_select")
    event_type = st.selectbox("Enter Your Event Type preference:", label_encoders['Event Type'].classes_, key="event_type_select")

    if st.button('Recommend'):
        st.session_state['predictions']=[]
        x_test=[]
        '''x_test.append(label_encoders['Dept'].transform([dept])[0])
        x_test.append(label_encoders['College'].transform([college])[0])
        x_test.append(label_encoders['City'].transform([st.session_state.selected_city])[0])
        x_test.append(label_encoders['Domain'].transform([domain_inst])[0])
        x_test.append(label_encoders['Event Type'].transform([event_type])[0])
        college_city_label = college + '_' + st.session_state['selected_city']
        x_test.append(label_encoders['College_City'].transform([college_city_label])[0])
        X_test = pd.DataFrame([x_test], columns=['Dept','College','City','Domain','Event Type','College_City'])
        models = train(data[['Dept','College','City','Domain','Event Type','College_City']],data['Event Name'])
        predictions = predict(models, X_test,label_encoders)
        st.session_state['predictions'].extend([predictions[0]])'''        

        x_col = []
        x_test = []

        if dept in label_encoders['Dept'].inverse_transform(data['Dept']):
            x_col.append('Dept')
            x_test.append(label_encoders['Dept'].transform([dept])[0])
        
        if college in label_encoders['College'].inverse_transform(data['College']):
            x_col.append('College')
            x_test.append(label_encoders['College'].transform([college])[0])

        if st.session_state.selected_city in label_encoders['City'].inverse_transform(data['City']):
            x_col.append('City')
            x_test.append(label_encoders['City'].transform([st.session_state.selected_city])[0])
                
        if domain_inst in label_encoders['Domain'].inverse_transform(data['Domain']):
            x_col.append('Domain')
            x_test.append(label_encoders['Domain'].transform([domain_inst])[0])

        if event_type in label_encoders['Event Type'].inverse_transform(data['Event Type']):
            x_col.append('Event Type')
            x_test.append(label_encoders['Event Type'].transform([event_type])[0])
            
        if 'College' in x_col and 'City' in x_col:
            college_city_label = college + '_' + st.session_state['selected_city']
            if college_city_label in label_encoders['College_City'].inverse_transform(data['College_City']):
                x_col.append('College_City')
                x_test.append(label_encoders['College_City'].transform([college_city_label])[0])
            else:
                st.write("KINDLY ENTER THE VALID LOCATION OF YOUR COLLEGE!!")
                return  # Exit if the label is not valid
        
        if not x_col:
            st.write(f"SORRY {st.session_state['name']}, PROVIDED DATA IS UNIQUE, UNABLE TO RECOMMEND!")
        else:
            X_test = pd.DataFrame([x_test], columns=x_col)

                # Train and predict
            with open('expo_model.pkl', 'rb') as f:
                model = pic.load(f)
            models=model[st.session_state['dataset']]
            #models = train(data[x_col], data['Event Name'])
            predictions = predict(models, X_test,label_encoders)
            
            new_events=new_events[new_events['City']==st.session_state['dataset']][['Event Name','Domain','Month','Organizer','Description','Contact Information','Event Type','college_location']]
            if not new_events.empty:
                if domain_inst in new_events['Domain']:
                    new_events=new_events[new_events['Domain']==domain_inst]
                else:
                    st.session_state['predictions'].extend(predictions)
                    st.session_state['final_event_dataset']=event_data
                    st.session_state['current_page']='page2'
                    st.rerun()
            if new_events.shape[0]>=1:
                new_events2=new_events
                new_events=new_events[new_events['Event Type']==event_type]
                if new_events.empty:
                    st.session_state['predictions'].extend(new_events2['Event Name'].tolist())
                    st.session_state['predictions'].extend(predictions)
                    st.session_state['final_event_dataset']=pd.concat([event_data,new_events2],axis=0,ignore_index=True)
                    st.session_state['current_page']='page2'
                    st.rerun()
                else:
                    st.session_state['predictions'].extend(new_events['Event Name'].tolist())
                    st.session_state['predictions'].extend(predictions)
                    st.session_state['final_event_dataset']=pd.concat([event_data,new_events],axis=0,ignore_index=True)
                    st.session_state['current_page']='page2'
                    st.rerun()
            else:


                    # Store user input into the database
                    #store_user_input(name, dept, college, st.session_state['selected_city'], event_type)
                st.session_state['predictions'].extend(predictions)
                st.session_state['final_event_dataset']=event_data
                st.session_state['current_page']='page2'
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

    if page=='Register Events':
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
            
            

def show():
    add_bg_from_base64("pencil_yellow.jpg")
    st.markdown(
    """
    <style>


    /* Title animation with hover effect */
    .stTitle {
        color: #333333; /* Dark grey */
        font-family: 'MV Boli', serif; /* Script font for a stylish look */
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
        transform: scale(1.05); /* Slight zoom on hover */
        text-shadow: 3px 3px 5px rgba(0, 0, 0, 0.3); /* Shadow effect */
    }

    /* Bold labels for select boxes */
    .stSelectbox label {
        font-weight: bold;
        color: #333333;
        font-size: 30px;  /* Adjusted size for better visibility */
    }

    /* Select box styling */
    .stSelectbox > div {
        margin: 10px auto;
        border: 2px solid #808080; /* Gray border */
        border-radius: 5px; /* Rounded corners */
        padding: 0.1px; /* Internal spacing */
        max-width: 800px; /* Limit width */
        transition: all 0.3s ease-in-out; /* Smooth transition effect */
    }

    /* Glow hover effect for select boxes */
    .stSelectbox > div:hover {
        border-color: #888888; /* Slightly darker gray on hover */
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3); /* Adds glowing effect */
        transform: scale(1.03); /* Slight enlargement */
    }

    /* Style buttons */
    .stButton>button {
        background-color: #333333; /* Dark grey background */
        color: white;
        padding: 8px 20px;
        border: none;
        border-radius: 8px;
        font-size: 18px;
        font-weight: bold;
        transition: background-color 0.3s ease, transform 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #555555; /* Hover effect - lighter grey */
        transform: scale(1.05);
        box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.4);
    }

    /* Style warning text */
    .stMarkdown {
        color:#333333 ;
        font-size: 16px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True)

    # Add the title with hover animation
    st.markdown('<h1 class="stTitle">EVENT RECOMMENDATION SYSTEM</h1>', unsafe_allow_html=True)

    recommend()
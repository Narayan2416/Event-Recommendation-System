import streamlit as st
import pickle as pic
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from streamlit_option_menu import option_menu
import mysql.connector

import base64

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
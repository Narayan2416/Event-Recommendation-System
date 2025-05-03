import streamlit as st
import psycopg2
import pandas as pd
from streamlit_option_menu import option_menu

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
            flex-direction: column;
            align-items: center;
        }}
        </style>
        """,
        unsafe_allow_html=True,)
    
def show():
    add_bg_from_base64("pencil_yellow.jpg")
    st.markdown(
        """
        <style>

        /* General text styling for the whole app (Dark grey text) */
        body, h3, label, span, a {
            color: #333333 !important; /* Dark grey color for text */
        }

        /* Title styling */
        .stTitle {
            color: #333333; /* Dark grey color for title */
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

        /* Button styling */
        .stButton button {
            background-color:#333333 !important; /* Make the background transparent */
            color: white !important; /* Button text is white */
            border: 2px solid #333333 !important; /* Dark grey border */
            border-radius: 8px;
            font-size: 16px;
            padding: 8px 20px;
            cursor: pointer;
            transition: all 0.3s ease-in-out;
        }

        .stButton button:hover {
            background-color: #555555 !important; /* Keep the background transparent on hover */
            color: white !important; /* Keep text white on hover */
            border-color: #505050 !important; /* Change the border to a slightly lighter grey on hover */
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.4);
            transform: scale(1.05);
        }

        /* Ensure text inside button is white */
        .stButton button span {
            color: white !important;
        }

        /* Filter box styling */
        .st-expander {
            border: 2px solid #333333 !important; /* Dark grey border */
            border-radius: 8px;
            background-color: rgba(255, 255, 255, 0.8); /* Semi-transparent */
            padding: 10px;
        }

        .st-expander .st-expander-header {
            background-color: rgba(255, 255, 255, 0.8) !important;
            color: white !important; /* Ensure header text is white */
            font-weight: bold !important;
        }

        /* Table styling */
        .stDataFrame {
            background-color: rgba(255, 255, 255, 0.5) !important; /* Semi-transparent background */
            border-radius: 8px;
        }

        .stDataFrame tbody tr {
            transition: all 0.3s ease;
        }

        .stDataFrame tbody tr:hover {
            background-color: rgba(200, 200, 200, 0.5) !important; /* Row hover effect */
            color: white !important; /* Row text color white on hover */
        }

        /* Table header styling */
        .stDataFrame thead th {
            color: white !important; /* White text in header */
            font-weight: bold !important;
        }

        /* Input box styling */
        .stTextInput>div>div>input, .stSelectbox>div>div>div>div {
            border: 1px solid #333333 !important; /* Dark grey border */
        }

        .stTextInput>div>div>input:focus, .stSelectbox>div>div>div>div:focus {
            border-color: #505050 !important; /* Slightly darker grey on focus */
            box-shadow: 0px 0px 5px rgba(50, 50, 50, 0.5);
        }

        /* Dark grey horizontal line */
        .stMarkdown hr {
            border: 1px solid #333333 !important; /* Dark grey border for the line */
        }

        .stTable {
            background-color: #25252F !important; /* Dark grey background */
            color: white !important; /* White text */
            border-radius: 18px; /* Rounded corners for the table */
            padding: 0px; /* Add some padding for aesthetics */
        }

        /* Customize the table header */
        .stTable th {
            background-color: #333333 !important; /* Slightly lighter grey for the header */
            color: white !important; /* White text for the header */
            font-weight: bold; /* Bold text in the header */
            
        }

        /* Customize the table rows */
        .stTable tbody tr {
            border-bottom: 1px solid #444444; /* Light border between rows */
            transition: all 0.3s ease; /* Smooth transition for hover effect */
        }

        .stTable tbody tr:hover {
            background-color: #373737; /* Slightly lighter grey on hover */
            color: white; /* Ensure text remains white */
        }

        .custom-title {
            color: black; /* White text for the title */
            font-family: 'Arial', sans-serif; /* Font family */
            font-size: 2.5em; /* Font size */
            font-weight: bold; /* Bold text */
            text-align: center; /* Center the title */
            margin-bottom: 20px; /* Space below the title */
            transition: transform 0.3s ease, text-shadow 0.3s ease; /* Smooth transition for hover effects */
        }

        /* Title hover effect */
        .custom-title:hover {
            transform: scale(1.1); /* Slight zoom-in effect */
            text-shadow: 3px 3px 10px rgba(0, 0, 0, 0.6); /* Shadow effect */
            color: #aaaaaa; /* Slightly lighter color on hover */
        }

        </style>
        """,
        unsafe_allow_html=True)
    

    st.markdown('<div class="custom-title">Registered Events</div>', unsafe_allow_html=True)

    con=psycopg2.connect(
          host='localhost',
          user='admin',
          password='admin',
          database='pro_expo',
          port='5432'
    )
    cur=con.cursor()
    view='''select Event_Name from registration 
    where email_id=%s;'''
    mail=st.session_state['user_mail']
    cur.execute(view,(mail,))
    data={'Events Registered':[]}
    rows=cur.fetchall()
    for i in rows:
        data['Events Registered'].append(i[0])
    df=pd.DataFrame(data)
    st.table(df)

    with st.sidebar:
        page=option_menu(
            menu_title='Menu',
            menu_icon='columns-gap',
            options=['Home','Register Events','Recommend','View Events'],
            icons=['house-fill','table','caret-right-fill','bullseye'],
            default_index=3,
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
        st.session_state['current_page']='final_model'
        st.rerun()
    elif page=='View Events':
        pass
import streamlit as st
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
            justify-content: flex-start; /* Align content to the left */
            align-items: flex-start; /* Align vertically to the top */
            flex-direction: column;
            padding-left: 50px; /* Left padding for alignment */
            padding-top: 50px; /* Top padding for alignment */
        }}
        </style>
        """,
        unsafe_allow_html=True,)

def show():
    add_bg_from_base64("pencil_yellow.jpg")  
    st.markdown(
    """
    <style>
        /* Title styling */
    .stMarkdown h3 {
        font-family: 'Dubai Light', serif;
        font-size: 32px;
        font-weight: bold;
        color: #2c3e50;
        text-transform: uppercase;
        text-align: left;
        transition: transform 0.3s ease, color 0.3s ease;
        margin-bottom: 30px;
    }
    .stMarkdown h3:hover {
        transform: scale(1.1) translateX(40px);
        color:#a6aeb7;
        text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
    }


    /* Title animation with hover effect */
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

    /* Bold labels for text input */
    .custom-input {
        font-weight: bold;
        color: #333333;
        font-size: 20px;  /* Adjusted size for better visibility */
    }

    /* Input box styling */
    .stTextInput > div {
        margin: 10px auto;
        border: 2px solid #a6aeb7; 
        border-radius: 10px;
        padding: 12px;
        max-width: 800px;
        transition: all 0.3s ease-in-out; /* Smooth transition effect */
    }

    /* Glow hover effect for input boxes */
    stTextInput > div:hover {
        border-color: #ffffff;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
        transform: scale(1.05);
    }
    .stTextInput input {
        color: dark grey; 
    }

    /* Style the button */
    .stFormSubmitButton button {
        background-color: #2c3e50; 
        color: white;
        padding: 12px 25px;
        border: none;
        border-radius: 8px;
        font-size: 18px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 90px;
        }   

    /* Pulsating hover effect for the button */
    .stFormSubmitButton button:hover {
        background-color: #a6aeb7;
        color: #2c3e50;
        transform: scale(1.05);
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
        }

    /* Align form elements to the left */
    .stForm, .stTextInput, .stButton, .stMarkdown {
        text-align: left;
        margin-left: 0px;
    }
    </style>
    """,
    unsafe_allow_html=True)
    with st.form('welcome'):
        st.markdown('<h1 class="stTitle">Welcome</h1>', unsafe_allow_html=True)
        name=st.text_input("Enter Your Name:")
        st.markdown(
            """
            <script>
            // Apply custom class to the text input
            document.querySelector("input[data-testid='stTextInput']").classList.add("custom-input");
            </script>
            """,
            unsafe_allow_html=True,)
        mail=st.text_input("Enter Your Mail id:")
        a=st.form_submit_button("Next")
        st.session_state['name']=name
    if a:
        if "@" not in mail or '.' not in mail:
            st.error("Enter valid email id")
        else:
            st.session_state['user_mail']=mail
            st.session_state['current_page']='search_bar'
            st.rerun()
import streamlit as st
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
            justify-content: flex-end; /* Moves content lower */
            align-items: center;
            flex-direction: column;
            padding-bottom: 100px; /* Fine-tune vertical positioning */
        }}
        </style>
        """,
        unsafe_allow_html=True,)
    
def show():
    add_bg_from_base64("pencil_yellow.jpg")
    # Add background image and styling
    st.markdown(
        """
        <style>

        /* Title styling for "EVENT REGISTRATION" */
        .stTitle {
            color: #333333; /* Dark grey color */
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

        /* General text styling for all text */
        .stText, .stMarkdown, .stSelectbox label {
            color: #333333; /* Dark grey color for all text */
            font-size: 16px;
        }

        /* Select box styles */
        .stSelectbox > div {
            background-color: #333333; /* Dark grey background */
            color: white; /* White text */
            border: 2px solid #333333; /* Dark grey border */
            border-radius: 5px;
            padding: 0.1px;
            transition: all 0.3s ease-in-out;
            max-width: 600px;
        }

        /* Select box hover effect */
        .stSelectbox > div:hover {
            background-color: #555555; /* Lighter grey when hovered */
            border-color: #555555; /* Lighter grey border */
            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3);
            transform: scale(1.03); /* Slight enlargement */
        }

        /* Button styles */
        .stButton>button {
            background-color: #333333; /* Dark grey background */
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease-in-out;
        }

        /* Hover effect for buttons */
        .stButton>button:hover {
            background-color: #555555;
            box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.4);
            transform: scale(1.05);
        }

        </style>
        """, unsafe_allow_html=True)

    # Display the custom title "EVENT REGISTRATION"
    st.markdown('<h1 class="stTitle">EVENT REGISTRATION</h1>', unsafe_allow_html=True)
    data=st.session_state['reg_dataset2']
    eve=st.selectbox("Select a Event",data['Event Name'],key='reg_eve')
    cole=st.selectbox("Select College name",data['college_location'].unique(),key='reg_col')
    sort_D=data[data['college_location']==cole]
    st.dataframe(sort_D[['Event Name','Domain','Month','Description','Event Type','college_location']])
    if st.button("Confirm"):
        if eve not in sort_D['Event Name'].values:
             st.write(f"There is no such event in the college {cole}")
        else:
            st.session_state['event_name']=eve
            st.session_state['event_dataset']=data
            st.session_state['current_page']='direct_reg'
            mon=sort_D[sort_D['Event Name'] == eve]['Month'].iloc[0]
            st.session_state['Month']=mon
            st.rerun()
    if st.button("Previous"):
        st.session_state['current_page']='search_bar'
        st.rerun()
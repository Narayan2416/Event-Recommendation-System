import streamlit as st
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
        </style>
        """,
        unsafe_allow_html=True)
    event_ssn=pd.read_csv("event_ssn.csv")
    event_kpr=pd.read_csv("event_kpr.csv")
    event_itech=pd.read_csv("event_data2.csv")
    event_nit=pd.read_csv("event_nit.csv")
    new_event=pd.read_csv("newlyadded_events.csv")

    students_ssn=pd.read_csv("feedback_ssn.csv")
    students_kpr=pd.read_csv("feedback_kpr.csv")
    students_itech=pd.read_csv("feedback_itech.csv")
    students_nit=pd.read_csv("feedback_nit.csv")

    event_ssn['college_location']=['SSN College of Engineering' for i in range(len(event_ssn))]
    event_kpr['college_location']=['KPR Institute of Engineering and Technology' for i in range(len(event_kpr))]
    event_itech['college_location']=['PSG Institute of Technology and Applied Research' for i in range(len(event_itech))]
    event_nit['college_location']=['NIT Trichy' for i in range(len(event_nit))]

    con=pd.concat([event_ssn,event_kpr,event_itech,event_nit,new_event],ignore_index=True).reset_index()
    search_data=con
    st.markdown("<h3 style='font-size: 30px;'>Events Available:</h3>", unsafe_allow_html=True)
    col1,col2=st.columns([3,1],vertical_alignment="bottom")
    with col1:
        st.markdown("""
        <style>
        .stTextInput input::placeholder {
            color: rgba(0, 0, 0, 0.5);  /* Color of placeholder text */
            font-size: 14px;             /* Size of placeholder text */
            font-style: italic;         /* Style of placeholder text */
        }
        </style>""", unsafe_allow_html=True)
        # Displaying the text input widget with custom placeholder text
        sea_input = st.text_input("Search Bar", placeholder="Enter a Month")
        search_input=sea_input.capitalize()
    with col2:
        #col2.write(' ')
        #col2.markdown("<br>"*1, unsafe_allow_html=True)
        if st.button("search"):
            if sea_input:
                events=pd.concat([event_itech,event_kpr,event_ssn,event_nit,new_event],axis=0,ignore_index=True) 
                global filter_data
                filter_data = events[events['Month'] == search_input].reset_index(drop=True)
                st.session_state['month_searched'] = search_input
                if not filter_data.empty:
                    search_data=filter_data
                else:
                    filter_data=con
            else:
                search_data=con
                filter_data=con
    st.dataframe(search_data[['Event Name','Domain','Month','Description','Event Type','college_location']])
    if st.button("Register Event",key='final2'):
        try:
            st.session_state['reg_dataset2']=filter_data
            st.session_state['current_page']='reg_form'
            st.rerun()
        except NameError:
            st.session_state['reg_dataset2']=con
            st.session_state['current_page']='reg_form'
            st.rerun()

    st.write("-----------------------------------------------------------------------------------")
    st.write("Select a City")
    custom_css = """
    <style>
        div.streamlit-expander {
            border: 10px solid #4CAF50; /* Change border thickness and color */
            border-radius: 10px;      /* Add rounded corners */
            margin-top: 10px;         /* Add space above the expander */
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2); /* Optional shadow effect */
        }
    </style>
    """

    # Inject the CSS into the app
    st.markdown(custom_css, unsafe_allow_html=True)
    with st.expander("Filter by Region"):
        search_input2=st.selectbox("Select your preferable Region",["Chennai","Coimbatore","Trichy"])

        if search_input2=='Chennai':
            new_eve=new_event[new_event['City']=='Chennai']
            st.session_state['event_dataset']=event_ssn
            st.session_state['dataset']='Chennai'
            st.session_state['students_dataset']=students_ssn
            st.dataframe(pd.concat([event_ssn,new_eve],axis=0,ignore_index=True)[['Event Name','Domain','Month','Description','Event Type','college_location']])

        elif search_input2=='Coimbatore':
            new_eve=new_event[new_event['City']=='Coimbatore']
            stu=pd.concat([students_itech,students_kpr],axis=0,ignore_index=True)
            coim=pd.concat([event_itech,event_kpr],axis=0,ignore_index=True)
            st.session_state['dataset']='Coimbatore'
            st.session_state['event_dataset']=coim
            st.session_state['students_dataset']=stu
            st.dataframe(pd.concat([coim,new_eve],axis=0,ignore_index=True)[['Event Name','Domain','Month','Description','Event Type','college_location']])

        elif search_input2=='Trichy':
            new_eve=new_event[new_event['City']=='Trichy']
            st.session_state['event_dataset']=event_nit
            st.session_state['dataset']='Trichy'
            st.session_state['students_dataset']=students_nit
            st.dataframe(pd.concat([event_nit,new_eve],axis=0,ignore_index=True)[['Event Name','Domain','Month','Description','Event Type','college_location']])
        if st.button("Register Event",key='final1'):
            if 'event_dataset' not in st.session_state:
                st.write("Select the Region")
            else:
                st.session_state['current_page']='reg_form'
                eve=st.session_state['event_dataset']
                st.session_state['reg_dataset2']=pd.concat([eve,new_eve],axis=0,ignore_index=True)
                st.rerun()
    
    #st.write("-----------------------------------------------------------------------------------")
    st.success(f"Selected City: {st.session_state['dataset']}")
    if st.button("Get Recommendation"):
        st.session_state['current_page']='final_model'
        st.rerun()
    
    with st.sidebar:
        page=option_menu(
            menu_title='Menu',
            menu_icon='columns-gap',
            options=['Home','Register Events','Recommend','View Events'],
            icons=['house-fill','table','caret-right-fill','bullseye'],
            default_index=1,
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
        pass
    elif page=='Home':
        st.session_state['current_page']='page1'
        st.rerun()
    elif page=='Recommend':
        st.session_state['current_page']='final_model'
        st.rerun()
    elif page=='View Events':
        st.session_state['current_page']='view'
        st.rerun()
    
    
import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from streamlit_option_menu import option_menu
import psycopg2

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
        }}
        </style>
        """,
        unsafe_allow_html=True,)
    
def exist(user_email,event_name):
    con=psycopg2.connect(
          host='localhost',
          user='admin',
          password='admin',
          database='pro_expo',
          port='5432'
    )
    cur=con.cursor()
    check='''
    select email_id from registration 
    where Event_Name=%s;'''
    cur.execute(check,(event_name,))
    rows=cur.fetchall()
    for i in rows:
        print(i,user_email)
        if i[0]==user_email:
            cur.close()
            con.close()
            print(1)
            return True
    else:
        cur.close()
        con.close()
        print(0)
        return False

def insert(user_email,event_name):

    con=psycopg2.connect(
        host='localhost',
        user='admin',
        password='admin',
        database='pro_expo',
        port='5432'
    )
    cur=con.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS registration (
        id SERIAL PRIMARY KEY,
        email_id varchar(50)NOT NULL,
        Event_Name VARCHAR(50)
    );
    """
    cur.execute(create_table_query)
    con.commit()

    insert_query = """
    INSERT INTO registration (email_id,Event_Name) VALUES (%s, %s);
    """
    if not exist(user_email,event_name):
        print("done")
        cur.execute(insert_query,(user_email,event_name))
        con.commit()
        cur.close()
        con.close()
        print(1)
        return True
    else:
        cur.close()
        con.close()
        print(0)
        return False




def send_registration_email(user_email, user_name, event_name,date):
    if insert(user_email,event_name):
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
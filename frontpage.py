import streamlit as st
import page1,page2,search,view
import final_model,Registratio

st.set_page_config(
    page_title='Event.com',
    page_icon='🎫'
)
# Initialize the session state for the current page
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'page1'  # default to Page 1

# Load the appropriate page based on the current page state
if st.session_state['current_page']=='page1':
    page1.show()  # Load Page 1 content
elif st.session_state['current_page']=='page2':
    page2.show()  # Load Page 2 content
elif st.session_state['current_page']=='final_model':
    final_model.show()
elif st.session_state['current_page']=='search_bar':
    search.show()
elif st.session_state['current_page']=='direct_reg':
    mail=st.session_state['user_mail']
    name=st.session_state['name']
    mon=st.session_state['Month']
    eve_name=st.session_state['event_name']
    page2.show()
elif st.session_state['current_page']=='reg_form':
    Registratio.show()
elif st.session_state['current_page']=='view':
    view.show()


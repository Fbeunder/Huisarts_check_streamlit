import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import json

# Import modules
from modules.auth_service import AuthService
from modules.data_layer import DataLayer
from modules.website_checker import WebsiteChecker

# Initialize services
@st.cache_resource
def initialize_services():
    data_layer = DataLayer()
    auth_service = AuthService(data_layer)
    website_checker = WebsiteChecker(data_layer)
    return data_layer, auth_service, website_checker

data_layer, auth_service, website_checker = initialize_services()

# Page config
st.set_page_config(
    page_title="Huisartsenpraktijken - Huisarts Check",
    page_icon="🏥",
    layout="wide"
)

# Check if user is logged in
if 'user' not in st.session_state or not st.session_state.user:
    st.warning("Je bent niet ingelogd. Ga terug naar de hoofdpagina om in te loggen.")
    st.page_link("/", label="Terug naar inloggen", icon="🏠")
    st.stop()

# Page title
st.title("Huisartsenpraktijken")

# Get user data
user = st.session_state.user
practices = data_layer.get_practices_by_user(user['userId'])

# Function to add a new practice
def add_practice():
    practice = {
        'practiceId': str(uuid.uuid4()),
        'userId': user['userId'],
        'name': st.session_state.practice_name,
        'websiteUrl': st.session_state.practice_url,
        'status': 'UNKNOWN',
        'lastChecked': None,
        'lastStatusChange': None,
        'details': json.dumps({})
    }
    
    result = data_layer.create_practice(practice)
    if result:
        st.session_state.show_add_form = False
        st.session_state.practice_name = ""
        st.session_state.practice_url = ""
        st.success("Huisartsenpraktijk toegevoegd!")
        st.rerun()

# Function to edit a practice
def update_practice():
    updates = {
        'name': st.session_state.edit_practice_name,
        'websiteUrl': st.session_state.edit_practice_url
    }
    
    result = data_layer.update_practice(st.session_state.edit_practice_id, updates)
    if result:
        st.session_state.show_edit_form = False
        st.session_state.edit_practice_id = None
        st.session_state.edit_practice_name = ""
        st.session_state.edit_practice_url = ""
        st.success("Huisartsenpraktijk bijgewerkt!")
        st.rerun()

# Initialize session state variables
if 'show_add_form' not in st.session_state:
    st.session_state.show_add_form = False

if 'show_edit_form' not in st.session_state:
    st.session_state.show_edit_form = False

if 'edit_practice_id' not in st.session_state:
    st.session_state.edit_practice_id = None

# Control buttons
col1, col2 = st.columns([1, 3])
with col1:
    if not st.session_state.show_add_form:
        if st.button("Nieuwe praktijk toevoegen", type="primary"):
            st.session_state.show_add_form = True
            st.session_state.show_edit_form = False

# Add practice form
if st.session_state.show_add_form:
    st.subheader("Nieuwe huisartsenpraktijk toevoegen")
    with st.form("add_practice_form"):
        st.text_input("Naam", key="practice_name")
        st.text_input("Website URL", key="practice_url", placeholder="https://example.com")
        col1, col2 = st.columns([1, 3])
        with col1:
            submit = st.form_submit_button("Toevoegen")
        with col2:
            if st.form_submit_button("Annuleren"):
                st.session_state.show_add_form = False
                st.rerun()
        
        if submit:
            if not st.session_state.practice_name or not st.session_state.practice_url:
                st.error("Vul alle velden in.")
            else:
                add_practice()

# Edit practice form
if st.session_state.show_edit_form and st.session_state.edit_practice_id:
    practice = data_layer.get_practice_by_id(st.session_state.edit_practice_id)
    if practice:
        st.subheader(f"Bewerk {practice['name']}")
        with st.form("edit_practice_form"):
            st.text_input("Naam", value=practice['name'], key="edit_practice_name")
            st.text_input("Website URL", value=practice['websiteUrl'], key="edit_practice_url")
            col1, col2 = st.columns([1, 3])
            with col1:
                submit = st.form_submit_button("Opslaan")
            with col2:
                if st.form_submit_button("Annuleren"):
                    st.session_state.show_edit_form = False
                    st.session_state.edit_practice_id = None
                    st.rerun()
            
            if submit:
                if not st.session_state.edit_practice_name or not st.session_state.edit_practice_url:
                    st.error("Vul alle velden in.")
                else:
                    update_practice()

# Practice list
st.subheader("Huisartsenpraktijken")
if not practices:
    st.info("Je hebt nog geen huisartsenpraktijken toegevoegd.")
else:
    # Create dataframe for table display
    practice_data = []
    for p in practices:
        # Format status for display
        status_icon = "🟢" if p.get('status') == 'ACCEPTING' else \
                      "🔴" if p.get('status') == 'NOT_ACCEPTING' else \
                      "⚪"
        status_display = "Open voor inschrijving" if p.get('status') == 'ACCEPTING' else \
                         "Gesloten voor inschrijving" if p.get('status') == 'NOT_ACCEPTING' else \
                         "Onbekend"
        
        # Format last checked date
        last_checked = p.get('lastChecked', '')
        if last_checked:
            try:
                dt = datetime.fromisoformat(last_checked.replace('Z', '+00:00'))
                last_checked = dt.strftime("%d-%m-%Y %H:%M")
            except:
                pass
        
        practice_data.append({
            'Status': status_icon,
            'Naam': p.get('name', ''),
            'Website': p.get('websiteUrl', ''),
            'Status Tekst': status_display,
            'Laatst gecontroleerd': last_checked,
            'ID': p.get('practiceId')  # Hidden column for reference
        })
    
    # Create table
    practice_df = pd.DataFrame(practice_data)
    
    # Display table
    for i, row in practice_df.iterrows():
        col1, col2, col3, col4 = st.columns([0.1, 1.7, 2, 0.7])
        with col1:
            st.write(row['Status'])
        with col2:
            st.write(f"**{row['Naam']}**")
        with col3:
            st.write(row['Website'])
        with col4:
            check_button_key = f"check_{row['ID']}"
            edit_button_key = f"edit_{row['ID']}"
            delete_button_key = f"delete_{row['ID']}"
            
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            with btn_col1:
                if st.button("✓", key=check_button_key, help="Controleer deze praktijk"):
                    with st.spinner(f"Controleren van {row['Naam']}..."):
                        result = website_checker.check_single_website(
                            row['Website'],
                            user['userId'],
                            row['ID']
                        )
                        
                        if result['success']:
                            status_text = "open voor inschrijving" if result['status'] == 'ACCEPTING' else \
                                         "gesloten voor inschrijving" if result['status'] == 'NOT_ACCEPTING' else \
                                         "onbekende status"
                            
                            if result.get('statusChanged'):
                                st.success(f"Status is gewijzigd! {row['Naam']} is nu {status_text}.")
                            else:
                                st.info(f"Status ongewijzigd. {row['Naam']} is {status_text}.")
                        else:
                            st.error(f"Fout bij controleren van praktijk: {result.get('message', 'Onbekende fout')}")
                        
                        # Refresh practices
                        st.rerun()
            with btn_col2:
                if st.button("🖊️", key=edit_button_key, help="Bewerk deze praktijk"):
                    st.session_state.show_edit_form = True
                    st.session_state.edit_practice_id = row['ID']
                    st.session_state.show_add_form = False
                    st.rerun()
            with btn_col3:
                if st.button("🗑️", key=delete_button_key, help="Verwijder deze praktijk"):
                    if data_layer.delete_practice(row['ID']):
                        st.success(f"{row['Naam']} verwijderd.")
                        st.rerun()
                    else:
                        st.error(f"Fout bij verwijderen van {row['Naam']}.")
        
        status_text = row['Status Tekst']
        last_checked = row['Laatst gecontroleerd'] if row['Laatst gecontroleerd'] else "Nog niet gecontroleerd"
        st.caption(f"{status_text} | Laatst gecontroleerd: {last_checked}")
        st.divider()
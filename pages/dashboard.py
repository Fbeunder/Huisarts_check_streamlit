import streamlit as st
import pandas as pd
from datetime import datetime
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
    page_title="Dashboard - Huisarts Check",
    page_icon="📊",
    layout="wide"
)

# Check if user is logged in
if 'user' not in st.session_state or not st.session_state.user:
    st.warning("Je bent niet ingelogd. Ga terug naar de hoofdpagina om in te loggen.")
    st.page_link("/", label="Terug naar inloggen", icon="🏠")
    st.stop()

# Page title
st.title("Dashboard")

# Get user data
user = st.session_state.user
practices = data_layer.get_practices_by_user(user['userId'])

# Top metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Totaal huisartsen", len(practices))
with col2:
    accepting_count = sum(1 for p in practices if p.get('status') == 'ACCEPTING')
    st.metric("Open voor inschrijving", accepting_count)
with col3:
    not_accepting_count = sum(1 for p in practices if p.get('status') == 'NOT_ACCEPTING')
    st.metric("Gesloten voor inschrijving", not_accepting_count)

# Actions
st.subheader("Acties")
col1, col2 = st.columns(2)
with col1:
    if st.button("Alle praktijken controleren", type="primary"):
        with st.spinner("Controleren van alle praktijken..."):
            result = website_checker.check_all_user_websites(user['userId'])
            if result['success']:
                st.success(f"Controle voltooid: {result['totalChecked']} praktijken gecontroleerd, {result['statusChanges']} statuswijzigingen")
                # Refresh practices data
                practices = data_layer.get_practices_by_user(user['userId'])
            else:
                st.error(f"Fout bij controleren van praktijken: {result['message']}")
with col2:
    st.button("Nieuwe praktijk toevoegen", on_click=lambda: st.switch_page("pages/practices.py"))

# Practice list
st.subheader("Huisartsenpraktijken")
if not practices:
    st.info("Je hebt nog geen huisartsenpraktijken toegevoegd.")
else:
    # Create dataframe for table display
    practice_data = []
    for p in practices:
        # Parse JSON string if needed
        details = p.get('details')
        if isinstance(details, str):
            try:
                details = json.loads(details)
            except:
                details = {}
        
        # Format status for display
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
            'Naam': p.get('name', ''),
            'Website': p.get('websiteUrl', ''),
            'Status': status_display,
            'Laatst gecontroleerd': last_checked,
            'ID': p.get('practiceId')  # Hidden column for reference
        })
    
    # Create table
    practice_df = pd.DataFrame(practice_data)
    
    # Display table with selection
    selected_indices = st.data_editor(
        practice_df.drop(columns=['ID']),
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key="practice_table"
    )
    
    # Check practice button
    if st.button("Geselecteerde praktijk controleren"):
        if st.session_state.practice_table.get('edited_rows'):
            selected_row = list(st.session_state.practice_table['edited_rows'].keys())[0]
            practice_id = practice_data[selected_row]['ID']
            practice = data_layer.get_practice_by_id(practice_id)
            
            with st.spinner(f"Controleren van {practice['name']}..."):
                result = website_checker.check_single_website(
                    practice['websiteUrl'],
                    user['userId'],
                    practice_id
                )
                
                if result['success']:
                    status_text = "open voor inschrijving" if result['status'] == 'ACCEPTING' else \
                                 "gesloten voor inschrijving" if result['status'] == 'NOT_ACCEPTING' else \
                                 "onbekende status"
                    
                    if result.get('statusChanged'):
                        st.success(f"Status is gewijzigd! {practice['name']} is nu {status_text}.")
                    else:
                        st.info(f"Status ongewijzigd. {practice['name']} is {status_text}.")
                    
                    # Show details
                    with st.expander("Details bekijken"):
                        st.json(result)
                else:
                    st.error(f"Fout bij controleren van praktijk: {result.get('message', 'Onbekende fout')}")
        else:
            st.warning("Selecteer eerst een praktijk in de tabel.")

# Recent status changes
st.subheader("Recente statuswijzigingen")
# Mock data for demonstration
status_changes = [
    {
        'practice': 'Huisartsenpraktijk Centrum',
        'timestamp': '2025-03-15T12:00:00Z',
        'oldStatus': 'NOT_ACCEPTING',
        'newStatus': 'ACCEPTING'
    },
    {
        'practice': 'Huisartspraktijk Noord',
        'timestamp': '2025-03-12T09:30:00Z',
        'oldStatus': 'UNKNOWN',
        'newStatus': 'NOT_ACCEPTING'
    }
]

if not status_changes:
    st.info("Geen recente statuswijzigingen.")
else:
    for change in status_changes:
        # Format date
        try:
            dt = datetime.fromisoformat(change['timestamp'].replace('Z', '+00:00'))
            formatted_date = dt.strftime("%d-%m-%Y %H:%M")
        except:
            formatted_date = change['timestamp']
        
        # Format statuses
        old_status = "Open voor inschrijving" if change['oldStatus'] == 'ACCEPTING' else \
                     "Gesloten voor inschrijving" if change['oldStatus'] == 'NOT_ACCEPTING' else \
                     "Onbekend"
        new_status = "Open voor inschrijving" if change['newStatus'] == 'ACCEPTING' else \
                     "Gesloten voor inschrijving" if change['newStatus'] == 'NOT_ACCEPTING' else \
                     "Onbekend"
        
        # Icon based on new status
        icon = "🟢" if change['newStatus'] == 'ACCEPTING' else \
              "🔴" if change['newStatus'] == 'NOT_ACCEPTING' else \
              "⚪"
        
        st.write(f"{icon} **{change['practice']}** is veranderd van {old_status} naar {new_status} op {formatted_date}")
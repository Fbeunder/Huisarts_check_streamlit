import streamlit as st
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Import modules
from modules.auth_service import AuthService
from modules.data_layer import DataLayer
from modules.website_checker import WebsiteChecker

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Huisarts Check",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def initialize_services():
    data_layer = DataLayer()
    auth_service = AuthService(data_layer)
    website_checker = WebsiteChecker(data_layer)
    return data_layer, auth_service, website_checker

data_layer, auth_service, website_checker = initialize_services()

# Set up session state
if 'user' not in st.session_state:
    st.session_state.user = None

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Login/Logout functionality
def login():
    user_email = st.session_state.email
    st.session_state.user = auth_service.get_user_by_email(user_email)
    if st.session_state.user:
        st.session_state.logged_in = True
    else:
        st.session_state.user = auth_service.create_user(user_email)
        st.session_state.logged_in = True

def logout():
    st.session_state.user = None
    st.session_state.logged_in = False

# Sidebar
with st.sidebar:
    st.title("Huisarts Check")
    
    if not st.session_state.logged_in:
        st.subheader("Inloggen")
        st.text_input("E-mail", key="email")
        st.button("Inloggen", on_click=login)
    else:
        st.success(f"Ingelogd als {st.session_state.user['email']}")
        st.button("Uitloggen", on_click=logout)
        
        st.divider()
        st.subheader("Menu")
        st.page_link("pages/dashboard.py", label="Dashboard", icon="📊")
        st.page_link("pages/practices.py", label="Huisartsenpraktijken", icon="🏥")
        st.page_link("pages/settings.py", label="Instellingen", icon="⚙️")
        st.page_link("pages/about.py", label="Over", icon="ℹ️")

# Main content
if not st.session_state.logged_in:
    st.title("Welkom bij Huisarts Check")
    st.write("""
    Deze applicatie helpt je bij het monitoren van huisartsenpraktijk websites 
    om te controleren of ze nieuwe patiënten aannemen. 
    
    Log in om te beginnen.
    """)
    st.image("https://images.unsplash.com/photo-1579684385127-1ef15d508118?q=80&w=2080", caption="Huisarts Check")
else:
    st.title(f"Welkom, {st.session_state.user['email']}")
    st.write("""
    Gebruik het menu links om te navigeren:
    - **Dashboard** toont een overzicht van je huisartsenpraktijken
    - **Huisartsenpraktijken** voor het beheren van je praktijken
    - **Instellingen** voor het aanpassen van je voorkeuren
    - **Over** voor informatie over deze applicatie
    """)
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    with col1:
        practices = data_layer.get_practices_by_user(st.session_state.user['userId'])
        st.metric("Huisartsenpraktijken", len(practices))
    with col2:
        accepting_count = sum(1 for p in practices if p.get('status') == 'ACCEPTING')
        st.metric("Open voor inschrijving", accepting_count)
    with col3:
        not_accepting_count = sum(1 for p in practices if p.get('status') == 'NOT_ACCEPTING')
        st.metric("Gesloten voor inschrijving", not_accepting_count)
    
    # Recent practices
    if practices:
        st.subheader("Recent toegevoegde huisartsenpraktijken")
        for practice in practices[:3]:
            status_color = "🟢" if practice.get('status') == 'ACCEPTING' else "🔴" if practice.get('status') == 'NOT_ACCEPTING' else "⚪"
            st.write(f"{status_color} **{practice.get('name')}** - {practice.get('websiteUrl')}")
        st.button("Alle huisartsenpraktijken bekijken", type="primary", help="Ga naar de pagina met huisartsenpraktijken")
    else:
        st.info("Je hebt nog geen huisartsenpraktijken toegevoegd. Ga naar 'Huisartsenpraktijken' om te beginnen.")
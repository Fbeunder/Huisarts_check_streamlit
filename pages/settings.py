import streamlit as st

# Import modules
from modules.auth_service import AuthService
from modules.data_layer import DataLayer

# Initialize services
@st.cache_resource
def initialize_services():
    data_layer = DataLayer()
    auth_service = AuthService(data_layer)
    return data_layer, auth_service

data_layer, auth_service = initialize_services()

# Page config
st.set_page_config(
    page_title="Instellingen - Huisarts Check",
    page_icon="⚙️",
    layout="wide"
)

# Check if user is logged in
if 'user' not in st.session_state or not st.session_state.user:
    st.warning("Je bent niet ingelogd. Ga terug naar de hoofdpagina om in te loggen.")
    st.page_link("/", label="Terug naar inloggen", icon="🏠")
    st.stop()

# Page title
st.title("Instellingen")

# Get user data
user = st.session_state.user
settings = user.get('settings', {
    'emailNotifications': True,
    'notificationFrequency': 'immediately'
})

# Function to save settings
def save_settings():
    updated_settings = {
        'emailNotifications': st.session_state.email_notifications,
        'notificationFrequency': st.session_state.notification_frequency
    }
    
    result = auth_service.update_user_settings(user['userId'], updated_settings)
    if result:
        # Update session state
        user['settings'] = updated_settings
        st.session_state.user = user
        return True
    return False

# Settings form
with st.form(key='settings_form'):
    st.subheader("Notificatie-instellingen")
    
    # Email notifications toggle
    email_notifications = st.toggle(
        "E-mailnotificaties ontvangen", 
        value=settings.get('emailNotifications', True),
        key="email_notifications",
        help="Ontvang e-mails wanneer een huisarts van status verandert"
    )
    
    # Notification frequency
    notification_frequency = st.selectbox(
        "Notificatiefrequentie",
        options=["immediately", "daily", "weekly"],
        format_func=lambda x: {
            "immediately": "Direct",
            "daily": "Dagelijks (samenvatting)",
            "weekly": "Wekelijks (samenvatting)"
        }.get(x, x),
        index=["immediately", "daily", "weekly"].index(settings.get('notificationFrequency', 'immediately')),
        key="notification_frequency",
        help="Hoe vaak wil je notificaties ontvangen?",
        disabled=not email_notifications
    )
    
    st.divider()
    
    submit_button = st.form_submit_button(label="Instellingen opslaan")
    
    if submit_button:
        if save_settings():
            st.success("Instellingen succesvol opgeslagen!")
        else:
            st.error("Er is een fout opgetreden bij het opslaan van de instellingen.")

# Apps Script connection settings (only for admins)
if user.get('isAdmin', False):
    st.subheader("Systeeminstellingen (Admin)")
    
    apps_script_url = st.text_input(
        "Apps Script URL voor OpenAI-integratie", 
        value=st.session_state.get('apps_script_url', ''), 
        placeholder="https://script.google.com/macros/s/....",
        help="URL van het gedeployde Apps Script dat communiceert met OpenAI"
    )
    
    spreadsheet_id = st.text_input(
        "Google Spreadsheet ID", 
        value=st.session_state.get('spreadsheet_id', ''),
        placeholder="1AbC...",
        help="ID van de Google Spreadsheet die als database dient"
    )
    
    if st.button("Systeeminstellingen opslaan"):
        # In a real application, this would save to environment variables or secure storage
        st.session_state['apps_script_url'] = apps_script_url
        st.session_state['spreadsheet_id'] = spreadsheet_id
        st.success("Systeeminstellingen opgeslagen!")
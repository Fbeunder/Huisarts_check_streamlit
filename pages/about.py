import streamlit as st

# Page config
st.set_page_config(
    page_title="Over - Huisarts Check",
    page_icon="ℹ️",
    layout="wide"
)

# Page title
st.title("Over Huisarts Check")

# Application information
st.markdown("""
## Wat is Huisarts Check?

Huisarts Check is een applicatie die huisartsenpraktijk websites monitort om te controleren of 
 ze nieuwe patiënten aannemen. Gebruikers kunnen een persoonlijke lijst met URLs van huisartsen 
 opgeven en worden via e-mail op de hoogte gebracht wanneer een huisarts van status verandert 
 naar het aannemen van nieuwe patiënten.

## Hoe werkt het?

1. **Registreer** - Log in met je e-mailadres
2. **Voeg huisartsen toe** - Voeg de websites van huisartsen in jouw omgeving toe
3. **Automatische controle** - De applicatie controleert regelmatig of de status is veranderd
4. **Notificaties** - Ontvang een e-mail zodra een huisarts nieuwe patiënten aanneemt

## Technische informatie

Deze applicatie is gebouwd met:
- **Frontend**: Streamlit
- **Backend**: Google Apps Script (voor OpenAI-integratie)
- **Database**: Google Sheets
- **AI**: OpenAI API voor het analyseren van websites

## Versie

Versie 1.0.0

## Contact

Voor vragen of suggesties, neem contact op via [email@example.com](mailto:email@example.com).
""")

# Creator information
st.divider()
st.write("Gemaakt door Stan de GitHub Agent, 2025")
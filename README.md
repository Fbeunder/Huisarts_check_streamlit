# Huisarts Check - Streamlit versie

Een Streamlit-applicatie die huisartsenpraktijk websites monitort om te controleren of ze nieuwe patiënten aannemen. Gebruikers kunnen zich aanmelden, een persoonlijke lijst met URLs van huisartsen opgeven, en worden via e-mail op de hoogte gebracht wanneer een huisarts van status verandert naar het aannemen van nieuwe patiënten.

## Eigenschappen

- **Gebruikersbeheer**: Log in met je e-mailadres
- **Huisartsenpraktijk beheer**: Voeg huisartsenpraktijken toe, bewerk en verwijder ze
- **Website monitoring**: Controleer websites op status (accepteert nieuwe patiënten of niet)
- **AI-analyse**: Gebruikt OpenAI via Google Apps Script om websites te analyseren
- **E-mailnotificaties**: Ontvang berichten wanneer een huisarts van status verandert
- **Streamlit interface**: Gebruiksvriendelijke web-interface

## Architectuur

Deze applicatie is opgebouwd volgens een modulaire structuur:

1. **Streamlit Frontend**
   - app.py (Hoofdapplicatie)
   - Pages (Dashboard, Praktijken, Instellingen, Over)

2. **Modules**
   - auth_service.py (Gebruikersbeheer)
   - data_layer.py (Database interacties)
   - website_checker.py (Website controle functionaliteit)
   - openai_bridge.py (Integratie met OpenAI via Apps Script)
   - email_service.py (Email notificatie service)
   - logger.py (Logging functionaliteit)

3. **Externe diensten**
   - Google Sheets (Database)
   - Google Apps Script (Bridge naar OpenAI)
   - OpenAI (Website-analyse)

## Installatie

### Vereisten

- Python 3.9+
- Google account met toegang tot Google Sheets en Apps Script
- OpenAI API sleutel

### Stappen

1. Clone de repository:
   ```
   git clone https://github.com/Fbeunder/Huisarts_check_streamlit.git
   cd Huisarts_check_streamlit
   ```

2. Installeer de vereiste packages:
   ```
   pip install -r requirements.txt
   ```

3. Configureer de .env file:
   - Kopieer .env.example naar .env
   - Vul de vereiste gegevens in
   ```
   cp .env.example .env
   ```

4. Stel de Google Sheets API in:
   - Maak een Google Cloud project aan
   - Schakel Google Sheets API in
   - Maak een service account aan en download de credentials als google_credentials.json

5. Stel Google Apps Script in voor OpenAI integratie:
   - Kopieer het Apps Script uit de originele repository
   - Implementeer het script en noteer de gedeployde URL
   - Voeg de OpenAI API-sleutel toe aan de scriptProperties

6. Start de applicatie:
   ```
   streamlit run app.py
   ```

## Google Apps Script voor OpenAI integratie

Deze Streamlit-applicatie gebruikt een Google Apps Script als bridge naar de OpenAI API. Volg deze stappen om het script op te zetten:

1. Open [Google Apps Script](https://script.google.com/)
2. Maak een nieuw project
3. Kopieer de inhoud van [OpenAIService.gs](https://github.com/Fbeunder/Huisarts_check/blob/main/OpenAIService.gs) uit de originele repository
4. Implementeer het script als web-app (toegankelijk voor iedereen)
5. Voeg de OpenAI API-sleutel toe aan de script properties

Zie de originele repository voor meer details over het Apps Script.

## Gebruik

1. Open de applicatie in je browser
2. Log in met je e-mailadres
3. Ga naar 'Huisartsenpraktijken' om praktijken toe te voegen
4. Gebruik het dashboard om een overzicht te krijgen en controles uit te voeren
5. Pas je notificatie-instellingen aan via de instellingenpagina

## Licentie

MIT
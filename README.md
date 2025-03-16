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

5. Stel Google Apps Script in voor OpenAI integratie (zie gedetailleerde instructies hieronder)

6. Start de applicatie:
   ```
   streamlit run app.py
   ```

## Gedetailleerde instructies voor Google Apps Script setup

De Streamlit-applicatie communiceert met OpenAI via een Google Apps Script als "bridge" om de API-sleutels veilig te beheren. Volg deze stappen om het Google Apps Script te configureren:

### 1. Maak een nieuw Google Apps Script project

1. Ga naar [Google Apps Script](https://script.google.com/)
2. Klik op "Nieuw project"
3. Geef het project een naam (bijv. "Huisarts Check OpenAI Bridge")

### 2. Voeg de OpenAI bridge code toe

Kopieer de volgende code naar het script:

```javascript
// OpenAI Bridge voor Huisarts Check
// Deze script dient als veilige bridge tussen de Streamlit applicatie en de OpenAI API

// Setup constants
const OPENAI_API_KEY = PropertiesService.getScriptProperties().getProperty('OPENAI_API_KEY');
const OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions';
const MODEL = 'gpt-4'; // Of een ander geschikt model

/**
 * Verwerkt een POST-verzoek van de Streamlit applicatie
 * @param {Object} e - Het HTTP-verzoekobject
 * @return {Object} HTTP-antwoord
 */
function doPost(e) {
  try {
    // Controleer of er een verzoekobject is
    if (!e || !e.postData || !e.postData.contents) {
      return createErrorResponse('Ongeldig verzoek');
    }

    // Parse de verzoekgegevens
    const requestData = JSON.parse(e.postData.contents);
    
    // Valideer het verzoek
    if (!requestData.action) {
      return createErrorResponse('Geen actie opgegeven');
    }
    
    // Route het verzoek naar de juiste functie
    switch (requestData.action) {
      case 'testConnection':
        return createSuccessResponse({
          message: 'Verbinding met Google Apps Script is succesvol'
        });
      
      case 'analyzeWebsite':
        return analyzeWebsite(requestData);
      
      default:
        return createErrorResponse(`Onbekende actie: ${requestData.action}`);
    }
  } catch (error) {
    console.error(`Fout bij verwerken verzoek: ${error.message}`);
    return createErrorResponse(`Fout bij verwerken verzoek: ${error.message}`);
  }
}

/**
 * Analyseert een website met behulp van OpenAI
 * @param {Object} requestData - Verzoekgegevens
 * @return {Object} HTTP-antwoord
 */
function analyzeWebsite(requestData) {
  try {
    // Valideer verzoekgegevens
    if (!requestData.url) {
      return createErrorResponse('Geen URL opgegeven');
    }

    // Controleer of OpenAI API-sleutel is geconfigureerd
    if (!OPENAI_API_KEY) {
      return createErrorResponse('OpenAI API-sleutel niet geconfigureerd');
    }

    // Bereid prompt voor
    const prompt = createPromptForWebsite(requestData.url);
    
    // Roep OpenAI API aan
    const openAIResponse = callOpenAI(prompt);
    
    // Verwerk en retourneer het resultaat
    const analysisResult = processOpenAIResponse(openAIResponse, requestData.url);
    return createSuccessResponse(analysisResult);
    
  } catch (error) {
    console.error(`Fout bij analyseren website: ${error.message}`);
    return createErrorResponse(`Fout bij analyseren website: ${error.message}`);
  }
}

/**
 * Maakt een prompt voor OpenAI om een website te analyseren
 * @param {string} url - De te analyseren website URL
 * @return {string} De prompt voor OpenAI
 */
function createPromptForWebsite(url) {
  const websiteContent = fetchWebsiteContent(url);
  
  return [
    {
      "role": "system",
      "content": "Je bent een assistent die websites van huisartsen analyseert om te bepalen of ze nieuwe patiënten aannemen. Geef een gestructureerde JSON-response met de sleutels: status (ACCEPTING, NOT_ACCEPTING, UNKNOWN), confidence (0-100), details (object met relevante info) en reasoning (korte uitleg)."
    },
    {
      "role": "user",
      "content": `Analyseer de volgende website inhoud van ${url} en bepaal of de huisartsenpraktijk nieuwe patiënten aanneemt. Return alleen een JSON object zoals beschreven in de system prompt. Website inhoud: ${websiteContent}`
    }
  ];
}

/**
 * Haalt de inhoud van een website op
 * @param {string} url - De URL van de website
 * @return {string} De inhoud van de website
 */
function fetchWebsiteContent(url) {
  try {
    // Probeer de website op te halen met UrlFetchApp
    const response = UrlFetchApp.fetch(url, {
      muteHttpExceptions: true,
      followRedirects: true
    });
    
    // Controleer HTTP-statuscode
    if (response.getResponseCode() >= 400) {
      console.warn(`Fout bij ophalen website ${url}: HTTP ${response.getResponseCode()}`);
      return `Kon de inhoud niet ophalen. HTTP-statuscode: ${response.getResponseCode()}`;
    }
    
    // Bepaal het content type
    const contentType = response.getHeaders()['Content-Type'] || '';
    
    // Als het HTML is, probeer alleen de relevante tekst te extraheren
    if (contentType.includes('text/html')) {
      const htmlContent = response.getContentText();
      
      // Eenvoudige HTML-cleaning (dit is niet perfect, maar werkt voor basistekst)
      let cleanedContent = htmlContent
        .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, ' ')
        .replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, ' ')
        .replace(/<[^>]*>/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
      
      // Beperk de lengte om binnen de OpenAI tokenlimiet te blijven
      if (cleanedContent.length > 8000) {
        cleanedContent = cleanedContent.substring(0, 8000) + '... [inhoud afgekapt wegens lengte]';
      }
      
      return cleanedContent;
    }
    
    // Voor andere content types, retourneer een bericht
    return `Website heeft content type: ${contentType}. Inhoud niet geanalyseerd.`;
    
  } catch (error) {
    console.error(`Fout bij ophalen website ${url}: ${error.message}`);
    return `Kon de inhoud niet ophalen: ${error.message}`;
  }
}

/**
 * Roept de OpenAI API aan
 * @param {Array} messages - De berichten voor de conversatie
 * @return {Object} Het antwoord van OpenAI
 */
function callOpenAI(messages) {
  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: {
      'Authorization': `Bearer ${OPENAI_API_KEY}`
    },
    payload: JSON.stringify({
      model: MODEL,
      messages: messages,
      temperature: 0.2,
      max_tokens: 800
    }),
    muteHttpExceptions: true
  };
  
  const response = UrlFetchApp.fetch(OPENAI_API_URL, options);
  const responseCode = response.getResponseCode();
  
  if (responseCode !== 200) {
    const error = JSON.parse(response.getContentText());
    console.error(`OpenAI API fout: ${error.error.message}`);
    throw new Error(`OpenAI API fout (${responseCode}): ${error.error.message}`);
  }
  
  return JSON.parse(response.getContentText());
}

/**
 * Verwerkt het antwoord van OpenAI
 * @param {Object} openAIResponse - Het antwoord van OpenAI
 * @param {string} url - De geanalyseerde URL
 * @return {Object} Het gestructureerde analyseresultaat
 */
function processOpenAIResponse(openAIResponse, url) {
  try {
    // Haal de content uit het antwoord
    const content = openAIResponse.choices[0].message.content;
    
    // Probeer het als JSON te parsen
    let result;
    try {
      result = JSON.parse(content);
    } catch (e) {
      // Als het geen JSON is, zoek dan naar een JSON-object in de tekst
      const jsonMatch = content.match(/({[\s\S]*})/);
      if (jsonMatch) {
        result = JSON.parse(jsonMatch[0]);
      } else {
        throw new Error('Kon geen JSON vinden in het OpenAI-antwoord');
      }
    }
    
    // Voeg metadata toe
    result.url = url;
    result.timestamp = new Date().toISOString();
    result.success = true;
    
    return result;
    
  } catch (error) {
    console.error(`Fout bij verwerken OpenAI-antwoord: ${error.message}`);
    return {
      success: false,
      status: 'UNKNOWN',
      message: `Fout bij verwerken OpenAI-antwoord: ${error.message}`,
      url: url,
      timestamp: new Date().toISOString()
    };
  }
}

/**
 * Maakt een succesvol HTTP-antwoord
 * @param {Object} data - De te retourneren gegevens
 * @return {Object} HTTP-antwoord
 */
function createSuccessResponse(data) {
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Maakt een fout-HTTP-antwoord
 * @param {string} message - De foutmelding
 * @return {Object} HTTP-antwoord
 */
function createErrorResponse(message) {
  return ContentService.createTextOutput(JSON.stringify({
    success: false,
    message: message
  }))
    .setMimeType(ContentService.MimeType.JSON);
}
```

### 3. Configureer de OpenAI API-sleutel

1. Klik in het Google Apps Script editor menu op "Project eigenschappen"
2. Ga naar het tabblad "Scripteigenschappen"
3. Klik op "Toevoegen"
4. Voeg de eigenschap toe:
   - Naam: `OPENAI_API_KEY`
   - Waarde: [Jouw OpenAI API-sleutel]

### 4. Implementeer het script als webapplicatie

1. Klik op "Implementeren" > "Nieuw implementatie"
2. Kies "Webapplicatie" als type
3. Vul de volgende gegevens in:
   - Beschrijving: "Huisarts Check OpenAI Bridge"
   - Uitvoeren als: "Ik" (of je e-mailadres)
   - Toegang tot: "Iedereen" (of "Iedereen binnen [jouw organisatie]" als je een beperktere toegang wilt)
4. Klik op "Implementeren"
5. Kopieer de URL die wordt weergegeven - dit is je `APPS_SCRIPT_URL`

### 5. Configureer de URL in je .env bestand

Open je `.env` bestand en voeg de URL toe:

```
APPS_SCRIPT_URL=https://script.google.com/macros/s/your-deployed-script-id/exec
```

### 6. Test de verbinding

Gebruik het meegeleverde testscript om te controleren of de verbinding werkt:

```
python test_openai_bridge.py
```

Indien nodig, kun je een website URL opgeven om te testen:

```
python test_openai_bridge.py https://www.example-huisarts.nl
```

## Google Sheets setup

De applicatie gebruikt Google Sheets als database. Volg deze stappen om dit in te stellen:

1. Maak een nieuw Google Spreadsheet aan of gebruik een bestaande
2. Noteer het Spreadsheet ID (dit is het lange alfanumerieke deel in de URL)
3. Voeg het ID toe aan je `.env` bestand:
   ```
   SPREADSHEET_ID=your_spreadsheet_id_here
   ```

## Email notificaties

De applicatie kan e-mailnotificaties verzenden wanneer de status van een huisartsenpraktijk verandert. Zie de instellingenpagina in de applicatie voor meer details.

## Gebruik

1. Open de applicatie in je browser
2. Log in met je e-mailadres
3. Ga naar 'Huisartsenpraktijken' om praktijken toe te voegen
4. Gebruik het dashboard om een overzicht te krijgen en controles uit te voeren
5. Pas je notificatie-instellingen aan via de instellingenpagina

## Licentie

MIT
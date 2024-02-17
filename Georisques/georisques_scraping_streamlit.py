import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO

# Function to process each partner name and fetch the required data
def fetch_data(nom_du_partenaire):
    url = "https://georisques.gouv.fr/webappReport/ws/installations/sites/_search"
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9,fr-FR;q=0.8,fr;q=0.7',
        'origin': 'https://www.georisques.gouv.fr',
        'referer': 'https://www.georisques.gouv.fr/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    params = {
        'page': '1',
        'etablissement': nom_du_partenaire,
        'fieldOrderBy': 'etab',
        'orderByAsc': 'true',
        'size': '10',
        'start': '0'
    }
    
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    if data.get("data"):
        numero_inspection = data["data"][0].get("numeroInspection", "")
        detail_url = f"https://www.georisques.gouv.fr/risques/installations/donnees/details/{numero_inspection}"
        response = requests.get(detail_url)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'lxml')
        tbodies = soup.find_all('tbody')
        
        second_td_content = ''
        if len(tbodies) >= 2:
            second_tbody = tbodies[1]
            tds = second_tbody.find_all('td')
            if len(tds) >= 2:
                second_td = tds[1]
                second_td_content = second_td.text.strip()
        
        return detail_url, second_td_content
    else:
        return '', ''

# Streamlit app UI starts here
st.title('Scraping Georisques')

# Introductory paragraph
st.write('Ajouter ici un fichier avec la liste des entreprises au format CSV et sous ce modèle là:')

# Link to the template
st.markdown('[Télécharger le modèle de fichier CSV](https://drive.google.com/file/d/1j4Uaw-a0MzScTHs9hopCzwqqmkYpQXxu/view?usp=sharing)', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Ajouter votre fichier CSV", type=['csv'])

if uploaded_file is not None:
    # Read the uploaded CSV file into a DataFrame
    df = pd.read_csv(uploaded_file, delimiter=';')
    
    # Add new columns for 'Detail URL' and 'Second TD Content'
    df['URL'] = ''
    df['Data'] = ''
    
    # Iterate over the DataFrame to process each row
    for index, row in df.iterrows():
        detail_url, second_td_content = fetch_data(row['Nom du partenaire'])
        df.at[index, 'URL'] = detail_url
        df.at[index, 'Data'] = second_td_content
        st.write(f"Processed: {row['Nom du partenaire']}")
    
    # Convert the updated DataFrame to CSV for download
    csv = df.to_csv(index=False, sep=';')
    st.download_button(
        label="Télécharger le fichier CSV mis à jour",
        data=csv,
        file_name='updated_georisques.csv',
        mime='text/csv',
    )

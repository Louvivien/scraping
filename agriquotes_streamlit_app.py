import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Function to fetch and parse data
def fetch_data():
    url = os.getenv('URL')
    headers = json.loads(os.getenv('HEADERS'))

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    scripts = soup.find_all('script', type='text/javascript')
    pattern = re.compile(r'mydata\s*=\s*(\[\{.*?\}\])', re.DOTALL)

    for script in scripts:
        result = pattern.search(script.text)
        if result:
            json_str = result.group(1)
            data = json.loads(json_str)
            return data[:2]  # Return the first two sets of data

# Streamlit app
def main():
    st.title('TOURTEAU COLZA EXPELLER FROID - ROYBON (38)')

    data = fetch_data()

    if data:
        st.json(data)
    else:
        st.write("No data found.")

if __name__ == "__main__":
    main()

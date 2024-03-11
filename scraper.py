import csv
import requests
from bs4 import BeautifulSoup

def scrape_montreal(url: str) -> str:
    """
    Scrapes article content from montreal.ca
    
    Args:
        url (str): url of the montreal.ca article
        
    Returns
        str: Article content of the page.
    """
    
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract text from all <div> elements with class "content-modules"
            div_contents = soup.find_all('div', class_='content-modules')
            
            # Extract text from each <div> and join with ". "
            extracted_text = ". ".join([div.get_text(separator='. ') for div in div_contents])
            
            return extracted_text
        else:
            # Print an error message if the request was not successful
            print("Failed to retrieve the webpage. Status code:", response.status_code)
            return None
    except Exception as e:
        print("Error occurred while scraping URL:", url)
        print("Error:", e)
        return None
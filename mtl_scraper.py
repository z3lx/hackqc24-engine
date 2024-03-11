import csv
import requests
from bs4 import BeautifulSoup

def scrape_text(url):
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

# Function to read URLs from a CSV file
def read_urls_from_csv():
    file_path = 'datasets\\Communiqués de presse\\Communiqués de presse (2023 à aujourd\'hui).csv'
    urls = []
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            if len(row) >= 3:  # Ensure the row has at least 3 columns
                urls.append(row[2])  # Assuming URLs are in the third column
    return urls

# Example usage
urls = read_urls_from_csv()
for url in urls:
    extracted_text = scrape_text(url)
    if extracted_text:
        print("URL:", url)
        print("Extracted text:\n", extracted_text)
        print("\n")

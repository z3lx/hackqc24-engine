from bs4 import BeautifulSoup
import requests
import json
import time
from data_utils import save_txt
import link_getter

def error_wrapper(func, url, **kwargs):
    """
    Wrapper function to handle errors related to requests while running the function.

    Args:
        func (Function): a function that takes a response object and returns a value
        url (str): url of the webpage

    Returns:
        Any: returns the value returned by the function or None if an error occurs
    """
    retries = 5
    retry_time = 60
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return func(response, **kwargs)
        else:
            print(f"Failed to retrieve {url}. Status code:", response.status_code)
            for retry in range(retries):
                print(f"Retrying in {retry_time} seconds...")
                print(f"{retries - retry} retrie(s) left.")
                time.sleep(retry_time)
                response = requests.get(url)
                if response.status_code == 200:
                    return func(response, **kwargs)
        print(f"Couldn't retrieve {url}") 
        return None
    except Exception as e:
        print(f"Error occurred while running {func.__name__}")
        print("Error:", e)
        return None

def scrape_montreal(url: str, path: str) -> str:
    """
    Scrapes article content from montreal.ca
    
    Args:
        url (str): url of the montreal.ca article
        
    Returns
        str: Article content of the page.
    """
    def func(response, path):
        soup = BeautifulSoup(response.text, 'html.parser') # Parse the HTML content
        divs = soup.find_all('div', class_='content-modules') #Get all the divs with the class 'content-modules'
        content = "".join([div.get_text() for div in divs]) #Extract text from each <div>
        metas = soup.find_all('meta') #Extract the metas from the page
        
        #Extract the metadata from the meta tags
        metadata = {}
        for meta in metas:
            if meta.get("property") and meta.get("content"):
                metadata[meta.get("property")] = meta.get("content")
            if meta.get("name") and meta.get("content"):
                metadata[meta.get("name")] = meta.get("content")
                
        save_txt(content, json.dumps(metadata), path)
        return content
    return error_wrapper(func, url, path=path)
    
    

def scrape_quebec(url: str, path: str):
    """
    Scrapes article content from quebec.ca

    Args:
        url (str): url of the quebec.ca article
        path (str): path to save the file
    """
    
    def func(response, path):
        soup = BeautifulSoup(response.text, 'html.parser') # Parse the HTML content
        divs = soup.find_all('div', class_='ce-bodytext') #Get all the divs with the class 'ce-bodytext'  
        content = "".join([div.get_text() for div in divs]) #Extract text from each <div> 
        metas = soup.find_all('meta') #Extract the metas from the page
        
        metadata = {}
        for meta in metas:
            if meta.get("property") and meta.get("content"):
                metadata[meta.get("property")] = meta.get("content")
            if meta.get("name") and meta.get("content"):
                metadata[meta.get("name")] = meta.get("content")
                
        save_txt(content, json.dumps(metadata), path)
        return content
    
    return error_wrapper(func, url, path=path)
    
def scrape_quebec_article_page():
    """
    Goes through every link in quebec.ca and keeps opening links until it finds an article to scrape.
    """
    
    i = 0
    links = link_getter.get_base_links()
    
    for link in links:
        content = requests.get(link).text
        page = BeautifulSoup(content, "html.parser")
        if len(page.find_all("a", class_ = "sous-theme-tous section-link")) == 0:
            scrape_quebec(link, f"chunks/independent_document{i}")
            print(f"Scraping {link}")
            i += 1
        else:
            # Add all the relevant sub-links if the page is not an article
            links.append(link_getter.get_quebec_sub_links(link))

if __name__ == "__main__":
    scrape_quebec_article_page()
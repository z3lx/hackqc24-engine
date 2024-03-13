from bs4 import BeautifulSoup
import requests
import json
from url_getter import extract_base_links
import time
from data_utils import save_txt

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
    retry_time = 5
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
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text from all <div> elements with class "content-modules"
        divs = soup.find_all('div', class_='content-modules')
        
        # Extract text from each <div> and join with ". "
        content = "".join([div.get_text() for div in divs])
        
        #Extract the metas from the page
        metas = soup.find_all('meta')
        
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
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text from all <div> elements with class "ce-bodytext"
        divs = soup.find_all('div', class_='ce-bodytext')
        
        #Extract the metas from the page
        metas = soup.find_all('meta')
        
        # Extract text from each <div> and join with ". "
        content = "".join([div.get_text() for div in divs])
        
        metadata = {}
        for meta in metas:
            if meta.get("property") and meta.get("content"):
                metadata[meta.get("property")] = meta.get("content")
            if meta.get("name") and meta.get("content"):
                metadata[meta.get("name")] = meta.get("content")
                
        save_txt(content, json.dumps(metadata), path)
        return content
    
    return error_wrapper(func, url, path=path)
        
def quebec_sub_url_getter(url:str):
    """
    Gets all the links of a subpage of quebec.ca
    
    Args:
        url (str): link to the subpage containing links.
    """
    links = []
    content = requests.get(url).text
    page = BeautifulSoup(content, "html.parser")
    links_html = page.find_all("a", class_="sous-theme-page-lien")
    for link in links_html:
        #only add the link if it's not already in the list and if it's not from a different domain
        if link.get("href") not in links and link.get("href").startswith("/"):
            links.append(f"https://www.quebec.ca{link.get("href")}")
    return links
    
    
def scrape_quebec_article_page():
    """
    Goes through every link in quebec.ca and keeps opening links until it finds an article to scrape.
    """
    
    index = 0
    links = extract_base_links()
    
    for link in links:
        content = requests.get(link).text
        page = BeautifulSoup(content, "html.parser")
        if len(page.find_all("a", class_ = "sous-theme-tous section-link")) == 0:
            scrape_quebec(link, f"chunks/independent_document{index}")
            print(f"Scraping {link}")
            index+=1
        else:
            links.append(quebec_sub_url_getter(link))

if __name__ == "__main__":
    scrape_quebec_article_page()
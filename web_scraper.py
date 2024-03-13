from bs4 import BeautifulSoup
import requests
import time
from data_utils import save_txt
import link_getter

def get_metadata(soup: BeautifulSoup) -> dict:
    """
    Extracts metadata from a webpage.

    Args:
        soup (BeautifulSoup): a BeautifulSoup object

    Returns:
        dict: metadata extracted from the webpage
    """
    #Extract the metas from the page
    metas = soup.find_all('meta') 
    metadata = {}
    for meta in metas:
        if meta.get("property") and meta.get("content"):
            metadata[meta.get("property")] = meta.get("content")
        if meta.get("name") and meta.get("content"):
            metadata[meta.get("name")] = meta.get("content")
    return metadata

def response_wrapper(response, func: callable, path: str,  save_file: bool = True) -> str:
    """
    Wrapper function to handle the response object obtained from requests.get. 
    It uses the user defined function to extract content from the webpage.

    Args:
        response (_type_): response object obtained from requests.get
        func (callable): a function defined by caller to extract content from the webpage. Takes a BeautifulSoup object and returns a string.
        path (str): path to save the file
        save_file (bool, optional): if True, saves the content to a file. Defaults to True.

    Returns:
        str: Article content of the page.
    """
    soup = BeautifulSoup(response.text, 'html.parser') 
    content = func(soup)     
    if save_file: 
        metadata = get_metadata(soup)
        save_txt(content, metadata, path)
    return content

def error_wrapper(url: str, func: callable,**kwargs):
    """
    Wrapper function to handle errors related to requests while running the function.

    Args:
        func (Function): a function that takes a beautifulsoup object and returns a string
        url (str): url of the webpage

    Returns:
        Any | None: returns the value returned by the function or None if an error occurs
    """
    retries = 5
    retry_time = 120
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response_wrapper(response, func, **kwargs)
        else:
            print(f"Failed to retrieve {url}. Status code:", response.status_code)
            for retry in range(retries):
                print(f"Retrying in {retry_time} seconds...")
                print(f"{retries - retry} retrie(s) left.")
                time.sleep(retry_time)
                response = requests.get(url)
                if response.status_code == 200:
                    return response_wrapper(response, func, **kwargs)
                print(f"Failed to retrieve {url}. Status code:", response.status_code)
        return None
    except Exception as e:
        print(f"Error occurred while running {func.__name__}")
        print("Error:", e)
        return None

def scrape(url: str, func: callable, path: str, save_file: bool = True) -> str:
    """
    General scrape function that accepts a user defined function to extract content from a webpage.

    Args:
        url (str): url of the webpage
        func (callable): a function defined by caller to extract content from the webpage. Takes a BeautifulSoup object and returns a string.
        path (str): path to save the file
        save_file (bool): if True, saves the content to a file. Defaults to True.

    Returns:
        str: Article content of the page.
    """
    return error_wrapper(url, func, path=path, save_file=save_file)

def scrape_montreal(url: str, path: str, save_file: bool = True) -> str:
    """
    Function specifically for scraping montreal.ca articles.
    
    Args:
        url (str): url of the montreal.ca article
        path (str): path to save the file
        save_file (bool): if True, saves the content to a file. Defaults to True.
        
    Returns:
        str: Article content of the page.
    """
    # Specific function to extract content from montreal.ca
    def func(soup: BeautifulSoup) -> str:
        divs = soup.find_all('div', class_='field--name-body')
        content = "\n".join([div.get_text() for div in divs])
        return content
    
    return scrape(url, func, path, save_file)

def scrape_quebec(url: str, path: str, save_file: bool = True) -> str:
    """
    Function specifically for scraping quebec.ca articles.

    Args:
        url (str): url of the quebec.ca article
        path (str): path to save the file
        save_file (bool): if True, saves the content to a file. Defaults to True.
        
    Returns:
        str: Article content of the page.
    """
    
    # Specific function to extract content from quebec.ca
    def func(soup: BeautifulSoup) -> str:
        divs = soup.find_all('div', class_='ce-bodytext')
        content = "\n".join([div.get_text() for div in divs])
        return content
    
    return scrape(url, func, path, save_file)
    
def scrape_quebec_article_page():
    """
    Goes through every link in quebec.ca and keeps opening links until it finds an article to scrape.
    """
    
    i = 0
    links = link_getter.get_base_links()
    if (links == None):
        print("Failed to retrieve links")
        return None
    
    for link in links:
        content = requests.get(link).text
        page = BeautifulSoup(content, "html.parser")
        if len(page.find_all("a", class_ = "sous-theme-tous section-link")) == 0:
            scrape_quebec(link, f"chunks/independent_document{i}")
            print(f"Scraping {link}")
            i += 1
        else:
            # Add all the relevant sub-links if the page is not an article
            sub_links = link_getter.get_quebec_sub_links(link)
            links.extend(sub_links)
            print(f"Opening {link}")
        print(f"{len(links)}\n")

if __name__ == "__main__":
    scrape_quebec_article_page()
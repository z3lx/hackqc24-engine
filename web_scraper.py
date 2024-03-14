import requests
import link_getter
import validators
from error import error_wrapper
from data_utils import save_txt
from bs4 import BeautifulSoup
import os

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
    
    #Error handling
    if not validators.url(url): raise ValueError("The url is not valid")
    if not os.path.exists(path) and save_file:
        print(f"Path {path} does not exist. Creating it...")
        os.makedirs(path)
        
    return error_wrapper(url, response_wrapper, retry_time=120, func=func, path=path, save_file=save_file)

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
    
def scrape_quebec_article_page(save_urls: bool = False):
    """
    Goes through every link in quebec.ca and keeps opening links until it finds an article to scrape.
    
    Args
        save_urls (bool): If true, will save all the urls visited into a txt file
    """
    
    i = 0
    links = link_getter.get_quebec_base_links()
    if (links == None):
        print("Failed to retrieve links")
        return None
    
    for link in links:
        if save_urls:
            with open("all_quebec_urls", "a", encoding="utf-8") as f:
                f.write(f"{link}\n")
                
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
    
    print(f"{len(links)} links in total.")
    
if __name__ == "__main__":
    scrape_quebec_article_page(save_urls=True)
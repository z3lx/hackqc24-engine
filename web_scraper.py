from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain.chains import create_extraction_chain
from langchain_text_splitters import RecursiveCharacterTextSplitter
from data_utils import save_json, save_csv
from bs4 import BeautifulSoup
import requests
import json

def error_wrapper(func, url: str):
    """
    Wrapper function to handle errors related to requests while running the function.

    Args:
        func (Function): a function that takes a response object and returns a value
        url (str): url of the webpage

    Returns:
        Any: returns the value returned by the function or None if an error occurs
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return func(response)
        else:
            print("Failed to retrieve the webpage. Status code:", response.status_code)
            return None
    except Exception as e:
        print(f"Error occurred while running {func.__name__}")
        print("Error:", e)
        return None

def scrape_montreal(url: str) -> str:
        
    """
    Scrapes article content from montreal.ca
    
    Args:
        url (str): url of the montreal.ca article
        
    Returns
        str: Article content of the page.
    """
    def func(response):
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text from all <div> elements with class "content-modules"
        div_contents = soup.find_all('div', class_='content-modules')
        
        # Extract text from each <div> and join with ". "
        extracted_text = ". ".join([div.get_text(separator='. ') for div in div_contents])
        
        return extracted_text
    return error_wrapper(func, url)
    
    
def extract_links(url: str, base_url: str, verbose: bool = False) -> list:
        """
        Extract links from all the urls without using ai.

        Args:
            verbose (bool, optional): If True, returns a list of dictionaries with the url and the links. Defaults to False.

        Returns:
            list: list of links
        """
        
        response = requests.get(url)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        links = soup.find_all("a")
        formatted_links = []
        for link in links:
            href = link.get('href')
            if href:
                if verbose:
                    text = link.get_text()  
                    if href.startswith("http"): formatted_links.append({"text": text, "url": href})
                    else: formatted_links.append({"text": text, "url": base_url + href})
                else:
                    if href.startswith("http"): formatted_links.append(href)
                    else: formatted_links.append(base_url + href)
        return formatted_links
    
def save_to_file(content: str, metadata: str, path: str) -> None:
    """
    Saves the content and metadata to a file.

    Args:
        content (str): content of the article
        metadata (str): metadata of the article
        path (str): path to save the file
    """
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)
    with open(f"{path}.metadata", 'w', encoding='utf-8') as file:
        file.write(metadata)

def scrape_quebec(url: str) -> None:
    """
    Scrapes article content from quebec.ca

    Args:
        url (str): url of the quebec.ca article
    """
    
    def func(response):
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text from all <div> elements with class "ce-bodytext"
        divs = soup.find_all('div', class_='ce-bodytext')
        
        #Extract the metas from the page
        metas = soup.find_all('meta')
        
        # Extract text from each <div> and join with ". "
        content = ". ".join([div.get_text(separator='. ') for div in divs])
        cleaned_content = content.replace("\n", " ").replace("\r", " ").replace("\t", " ")
        
        metadata = {}
        for meta in metas:
            if meta.get("property") and meta.get("content"):
                metadata[meta.get("property")] = meta.get("content")
            if meta.get("name") and meta.get("content"):
                metadata[meta.get("name")] = meta.get("content")
                
        save_to_file(cleaned_content, json.dumps(metadata), f"./datasets/scraped_content{i}.txt")
    
    return error_wrapper(func, url)

links = extract_links("https://www.quebec.ca/plan-du-site", "https://www.quebec.ca/")


i = 1
for link in links:
    scraped_content = scrape_quebec(link)
    i += 1
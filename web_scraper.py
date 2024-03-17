import link_getter
from utils.error import error_wrapper
from utils.document import save_documents, Document
from bs4 import BeautifulSoup
import pandas as pd
import argparse
from scripts.dataset_downloader import get_packages

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


def scrape(url: str, func: callable) -> Document:
    """
    General scrape function that accepts a user defined function to extract content from a webpage.

    Args:
        url (str): url of the webpage
        func (callable): a function defined by caller to extract content from the webpage. Takes a BeautifulSoup object and returns a string.

    Returns:
        Document: A Document object representing the text file and its associated metadata.
    """
    
    def response_wrapper(response, func: callable) -> Document:
        soup = BeautifulSoup(response.text, 'html.parser') 
        page_content = func(soup)     
        metadata = get_metadata(soup)
        doc = Document(page_content=page_content, metadata=metadata)
        return doc
        
    return error_wrapper(url, response_wrapper, retry_time=120, func=func)

def scrape_montreal(url: str) -> Document:
    """
    Function specifically for scraping montreal.ca articles.
    
    Args:
        url (str): url of the montreal.ca article
        
    Returns:
        Document: A Document object representing the text file and its associated metadata.
    """
    # Specific function to extract content from montreal.ca
    def func(soup: BeautifulSoup) -> str:
        divs = soup.find_all('div', class_='content-module-stacked')
        content = "\n".join([div.get_text() for div in divs])
        return content
    
    return scrape(url, func)

def scrape_quebec(url: str) -> Document:
    """
    Function specifically for scraping quebec.ca articles.

    Args:
        url (str): url of the quebec.ca article
        
    Returns:
        Document: A Document object representing the text file and its associated metadata.
    """
    
    # Specific function to extract content from quebec.ca
    def func(soup: BeautifulSoup) -> str:
        divs = soup.find_all('div', class_='ce-bodytext')
        content = "\n".join([div.get_text() for div in divs])
        return content
    
    return scrape(url, func)

def scrape_articles(links: list[str], scrape_func: callable, sublink_func: callable, save_urls: bool = False, path: str = "chunks") -> None:
    """
    Scrapes a list of articles given by the links using the scrape_function and saves them to a directory. Recursively opens sublinks using the sublink_func.
    
    Args:
        links (list[str]): list of links to scrape
        scrape_func (callable): function to scrape the articles. Takes a url and returns a Document object.
        sublink_func (callable): function to get the sublinks of a page. Takes a url and returns a list of urls. Built with link_getter.get_sub_links
        save_urls (bool): If true, will save all the urls visited into a txt file. Defaults to False.
        path (str): The directory where the Document objects will be saved. Defaults to "chunks".
        
    Returns:
        None: It only saves the articles to a directory
    """
    
    if (links == None):
        print("No links to scrape.")
        return None
    
    i: int = 0
    docs: list[Document] = []
    for link in links:
        if save_urls:
            with open("all_urls", "a", encoding="utf-8") as f:
                f.write(f"{link}\n")
        
        sub_links = sublink_func(link)
        
        # Scrape if current link is an article
        if len(sub_links) == 0:
            print(f"Scraping {link}")
            doc = scrape_func(link)
            docs.append(doc)
            i += 1
        # Add sub links
        else:
            print(f"Opening {link}")
            links.extend(sub_links)
                        
        print(f"Currently {len(links)} links in total.\n")
        
    print(f"{len(links)} links in total.")

    print(f"Saving {i} documents to {path}.")
    save_documents(path, docs)
    
def scrape_quebec_articles(path: str = "chunks", save_urls: bool = False):
    """
    Goes through every link in quebec.ca and keeps opening links until it finds an article to scrape.
    
    Args
        save_urls (bool): If true, will save all the urls visited into a txt file
    """
    
    links = link_getter.get_quebec_base_links()
    scrape_articles(links, scrape_quebec, link_getter.get_quebec_sub_links, save_urls, path)
    
def scrape_montreal_articles(path: str = "chunks", save_urls: bool = False):
    """
    Goes through every link in montreal.ca and keeps opening links until it finds an article to scrape.
    
    Args
        save_urls (bool): If true, will save all the urls visited into a txt file
    """
    
    #download the montreal packages and get the urls from the csv
    get_packages(package_list=["vmtl-communique-presse"])    
    path_to_csv = "datasets/Communiqués de presse/Communiqués de presse (2023 à aujourd'hui).csv"
    links = pd.read_csv(path_to_csv)["url"].tolist()
    
    scrape_articles(links, scrape_montreal, link_getter.get_montreal_sub_links, save_urls, path)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter documents metadata.")
    parser.add_argument("--site", type=str, required=True,
                        help="The website to scrape. Either 'montreal' or 'quebec'.")
    parser.add_argument("--path", type=str, required=False,
                        help="The output directory to save the filtered documents.")
    parser.add_argument("--save_urls", type=bool, required=False,
                        help="If True, saves the urls visited to a file.")
    
    args = parser.parse_args()
    
    if args.site == "montreal":
        scrape_montreal_articles(args.path, args.save_urls)
    elif args.site == "quebec":
        scrape_quebec_articles(args.path, args.save_urls)
    else:
        print("Invalid site. Please choose either 'montreal' or 'quebec'.")
from bs4 import BeautifulSoup
import requests
from data_utils import save_json, save_csv


def get_quebec_sub_links(url: str) -> list[str]:
    """
    Gets all the links of a subpage of quebec.ca
    
    Args:
        url (str): link to the subpage containing links.
        
    Returns:
        list[str]: list of links
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

def get_base_links(url: str = "https://www.quebec.ca/plan-du-site", 
                       base_url: str = "https://www.quebec.ca/", 
                       verbose: bool = False,
                       save_format: str = None
                       ) -> list:
    """
    Extract all the useful links from the base level of a website. These links are all inside div class 'col-12 col-md-4' inside 'li' tags.

    Args:
        url (str, optional): The url to scrape. Defaults to "https://www.quebec.ca/plan-du-site".
        base_url (str, optional): The base url of the website. Defaults to "https://www.quebec.ca/".
        verbose (bool, optional): If True, returns a list of dictionaries with the url and the links. Defaults to False.
        save_format (str, optional): If not None, saves the links to a file. Defaults to None.

    Returns:
        list: list of links
    """
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve {url}, Status code: {response.status_code}")
        return None
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    formatted_links = []
    
    links_html = soup.find_all("div", class_ = "col-12 col-md-4")
    for link_html in links_html:
        
        #find all 'a' tags within each 'li' tag
        lis = link_html.find_all('li')
        
        links = []
        for li in lis:
            links.extend(li.find_all('a'))
        
        
        for link in links:
            href = link.get('href')
            if href:
                if verbose:
                    text = link.get_text()  
                    # if href.startswith("http"): formatted_links.append({"text": text, "url": href})
                    
                    #only add the link if it's not already in the list and if it's not from a different domain
                    if href.startswith("/") and not {"text": text, "url": base_url + href} in formatted_links:
                        formatted_links.append({"text": text, "url": base_url + href})
                else:
                    # if href.startswith("http"): formatted_links.append(href)
                    if href.startswith("/") and not base_url + href in formatted_links:
                        formatted_links.append(base_url + href)
                
    if save_format == "json":
        save_json(formatted_links, "base-links")
    elif save_format == "csv":
        save_csv(formatted_links, "base-links")
    elif save_format != None:
        print(f"Save format {save_format} is not supported")            
    
    return formatted_links
        
if __name__ == "__main__":
    get_base_links(save_format="json")
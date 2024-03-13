from bs4 import BeautifulSoup
import requests
import json
from data_utils import save_json, save_csv

'''
This script scrapes the Quebec government website and extracts all the links from the site map while
keeping a hierarchical structure of the links with categories and subcategories. The data has the following structure:
{
    "category1": {
        "subcategory1": [
            {"text": "Link text", "url": "Link URL"},
            ...
        ],
        ...
    },
    ...
}
'''

# Specify the encoding when writing the JSON file
def get_urls(save_links:bool = False) -> dict:
    """
    Scrapes the base level of thequebec plan-du-site page and extracts all the links from the site map.

    Args:
        save_links (bool, optional): If true, saves the links to a json file. Defaults to False.

    Returns:
        dict: The data extracted from the site map.
    """
    # The URL of the website to scrape
    url = "https://www.quebec.ca/plan-du-site"
    base_url = "https://www.quebec.ca"
    content = requests.get(url).text.encode("utf-8")
    document = BeautifulSoup(content, "html.parser")

    # Create a dictionary to store the data
    data: dict[dict[list[str, str]]] = {}

    # Find all the divs in the body
    divs: list = document.find("body").find_all("div")
    for div in divs:
        # If the div doesn't have an h3 tag, skip it
        if not div.find("h3"): continue

        # Get the category and create a dictionary for it
        category = div.find("h3").text
        data[category] = {}

        # get all the sibling divs of the current div (because the site is structured that way)
        subdivs = div.parent.find_all("div")

        for sub in subdivs:
            # If the sub div doesn't have an h4 tag, skip it
            if not sub.find("h4"): continue

            # Get the subcategory
            subcategory = sub.find("h4").get_text()
            data[category][subcategory] = []

            links = sub.find_all("a")

            # For each link, get the href and text and add it to the data as a dictionary
            for link in links:
                href = link.get("href")
                text = link.get_text()
                if href:
                    if not href.startswith("http"):
                        data[category][subcategory].append({"text": text, "url": base_url + href})
        
    # Save the data to a json file
    if save_links:
        with open("data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    
    return data

def extract_base_links(url: str = "https://www.quebec.ca/plan-du-site", 
                       base_url: str = "https://www.quebec.ca/", 
                       verbose: bool = False,
                       save_format: str = None
                       ) -> list:
    """
    Extract all the links from the base level of a website. These links are all inside 'li' tags.

    Args:
        url (str, optional): The url to scrape. Defaults to "https://www.quebec.ca/plan-du-site".
        base_url (str, optional): The base url of the website. Defaults to "https://www.quebec.ca/".
        verbose (bool, optional): If True, returns a list of dictionaries with the url and the links. Defaults to False.
        save_format (str, optional): If not None, saves the links to a file. Defaults to None.

    Returns:
        list: list of links
    """
    
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    
    #find all 'a' tags within each 'li' tag
    lis = soup.find_all('li')
    
    links = []
    for li in lis:
        links.extend(li.find_all('a'))
    
    
    formatted_links = []
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
    extract_base_links(save_format="json")
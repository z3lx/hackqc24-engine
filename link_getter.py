from bs4 import BeautifulSoup
from data_utils import save_json, save_csv
import validators
from error import error_wrapper

def get_sub_links(url: str, base_url: str, func: callable, verbose: bool = False, save_format: str = None) -> list[str]:
    """
    General function to get all the links of a subpage of a website. It can also be used for the base page itself if url == base_url.
    
    Args:
        _url (str): link to the subpage containing links.
        base_url (str): base url of the website.
        func (callable): function that accepts a soup object and returns a list of anchor tags.
        
    Returns:
        list[str]: list of links
    """

    #action function to be passed to error_wrapper
    def action(response) -> list[str]:
        #Error handling
        if not validators.url(url): raise ValueError("The url is not valid")
        if not validators.url(base_url): raise ValueError("The base url is not valid")
        if not url.startswith(base_url): raise ValueError("The url must be from the same domain as the base url")


        links = []
        content = response.text
        page = BeautifulSoup(content, "html.parser")
        anchor_tags = func(page)

        for a in anchor_tags:
            #only add the link if it's not already in the list and if it's not from a different domain
            condition: bool = base_url + a.get("href") not in links and a.get("href").startswith("/")
            if verbose:
                if condition: links.append({"text": a.get_text(), "url": base_url + a.get("href")})
            else:
                if condition: links.append(base_url + a.get("href"))
                    
        if save_format == "json":
            save_json(links, "base-links")
        elif save_format == "csv":
            save_csv(links, "base-links")
        elif save_format != None:
            print(f"Save format {save_format} is not supported")    
                    
        return links
    
    return error_wrapper(url, action)
    

def get_quebec_sub_links(url: str, verbose: bool = False, save_format: str = None) -> list:
    """
    Gets all the links of a subpage of quebec.ca
    
    Args:
        url (str): link to the subpage containing links.
        
    Returns:
        list[str]: list of links
    """

    #get all the anchor tags with the class "sous-theme-page-lien"    
    def func(page: BeautifulSoup) -> list:
        return page.find_all("a", class_="sous-theme-page-lien")
    
    return get_sub_links(url, "https://www.quebec.ca/", func, verbose, save_format)

def get_montreal_sub_links(url: str, verbose: bool = False, save_format: str = None) -> list:
    """
    Gets all the links of a subpage of montreal.ca
    
    Args:
        url (str): link to the subpage containing links.
        
    Returns:
        list[str]: list of links
    """
        
    def func(page: BeautifulSoup) -> list:
        divs = page.find_all("div", class_="list-item-action")
        anchor_tags = [div.find("a") for div in divs]
        return anchor_tags
    
    return get_sub_links(url, "https://montreal.ca/", func, verbose, save_format)

def get_quebec_base_links(verbose: bool = False, save_format: str = None) -> list:
    """
    Extract all the links from the base level of quebec website

    Args:
        url (str, optional): The url to scrape. Defaults to "https://www.quebec.ca/plan-du-site".
        base_url (str, optional): The base url of the website. Defaults to "https://www.quebec.ca/".
        verbose (bool, optional): If True, returns a list of dictionaries with the url and the links. Defaults to False.
        save_format (str, optional): If not None, saves the links to a file. Defaults to None.

    Returns:
        list: list of links
    """
    
    def func(page: BeautifulSoup) -> list:
        anchor_tags = [];
        lis = page.find_all('li')
        for li in lis:
            anchor_tags.extend(li.find_all('a'))
        return anchor_tags
            
    return get_sub_links("https://www.quebec.ca/plan-du-site", "https://www.quebec.ca/", func, verbose, save_format)
        
if __name__ == "__main__":
    get_quebec_base_links(save_format="json")
from bs4 import BeautifulSoup
import requests
import json

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

# Specify the encoding when writing the JSON file
with open("data.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4, ensure_ascii=False)
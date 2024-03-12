from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain.chains import create_extraction_chain
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pprint
import validators
from data_utils import save_to_json, save_to_csv
import csv
import json
from bs4 import BeautifulSoup
import requests

def scrape_montreal(url: str) -> str:
        
    """
    Scrapes article content from montreal.ca
    
    Args:
        url (str): url of the montreal.ca article
        
    Returns
        str: Article content of the page.
    """

    try:
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract text from all <div> elements with class "content-modules"
            div_contents = soup.find_all('div', class_='content-modules')
            
            # Extract text from each <div> and join with ". "
            extracted_text = ". ".join([div.get_text(separator='. ') for div in div_contents])
            
            return extracted_text
        else:
            # Print an error message if the request was not successful
            print("Failed to retrieve the webpage. Status code:", response.status_code)
            return None
    except Exception as e:
        print("Error occurred while scraping URL:", url)
        print("Error:", e)
        return None

#constant schema for default values
schema = {
    "properties": {
        "links": {
            "description": "A list of links found in the document.",
            "type": "array",
            "items": {
                "type": "string"  
            }
        }
    },
    "required": ["links"]
}

class WebScraper:
    """
    Extractor library that uses AI to extract information from web pages.
    Main method to use is scrape_with_playwright which will scrape a list of urls using playwright.
    A schema is required to define the properties to extract.
    """
    
    def __init__(self, urls: list[str] = ["https://www.quebec.ca/"],
                 llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo"),
                 Loader=AsyncChromiumLoader,
                 Transformer=BeautifulSoupTransformer):
        self.__urls = urls
        self.Loader = Loader
        self.Transformer = Transformer
        self.llm = llm
        
    @property
    def urls(self):
        return self.__urls
    
    @urls.setter
    def urls(self, urls: list[str]):
        #Check if the urls are valid
        for url in self.__urls:
            if not validators.url(url):
                raise ValueError(f"{url} is not a valid url")
        self.__urls = urls

    def load(self) -> list[Document]:
        """
        Load a list of documents from a list of urls using a loader from langchain_community.document_loaders

        Args:
            Loader (Loader, optional): Loader to load documents with. Defaults to AsyncChromiumLoader.
            urls (list[str], optional): Urls of pages to load. Defaults to ["https://www.quebec.ca/"].
        Returns:
            list[Document]: list of documents from the urls
        """
        loader = self.Loader(self.__urls)
        docs = loader.load()
        return docs
    
    def transform(self, docs: list[Document], tags_to_extract: list[str] = ["span", "p", "h1", "h2", "a"]) -> list[Document]:
        """
        Transform a list of documents using self.transformer from langchain_community.document_transformers

        Args:
            docs (list[Document]): list of documents to transform
            tags_to_extract (list[str], optional): Tags to extract from the documents. Only works with bs4. Defaults to ["span", "p", "h1", "h2", "a"].
        Returns:
            list[Document]: list of transformed documents
        """
        transformer = self.Transformer()
        docs_transformed = transformer.transform_documents(docs, tags_to_extract=tags_to_extract)
        return docs_transformed
    
    def extract(self, content: str, schema: dict = schema):
        """
        Extract information from a document using a schema

        Args:
            content (str): content of the document
            schema (dict): schema that defines the properties to extract
        Returns:
            Any: extraction content
        """
        # Inside the function that processes the content
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        return create_extraction_chain(schema=schema, llm=self.llm).invoke(content)
    
    def scrape_with_playwright(self, schema: dict = schema, tags_to_extract: list[str] = ["span", "p", "h1", "h2", "a"]) -> dict:
        """
        Scrape a list of urls using playwright
        
        Args:
            schema (dict): schema that defines the properties to extract. Example Format:
            {
                "properties": {
                    "links": {
                        "description": "A list of links found in the document.",
                        "type": "array",
                        "items": {
                            "type": "string"  
                        }
                    }
                },
                "required": ["links"]
            }
        Returns:
            dict: extracted data
        """
        docs = self.load()
        docs_transformed = self.transform(docs, tags_to_extract=tags_to_extract)
        print("Extracting content with LLM")
        
        #Grab the first 1000 tokens of the document
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=1000, chunk_overlap=0)
        splits = splitter.split_documents(docs_transformed)
        
        #extract the data from the splits
        data = []
        for split in splits:
            extracted = self.extract(split.page_content, schema)
            pprint.pprint(extracted.get("text"))
            data.append(extracted)
        
        #return cleaned data
        return self.clean_data_splits(data, schema)
    
    def scrape_and_save(self, schema: dict = schema,
                        tags_to_extract: list[str] = ["span", "p", "h1", "h2", "a"],
                        filename: str = "extracted",
                        dir: str = "",
                        format: str = "json"):
        """
        Shortcut to scrape_with_playwright and save the data to a file

        Args:
            schema (dict, optional): Schema . Defaults to schema.
            tags_to_extract (list[str], optional): _description_. Defaults to ["span", "p", "h1", "h2", "a"].
            filename (str, optional): Do not include format extensions. Defaults to "extracted".
            dir (str, optional): _description_. Defaults to "".
            format (str, optional): _description_. Defaults to "json".

        Raises:
            ValueError: _description_
        """
        data = self.scrape_with_playwright(schema, tags_to_extract)
        if format == "json":
            save_to_json(data, filename, dir)
        elif format == "csv":
            save_to_csv(data, filename, dir)
        else:
            raise ValueError(f"Format {format} is not supported")
            
    def clean_data_splits(self, splits: list, schema: dict) -> dict:
        """
        Clean the data from the splits

        Args:
            splits (list): list of splits chunked by a text splitter
            schema (dict): schema that defines the properties to extract

        Returns:
            dict: cleaned data
        """
        
        data = {}
        #name of each column
        properties: list[str] = schema.get("properties").keys()
        
        for p in properties:
            data[p] = []
            
        for split in splits:
            #get the object that actually contains the data
            object = split.get("text")[0]
            for p in properties:
                if p in object: data[p].extend(object[p])
                
        return data
    
    
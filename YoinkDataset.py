"""
    Hallo!

    This program will download all the datasets to $workingDirectory/dataset/$datasetName

    I have yet to implement the metadata stuff.

    Another issue is that sometimes you'll have to wait for the program to time out due to inaccessible ressources.
        I have no clue why they'd list them in the database if we can't grab them, but I might be doing smt wrong so who knows.
        It appears to happen with most HTML documents with geo data. Maybe it's trying to crawl the website all the way up to Google Earth?:

    This program was mostly written by AI since I couldn't be fucked to read the CKAN documentation myself.
        ( In retrospective, it might have been faster that way... )
"""






import os
import requests
import logging
from tqdm import tqdm  # For the progress bar

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def get_all_datasets(base_url):
    """
    Retrieves a list of all datasets from the Données Québec portal.

    Args:
        base_url (str): Base URL for the CKAN API.

    Returns:
        list: List of dataset names.
    """
    package_list_endpoint = "package_list"
    response = requests.get(f"{base_url}{package_list_endpoint}")

    if response.status_code == 200:
        data = response.json()
        return data.get("result", [])
    else:
        print(f"Error fetching dataset list. Status code: {response.status_code}")
        return []

def download_datasets(base_url, package_list):
    for package_name in package_list:
        package_dir = os.path.join("datasets", package_name)
        os.makedirs(package_dir, exist_ok=True)

        package_show_endpoint = f"package_show?id={package_name}"
        response = requests.get(f"{base_url}{package_show_endpoint}")

        if response.status_code == 200:
            data = response.json()
            resources = data.get("result", {}).get("resources", [])

            for resource in resources:
                resource_name = resource.get("name")
                resource_url = resource.get("url")

                if resource_name and resource_url:
                    try:
                        response = requests.get(resource_url, stream=True)  # Stream the content
                        total_size = int(response.headers.get("content-length", 0))

                        # Initialize the progress bar
                        with tqdm(total=total_size, unit="B", unit_scale=True, desc=resource_name) as pbar:
                            with open(os.path.join(package_dir, resource_name), "wb") as f:
                                for chunk in response.iter_content(chunk_size=1024):
                                    if chunk:
                                        f.write(chunk)
                                        pbar.update(len(chunk))

                        logger.info(f"Downloaded: {resource_name}")
                    except Exception as e:
                        logger.error(f"Error downloading {resource_name}: {e}")
        else:
            logger.error(f"Error fetching details for package {package_name}")

if __name__ == "__main__":
    base_url = "https://www.donneesquebec.ca/recherche/api/3/action/"
    all_datasets = get_all_datasets(base_url)
    download_datasets(base_url, all_datasets)

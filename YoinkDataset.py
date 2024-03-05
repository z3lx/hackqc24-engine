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
import re
import requests
import logging
from tqdm import tqdm

# Set up logging
logging.basicConfig(level=logging.INFO, format="[%(levelname).4s] %(message)s")
logger = logging.getLogger(__name__)


def get_all_datasets(base_url):
    """
    Retrieves a list of all datasets from the Données Québec portal.

    Args:
        base_url (str): Base URL for the CKAN API.

    Returns:
        list: List of dataset names.
    """
    package_list_endpoint = f"{base_url}package_list"
    response = requests.get(package_list_endpoint)

    if response.status_code == 200:
        data = response.json()
        return data.get("result", [])
    else:
        print(f"Error fetching dataset list. Status code: {response.status_code}")
        return []


def download_datasets(base_url, package_list):
    for package_index, package_name in enumerate(package_list):
        package_log_info = f"package {package_index + 1}/{len(package_list)} ({package_name})"

        endpoint = f"{base_url}package_show?id={package_name}"
        response = requests.get(endpoint)

        if response.status_code != 200:
            logger.error(f"Error fetching details for {package_log_info}: "
                         f"status code {response.status_code}.")
            continue

        try:
            data = response.json()
        except Exception as e:
            logger.error(f"Error parsing JSON for {package_log_info}: {e}.")
            continue

        package_success = data.get("success", False)
        package_result = data.get("result")
        if not (package_success and package_result):
            logger.error(f"Error fetching details for {package_log_info}: "
                         f"unsuccessful.")
            continue

        package_title = package_result.get("title")
        if not package_title:
            package_title = package_name
        package_dir = os.path.join("datasets", re.sub(r'[\\/:*?"<>|]', "", package_title))
        os.makedirs(package_dir, exist_ok=True)

        resource_list = package_result.get("resources", [])
        for resource_index, resource in enumerate(resource_list):
            resource_log_info = f"resource {resource_index + 1}/{len(resource_list)} for {package_log_info}"

            resource_format = resource.get("format")
            resource_name = resource.get("name")
            resource_url = resource.get("url")

            if not (resource_format and resource_name and resource_url):
                logger.warning(f"Skipping {resource_log_info}: missing metadata.")
                continue

            resource_format = resource_format.lower()
            if resource_format not in ["csv", "xlsx", "xls", "json", "sqlite", "pdf"]:
                logger.warning(f"Skipping {resource_log_info}: incompatible format.")
                continue

            resource_dir = os.path.join(package_dir, re.sub(r'[\\/:*?"<>|]', "", resource_name) + "." + resource_format)
            try:
                resource_response = requests.get(resource_url, stream=True)
                resource_size = int(resource_response.headers.get("content-length", 0))
                description = (f"Downloading resource {resource_index + 1}/{len(resource_list)} "
                               f"of package {package_index + 1}/{len(package_list)}")

                with tqdm(total=resource_size, unit="B", unit_scale=True, desc=description) as progress_bar:
                    with open(resource_dir, "wb") as file:
                        for chunk in resource_response.iter_content(chunk_size=1024):
                            if not chunk:
                                continue
                            file.write(chunk)
                            progress_bar.update(len(chunk))
            except Exception as e:
                logger.error(f"Error downloading {resource_log_info}: {e}.")
                os.remove(resource_dir)
                continue


if __name__ == "__main__":
    base_url = "https://www.donneesquebec.ca/recherche/api/3/action/"
    all_datasets = get_all_datasets(base_url)
    download_datasets(base_url, all_datasets)

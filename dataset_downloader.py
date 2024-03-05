"""
dataset_downloader.py
Downloads all datasets from the Données Québec portal using the CKAN API.
"""

import os
import re
import time

import requests
import logging
from tqdm import tqdm


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes the filename by removing any characters that are not allowed in filenames.

    Args:
        filename (str): The original filename.

    Returns:
        str: The sanitized filename.
    """
    return re.sub(r'[\\/:*?"<>|]', "", filename)


def get_package_list() -> list[str]:
    """
    Fetches the package list from the Données Québec using the CKAN API.

    Returns:
        list[str]: The list of package names. If an error occurs, an empty list is returned.
    """

    logger = logging.getLogger(__name__)
    base_url = "https://www.donneesquebec.ca/recherche/api/3/action/"
    package_list_endpoint = f"{base_url}package_list"
    response = requests.get(package_list_endpoint)

    if response.status_code != 200:
        logger.error(f"Error fetching package list: "
                     f"status code {response.status_code}.")
        return []
    try:
        data = response.json()
        return data.get("result", [])
    except Exception as e:
        logger.error(f"Error parsing JSON for package list: {e}.")
        return []


def get_packages(output_dir: str = "", package_list: list[str] = None, max_retries: int = 12, delay: int = 5) -> None:
    """
    Downloads all packages from the Données Québec portal using the CKAN API.

    Args:
        output_dir (str, optional): The directory where the downloaded packages will be stored. Defaults to the current directory.
        package_list (list[str], optional): The list of package names to download. If None, all packages will be downloaded. Defaults to None.
        max_retries (int, optional): The maximum number of retries for each download attempt. Defaults to 12.
        delay (int, optional): The delay (in seconds) between each retry. Defaults to 5.
    """

    if package_list is None:
        package_list = get_package_list()

    logger = logging.getLogger(__name__)
    base_url = "https://www.donneesquebec.ca/recherche/api/3/action/"

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
        package_dir = os.path.join(output_dir, "datasets", sanitize_filename(package_title))
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

            resource_dir = os.path.join(package_dir, f"{sanitize_filename(resource_name)}.{resource_format}")
            for retry_index in range(max_retries):
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
                    break
                except Exception as e:
                    logger.error(f"Error downloading {resource_log_info}: {e}.")
                    logger.info(f"Retrying in {delay} second(s)... "
                                f"{max_retries - retry_index - 1} retrie(s) remaining.")
                    if os.path.exists(resource_dir):
                        os.remove(resource_dir)
                    if retry_index < max_retries - 1:
                        time.sleep(delay)
                    continue


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(levelname).4s] %(message)s")
    get_packages()

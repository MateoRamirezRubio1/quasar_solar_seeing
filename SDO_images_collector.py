import os
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
BASE_IMAGE_DIR = "images/imagesSDO"


def fetch_html_content(url: str) -> Optional[str]:
    """Fetch HTML content from a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching HTML content from {url}: {e}")
        return None


def extract_image_names(
    html_content: str, type_images: List[str], date_time: str
) -> List[str]:
    """Extracts image names from HTML content, filtered by type and date."""
    soup = BeautifulSoup(html_content, "html.parser")
    pre_text = soup.find("pre").get_text().split("\n")

    image_names = [
        line.split()[0]
        for line in pre_text
        if date_time in line and line.split(".")[0].split("_")[-1] in type_images
    ]
    return image_names


def create_folder_if_not_exists(folder_path: str) -> None:
    """Creates a folder if it does not exist."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        logging.info(f"Created folder: {folder_path}")


def download_image(url: str, file_path: str) -> None:
    """Downloads a single image from a URL and saves it to a file path."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(file_path, "wb") as file:
            file.write(response.content)
        logging.info(f"Image saved at {file_path}")
    except requests.RequestException as e:
        logging.error(f"Error fetching image from {url}: {e}")
    except IOError as e:
        logging.error(f"Error saving image at {file_path}: {e}")


def download_images(params: Dict[str, str]) -> None:
    """Downloads images from URLs and saves them in a specific directory."""
    url_base = params.get("url_base")
    image_names = params.get("image_names", [])
    folder_path = os.path.join(
        params.get("base_folder"),
        params.get("folder_name"),
        params.get("subfolder_name"),
    )

    if not all([url_base, image_names, folder_path]):
        logging.error("Error: Missing required parameters.")
        return

    create_folder_if_not_exists(folder_path)

    for name in image_names:
        image_url = f"{url_base}/{name}"
        file_path = os.path.join(folder_path, name)
        download_image(image_url, file_path)


def main():
    # Initial user information
    print("\nWelcome to the SDO Image Downloader.\n")
    print(
        "This script allows you to efficiently download various types of solar images from the SDO database."
    )
    print(
        "There is no need to manually create folders for storing images; the script handles that automatically.\n"
    )

    # Get input from the user
    image_types = input(
        "Enter the image types separated by a space (e.g., HMIIC HMIIF): "
    ).split()
    date_time = input(
        "Enter the date and time in the format YYYY-MM-DD HH:MM (e.g., 2024-08-02 01:10): "
    )

    date_time_parser = date_time.split()[0].replace("-", "/")
    url_base = f"https://sdo.gsfc.nasa.gov/assets/img/browse/{date_time_parser}"

    html_content = fetch_html_content(url_base)
    if not html_content:
        return

    image_names = extract_image_names(html_content, image_types, date_time)

    if not image_names:
        logging.info("No images found")
        return

    params_download_images = {
        "url_base": url_base,
        "image_names": image_names,
        "base_folder": BASE_IMAGE_DIR,
        "folder_name": date_time.split()[0],
        "subfolder_name": date_time.split()[1].replace(":", "-"),
    }
    download_images(params_download_images)
    logging.info("Execution completed")


if __name__ == "__main__":
    main()

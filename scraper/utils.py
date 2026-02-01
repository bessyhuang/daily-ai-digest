"""
Utility functions for web scraping
"""
import os
import time
import requests
from typing import Optional
from urllib.parse import urljoin


def download_image(image_url: str, save_path: str, timeout: int = 10) -> bool:
    """
    Download an image from URL and save to local path

    Args:
        image_url: URL of the image to download
        save_path: Local path to save the image
        timeout: Request timeout in seconds

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Download image
        response = requests.get(image_url, timeout=timeout, stream=True)
        response.raise_for_status()

        # Save image
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return True
    except Exception as e:
        print(f"Error downloading image {image_url}: {e}")
        return False


def make_request(url: str, delay: float = 1.5, timeout: int = 10) -> Optional[requests.Response]:
    """
    Make HTTP GET request with delay and error handling

    Args:
        url: URL to request
        delay: Delay in seconds before making the request
        timeout: Request timeout in seconds

    Returns:
        requests.Response or None if request failed
    """
    time.sleep(delay)

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response
    except Exception as e:
        print(f"Error requesting {url}: {e}")
        return None


def normalize_url(url: str, base_url: str) -> str:
    """
    Normalize a URL by joining it with base URL if relative

    Args:
        url: URL to normalize
        base_url: Base URL to use for relative URLs

    Returns:
        Normalized absolute URL
    """
    if url.startswith('http'):
        return url
    return urljoin(base_url, url)


def extract_product_id(detail_url: str) -> Optional[str]:
    """
    Extract product ID from detail URL

    Args:
        detail_url: Product detail URL

    Returns:
        Product ID string or None
    """
    try:
        # URL format: https://www.u-chance.com.tw/products_detail/{id}
        return detail_url.rstrip('/').split('/')[-1]
    except:
        return None

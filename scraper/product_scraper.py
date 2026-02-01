"""
Product scraper for U-Chance furniture website
"""
import json
import os
import sys
from typing import List, Dict, Optional

from bs4 import BeautifulSoup
from tqdm import tqdm

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    BASE_URL, PRODUCTS_LIST_URL,
    TOTAL_PAGES, REQUEST_DELAY, DATA_DIR, IMAGES_DIR, PRODUCTS_JSON
)
from scraper.utils import (
    download_image, make_request, normalize_url, extract_product_id
)


class UChanceScraper:
    """Scraper for U-Chance furniture products"""

    def __init__(self):
        self.products = []
        self.base_url = BASE_URL
        self.delay = REQUEST_DELAY

        # Create data directories
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(IMAGES_DIR, exist_ok=True)

    def scrape_product_list_page(self, page: int) -> List[str]:
        """
        Scrape a single product list page to get product URLs

        Args:
            page: Page number to scrape

        Returns:
            List of product detail URLs
        """
        url = f"{PRODUCTS_LIST_URL}{page}"
        print(f"Scraping page {page}: {url}")

        response = make_request(url, delay=self.delay)
        if not response:
            return []

        soup = BeautifulSoup(response.content, 'lxml')
        product_urls = []

        # Find product links - adjust selectors based on actual HTML structure
        # This is a generic selector, may need adjustment
        product_links = soup.select('a[href*="products_detail"]')

        for link in product_links:
            href = link.get('href')
            if href:
                detail_url = normalize_url(href, self.base_url)
                if detail_url not in product_urls:
                    product_urls.append(detail_url)

        print(f"Found {len(product_urls)} products on page {page}")
        return product_urls

    def scrape_product_detail(self, detail_url: str) -> Optional[Dict]:
        """
        Scrape product detail page

        Args:
            detail_url: URL of the product detail page

        Returns:
            Dict with product information or None if failed
        """
        response = make_request(detail_url, delay=self.delay)
        if not response:
            return None

        soup = BeautifulSoup(response.content, 'lxml')

        # Extract product ID from URL
        product_id = extract_product_id(detail_url)
        if not product_id:
            print(f"Could not extract product ID from {detail_url}")
            return None

        # Extract product information based on actual HTML structure
        try:
            # Product name - from h1 tag
            name_elem = soup.select_one('h1')
            name = name_elem.get_text(strip=True) if name_elem else f"Product {product_id}"

            # Category - from h2 tag (appears to be the category)
            category_elem = soup.select_one('h2')
            category = category_elem.get_text(strip=True) if category_elem else "Unknown"

            # Description - from .products-detail div
            desc_elem = soup.select_one('.products-detail')
            description = desc_elem.get_text(strip=True) if desc_elem else ""

            # Image URL - find the main product image (first image with 'products' in src)
            image_elem = None
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if 'products' in src and not src.endswith('site_info'):
                    image_elem = img
                    break

            image_url = None
            if image_elem and image_elem.get('src'):
                image_url = normalize_url(image_elem['src'], self.base_url)

            product_data = {
                'product_id': product_id,
                'name': name,
                'category': category,
                'description': description,
                'image_url': image_url,
                'detail_url': detail_url
            }

            return product_data

        except Exception as e:
            print(f"Error parsing product {detail_url}: {e}")
            return None

    def download_product_image(self, product: Dict) -> bool:
        """
        Download product image to local storage

        Args:
            product: Product dictionary with image_url

        Returns:
            bool: True if successful, False otherwise
        """
        if not product.get('image_url'):
            return False

        product_id = product['product_id']
        image_url = product['image_url']

        # Determine file extension
        ext = os.path.splitext(image_url.split('?')[0])[1] or '.jpg'
        local_path = os.path.join(IMAGES_DIR, f"{product_id}{ext}")

        success = download_image(image_url, local_path)

        if success:
            # Update product with local path
            product['local_image_path'] = local_path

        return success

    def scrape_all_products(self, start_page: int = 1, end_page: Optional[int] = None):
        """
        Scrape all products from the website

        Args:
            start_page: Starting page number
            end_page: Ending page number (None for TOTAL_PAGES)
        """
        if end_page is None:
            end_page = TOTAL_PAGES

        print(f"Starting to scrape pages {start_page} to {end_page}")

        # Step 1: Collect all product URLs
        all_product_urls = []
        for page in tqdm(range(start_page, end_page + 1), desc="Collecting product URLs"):
            urls = self.scrape_product_list_page(page)
            all_product_urls.extend(urls)

        # Remove duplicates
        all_product_urls = list(set(all_product_urls))
        print(f"\nTotal unique products found: {len(all_product_urls)}")

        # Step 2: Scrape each product detail
        for url in tqdm(all_product_urls, desc="Scraping product details"):
            product = self.scrape_product_detail(url)
            if product:
                self.products.append(product)

        print(f"\nSuccessfully scraped {len(self.products)} products")

        # Step 3: Download images
        print("\nDownloading product images...")
        success_count = 0
        for product in tqdm(self.products, desc="Downloading images"):
            if self.download_product_image(product):
                success_count += 1

        print(f"Successfully downloaded {success_count}/{len(self.products)} images")

    def save_products(self, filepath: Optional[str] = None):
        """
        Save scraped products to JSON file

        Args:
            filepath: Path to save JSON file (defaults to PRODUCTS_JSON)
        """
        if filepath is None:
            filepath = PRODUCTS_JSON

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, ensure_ascii=False, indent=2)

        print(f"Saved {len(self.products)} products to {filepath}")

    def load_products(self, filepath: Optional[str] = None) -> List[Dict]:
        """
        Load products from JSON file

        Args:
            filepath: Path to JSON file (defaults to PRODUCTS_JSON)

        Returns:
            List of product dictionaries
        """
        if filepath is None:
            filepath = PRODUCTS_JSON

        if not os.path.exists(filepath):
            print(f"File {filepath} does not exist")
            return []

        with open(filepath, 'r', encoding='utf-8') as f:
            self.products = json.load(f)

        print(f"Loaded {len(self.products)} products from {filepath}")
        return self.products


def main():
    """Main function to run the scraper"""
    print("=" * 50)
    print("U-Chance Product Scraper")
    print("=" * 50)

    scraper = UChanceScraper()

    # For testing, you can scrape just a few pages first:
    # scraper.scrape_all_products(start_page=1, end_page=2)

    # To scrape all pages (1-81):
    scraper.scrape_all_products(start_page=1, end_page=TOTAL_PAGES)

    # Save results
    scraper.save_products()

    print("\n" + "=" * 50)
    print("Scraping completed!")
    print(f"Products saved to: {PRODUCTS_JSON}")
    print(f"Images saved to: {IMAGES_DIR}")
    print("=" * 50)


if __name__ == "__main__":
    main()

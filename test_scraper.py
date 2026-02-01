"""
Test script to verify scraper functionality
"""
import sys
import os
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.product_scraper import UChanceScraper

def test_single_product():
    """Test scraping a single product"""
    print("=" * 60)
    print("Testing Product Scraper")
    print("=" * 60)

    scraper = UChanceScraper()

    # Test URL
    test_url = "https://www.u-chance.com.tw/products_detail/383"
    print(f"\nTesting URL: {test_url}\n")

    # Scrape product
    product = scraper.scrape_product_detail(test_url)

    if product:
        print("✓ Successfully scraped product!")
        print("\nProduct Data:")
        print(json.dumps(product, indent=2, ensure_ascii=False))

        # Test image download
        print("\n" + "=" * 60)
        print("Testing Image Download")
        print("=" * 60)

        if scraper.download_product_image(product):
            print(f"✓ Image downloaded successfully!")
            print(f"  Saved to: {product.get('local_image_path')}")
        else:
            print("✗ Failed to download image")

    else:
        print("✗ Failed to scrape product")

    print("\n" + "=" * 60)

def test_product_list():
    """Test scraping product list page"""
    print("=" * 60)
    print("Testing Product List Scraping")
    print("=" * 60)

    scraper = UChanceScraper()

    # Test first page
    print("\nScraping page 1...\n")
    product_urls = scraper.scrape_product_list_page(1)

    print(f"\n✓ Found {len(product_urls)} products")
    print("\nFirst 5 products:")
    for i, url in enumerate(product_urls[:5], 1):
        print(f"{i}. {url}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    # Test single product detail
    test_single_product()

    print("\n\n")

    # Test product list
    test_product_list()

    print("\nTests completed!")

"""
Batch embedding generation for all products
"""
import json
import os
import sys
import time
from typing import List, Dict

import numpy as np
from tqdm import tqdm

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PRODUCTS_JSON, EMBEDDINGS_FILE, DATA_DIR
from embeddings.bedrock_client import BedrockEmbeddingClient


class ProductEmbeddingGenerator:
    """Generate embeddings for all products"""

    def __init__(self):
        self.client = BedrockEmbeddingClient()
        self.products = []
        self.embeddings = []
        self.failed_products = []

    def load_products(self, filepath: str = PRODUCTS_JSON) -> List[Dict]:
        """
        Load products from JSON file

        Args:
            filepath: Path to products JSON file

        Returns:
            List of product dictionaries
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Products file not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            self.products = json.load(f)

        print(f"Loaded {len(self.products)} products")
        return self.products

    def generate_product_embedding(self, product: Dict) -> tuple:
        """
        Generate embedding for a single product

        Args:
            product: Product dictionary

        Returns:
            Tuple of (embedding, success)
        """
        try:
            # Get local image path
            local_image_path = product.get('local_image_path')
            if not local_image_path or not os.path.exists(local_image_path):
                print(f"Image not found for product {product['product_id']}")
                return None, False

            # Generate text description for multimodal embedding
            text_description = f"{product['name']} - {product['category']}"
            if product.get('description'):
                text_description += f" - {product['description'][:200]}"

            # Generate multimodal embedding (image + text)
            embedding = self.client.get_multimodal_embedding(
                text=text_description,
                image_path=local_image_path
            )

            if embedding:
                return embedding, True
            else:
                return None, False

        except Exception as e:
            print(f"Error generating embedding for product {product['product_id']}: {e}")
            return None, False

    def generate_all_embeddings(self, delay: float = 0.1):
        """
        Generate embeddings for all products

        Args:
            delay: Delay between API calls in seconds
        """
        print(f"\nGenerating embeddings for {len(self.products)} products...")
        print(f"Model: {self.client.model_id}")
        print(f"Embedding dimension: {self.client.get_embedding_dimension()}")

        self.embeddings = []
        self.failed_products = []

        for product in tqdm(self.products, desc="Generating embeddings"):
            embedding, success = self.generate_product_embedding(product)

            if success:
                self.embeddings.append(embedding)
            else:
                # Use zero vector for failed products
                self.embeddings.append([0.0] * self.client.get_embedding_dimension())
                self.failed_products.append(product['product_id'])

            # Add delay to avoid rate limiting
            time.sleep(delay)

        print(f"\nSuccessfully generated {len(self.products) - len(self.failed_products)}/{len(self.products)} embeddings")
        if self.failed_products:
            print(f"Failed products: {', '.join(self.failed_products)}")

    def save_embeddings(self, filepath: str = EMBEDDINGS_FILE):
        """
        Save embeddings to numpy file

        Args:
            filepath: Path to save embeddings
        """
        if not self.embeddings:
            raise ValueError("No embeddings to save")

        # Create directory if needed
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Convert to numpy array and save
        embeddings_array = np.array(self.embeddings, dtype=np.float32)
        np.save(filepath, embeddings_array)

        print(f"\nSaved embeddings to {filepath}")
        print(f"Shape: {embeddings_array.shape}")
        print(f"Size: {embeddings_array.nbytes / 1024:.2f} KB")

    def save_metadata(self):
        """Save metadata about embeddings"""
        metadata = {
            'total_products': len(self.products),
            'successful_embeddings': len(self.products) - len(self.failed_products),
            'failed_products': self.failed_products,
            'embedding_dimension': self.client.get_embedding_dimension(),
            'model_id': self.client.model_id
        }

        metadata_path = os.path.join(DATA_DIR, 'embeddings_metadata.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"Saved metadata to {metadata_path}")


def main():
    """Main function to generate embeddings"""
    print("=" * 60)
    print("Product Embedding Generation")
    print("=" * 60)

    generator = ProductEmbeddingGenerator()

    # Load products
    try:
        generator.load_products()
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("Please run the scraper first: uv run python -m scraper.product_scraper")
        sys.exit(1)

    # Generate embeddings
    generator.generate_all_embeddings(delay=0.1)

    # Save embeddings and metadata
    generator.save_embeddings()
    generator.save_metadata()

    print("\n" + "=" * 60)
    print("Embedding generation completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

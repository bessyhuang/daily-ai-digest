"""
Vector store for product embeddings with similarity search
"""
import json
import os
import sys
from typing import List, Dict, Optional

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PRODUCTS_JSON, EMBEDDINGS_FILE


class VectorStore:
    """Simple vector store using numpy and cosine similarity"""

    def __init__(self):
        self.embeddings = None
        self.products = []
        self.dimension = 1024

    def load(
        self,
        embeddings_path: str = EMBEDDINGS_FILE,
        products_path: str = PRODUCTS_JSON
    ):
        """
        Load embeddings and product data

        Args:
            embeddings_path: Path to embeddings numpy file
            products_path: Path to products JSON file
        """
        # Load embeddings
        if not os.path.exists(embeddings_path):
            raise FileNotFoundError(f"Embeddings file not found: {embeddings_path}")

        self.embeddings = np.load(embeddings_path)
        print(f"Loaded embeddings: shape={self.embeddings.shape}")

        # Load products
        if not os.path.exists(products_path):
            raise FileNotFoundError(f"Products file not found: {products_path}")

        with open(products_path, 'r', encoding='utf-8') as f:
            self.products = json.load(f)

        print(f"Loaded {len(self.products)} products")

        # Verify consistency
        if len(self.embeddings) != len(self.products):
            raise ValueError(
                f"Mismatch: {len(self.embeddings)} embeddings "
                f"but {len(self.products)} products"
            )

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[Dict]:
        """
        Search for similar products using cosine similarity

        Args:
            query_embedding: Query embedding vector (1D array)
            top_k: Number of results to return
            threshold: Minimum similarity threshold (0-1)

        Returns:
            List of product dictionaries with similarity scores
        """
        if self.embeddings is None:
            raise ValueError("Vector store not loaded. Call load() first.")

        # Ensure query is 2D array
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        # Calculate cosine similarity
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        # Filter by threshold and build results
        results = []
        for idx in top_indices:
            similarity = float(similarities[idx])

            if similarity >= threshold:
                product = self.products[idx].copy()
                product['similarity'] = similarity
                results.append(product)

        return results

    def search_by_id(
        self,
        product_id: str,
        top_k: int = 5,
        exclude_self: bool = True
    ) -> List[Dict]:
        """
        Find similar products to a given product

        Args:
            product_id: ID of the product to find similar items for
            top_k: Number of results to return
            exclude_self: Whether to exclude the query product from results

        Returns:
            List of similar products with similarity scores
        """
        # Find product index
        product_idx = None
        for i, product in enumerate(self.products):
            if product['product_id'] == product_id:
                product_idx = i
                break

        if product_idx is None:
            raise ValueError(f"Product ID {product_id} not found")

        # Get embedding
        query_embedding = self.embeddings[product_idx]

        # Search (get top_k + 1 if excluding self)
        k = top_k + 1 if exclude_self else top_k
        results = self.search(query_embedding, top_k=k)

        # Exclude self if needed
        if exclude_self:
            results = [r for r in results if r['product_id'] != product_id][:top_k]

        return results

    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """
        Get product data by ID

        Args:
            product_id: Product ID to lookup

        Returns:
            Product dictionary or None if not found
        """
        for product in self.products:
            if product['product_id'] == product_id:
                return product.copy()
        return None

    def get_all_products(self) -> List[Dict]:
        """
        Get all products

        Returns:
            List of all products
        """
        return self.products.copy()

    def get_stats(self) -> Dict:
        """
        Get statistics about the vector store

        Returns:
            Dictionary with statistics
        """
        return {
            'total_products': len(self.products),
            'embedding_dimension': self.embeddings.shape[1] if self.embeddings is not None else 0,
            'total_embeddings': len(self.embeddings) if self.embeddings is not None else 0,
            'categories': list(set(p['category'] for p in self.products))
        }

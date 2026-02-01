"""
Query handler for text and image search
"""
import sys
import os
from typing import List, Dict, Optional, Union

import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from embeddings.bedrock_client import BedrockEmbeddingClient
from search.vector_store import VectorStore


class QueryHandler:
    """Handle search queries with text and/or images"""

    def __init__(self):
        self.bedrock_client = BedrockEmbeddingClient()
        self.vector_store = VectorStore()

    def load_vector_store(self):
        """Load vector store with embeddings and products"""
        self.vector_store.load()
        print("Vector store loaded successfully")

    def search_by_text(
        self,
        query_text: str,
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[Dict]:
        """
        Search products by text description

        Args:
            query_text: Text query (e.g., "白色升降桌")
            top_k: Number of results to return
            threshold: Minimum similarity threshold

        Returns:
            List of matching products with similarity scores
        """
        # Generate text embedding
        embedding = self.bedrock_client.get_text_embedding(query_text)

        if embedding is None:
            raise ValueError("Failed to generate text embedding")

        # Convert to numpy array
        embedding = np.array(embedding, dtype=np.float32)

        # Search
        results = self.vector_store.search(
            query_embedding=embedding,
            top_k=top_k,
            threshold=threshold
        )

        return results

    def search_by_image(
        self,
        image_path: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[Dict]:
        """
        Search products by image

        Args:
            image_path: Path to query image
            image_bytes: Image bytes (alternative to image_path)
            top_k: Number of results to return
            threshold: Minimum similarity threshold

        Returns:
            List of matching products with similarity scores
        """
        # Generate image embedding
        embedding = self.bedrock_client.get_image_embedding(
            image_path=image_path,
            image_bytes=image_bytes
        )

        if embedding is None:
            raise ValueError("Failed to generate image embedding")

        # Convert to numpy array
        embedding = np.array(embedding, dtype=np.float32)

        # Search
        results = self.vector_store.search(
            query_embedding=embedding,
            top_k=top_k,
            threshold=threshold
        )

        return results

    def search_multimodal(
        self,
        query_text: Optional[str] = None,
        image_path: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[Dict]:
        """
        Search products with both text and image

        Args:
            query_text: Text query
            image_path: Path to query image
            image_bytes: Image bytes (alternative to image_path)
            top_k: Number of results to return
            threshold: Minimum similarity threshold

        Returns:
            List of matching products with similarity scores
        """
        # Generate multimodal embedding
        embedding = self.bedrock_client.get_multimodal_embedding(
            text=query_text,
            image_path=image_path,
            image_bytes=image_bytes
        )

        if embedding is None:
            raise ValueError("Failed to generate multimodal embedding")

        # Convert to numpy array
        embedding = np.array(embedding, dtype=np.float32)

        # Search
        results = self.vector_store.search(
            query_embedding=embedding,
            top_k=top_k,
            threshold=threshold
        )

        return results

    def search_similar(
        self,
        product_id: str,
        top_k: int = 5,
        exclude_self: bool = True
    ) -> List[Dict]:
        """
        Find similar products to a given product

        Args:
            product_id: ID of the reference product
            top_k: Number of results to return
            exclude_self: Whether to exclude the reference product

        Returns:
            List of similar products with similarity scores
        """
        return self.vector_store.search_by_id(
            product_id=product_id,
            top_k=top_k,
            exclude_self=exclude_self
        )

    def get_product(self, product_id: str) -> Optional[Dict]:
        """
        Get product by ID

        Args:
            product_id: Product ID

        Returns:
            Product dictionary or None
        """
        return self.vector_store.get_product_by_id(product_id)

    def get_all_products(self) -> List[Dict]:
        """
        Get all products

        Returns:
            List of all products
        """
        return self.vector_store.get_all_products()

    def get_stats(self) -> Dict:
        """
        Get vector store statistics

        Returns:
            Statistics dictionary
        """
        return self.vector_store.get_stats()

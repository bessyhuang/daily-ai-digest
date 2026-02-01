"""
AWS Bedrock client for generating embeddings using Titan Multimodal Embeddings
"""
import base64
import json
import os
from typing import List, Optional, Union

import boto3
from botocore.exceptions import ClientError

from config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_DEFAULT_REGION,
    BEDROCK_MODEL_ID
)


class BedrockEmbeddingClient:
    """Client for generating embeddings using AWS Bedrock Titan model"""

    def __init__(
        self,
        model_id: str = BEDROCK_MODEL_ID,
        region_name: str = AWS_DEFAULT_REGION
    ):
        """
        Initialize Bedrock client

        Args:
            model_id: Bedrock model ID (default: amazon.titan-embed-image-v1)
            region_name: AWS region (default: us-east-1)
        """
        self.model_id = model_id
        self.region_name = region_name

        # Initialize boto3 client
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=region_name,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

    def get_image_embedding(
        self,
        image_path: Optional[str] = None,
        image_bytes: Optional[bytes] = None
    ) -> Optional[List[float]]:
        """
        Generate embedding for an image

        Args:
            image_path: Path to image file
            image_bytes: Image bytes (alternative to image_path)

        Returns:
            List of floats representing the embedding, or None if failed
        """
        try:
            # Read image data
            if image_path:
                with open(image_path, 'rb') as f:
                    image_data = f.read()
            elif image_bytes:
                image_data = image_bytes
            else:
                raise ValueError("Either image_path or image_bytes must be provided")

            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # Prepare request body
            body = {
                "inputImage": image_base64
            }

            # Call Bedrock API
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )

            # Parse response
            response_body = json.loads(response['body'].read())
            embedding = response_body.get('embedding')

            if embedding:
                return embedding
            else:
                print(f"No embedding in response for image")
                return None

        except ClientError as e:
            print(f"AWS ClientError: {e}")
            return None
        except Exception as e:
            print(f"Error generating image embedding: {e}")
            return None

    def get_text_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for text

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding, or None if failed
        """
        try:
            # Prepare request body
            body = {
                "inputText": text
            }

            # Call Bedrock API
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )

            # Parse response
            response_body = json.loads(response['body'].read())
            embedding = response_body.get('embedding')

            if embedding:
                return embedding
            else:
                print(f"No embedding in response for text: {text[:50]}...")
                return None

        except ClientError as e:
            print(f"AWS ClientError: {e}")
            return None
        except Exception as e:
            print(f"Error generating text embedding: {e}")
            return None

    def get_multimodal_embedding(
        self,
        text: Optional[str] = None,
        image_path: Optional[str] = None,
        image_bytes: Optional[bytes] = None
    ) -> Optional[List[float]]:
        """
        Generate embedding for both text and image

        Args:
            text: Text to embed
            image_path: Path to image file
            image_bytes: Image bytes (alternative to image_path)

        Returns:
            List of floats representing the embedding, or None if failed
        """
        try:
            body = {}

            # Add text if provided
            if text:
                body["inputText"] = text

            # Add image if provided
            if image_path or image_bytes:
                # Read image data
                if image_path:
                    with open(image_path, 'rb') as f:
                        image_data = f.read()
                else:
                    image_data = image_bytes

                # Encode image to base64
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                body["inputImage"] = image_base64

            if not body:
                raise ValueError("Either text or image must be provided")

            # Call Bedrock API
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )

            # Parse response
            response_body = json.loads(response['body'].read())
            embedding = response_body.get('embedding')

            if embedding:
                return embedding
            else:
                print(f"No embedding in response")
                return None

        except ClientError as e:
            print(f"AWS ClientError: {e}")
            return None
        except Exception as e:
            print(f"Error generating multimodal embedding: {e}")
            return None

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings for this model

        Returns:
            Embedding dimension (1024 for Titan)
        """
        # Titan Multimodal Embeddings produces 1024-dimensional vectors
        return 1024

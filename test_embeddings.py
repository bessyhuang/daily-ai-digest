"""
Test script for embedding generation
"""
import sys
import os
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from embeddings.bedrock_client import BedrockEmbeddingClient


def test_text_embedding():
    """Test text embedding generation"""
    print("=" * 60)
    print("Testing Text Embedding")
    print("=" * 60)

    client = BedrockEmbeddingClient()

    test_text = "白色升降桌"
    print(f"\nTest text: {test_text}")

    embedding = client.get_text_embedding(test_text)

    if embedding:
        print(f"✓ Successfully generated text embedding!")
        print(f"  Dimension: {len(embedding)}")
        print(f"  First 5 values: {embedding[:5]}")
    else:
        print("✗ Failed to generate text embedding")

    print("\n" + "=" * 60)


def test_image_embedding():
    """Test image embedding generation"""
    print("=" * 60)
    print("Testing Image Embedding")
    print("=" * 60)

    client = BedrockEmbeddingClient()

    # Use the first product image (from current scraped data)
    test_image = "data/images/1075.jpg"

    if not os.path.exists(test_image):
        print(f"✗ Test image not found: {test_image}")
        print("  Please run the scraper first or check the image path")
        return

    print(f"\nTest image: {test_image}")

    embedding = client.get_image_embedding(image_path=test_image)

    if embedding:
        print(f"✓ Successfully generated image embedding!")
        print(f"  Dimension: {len(embedding)}")
        print(f"  First 5 values: {embedding[:5]}")
    else:
        print("✗ Failed to generate image embedding")

    print("\n" + "=" * 60)


def test_multimodal_embedding():
    """Test multimodal embedding generation"""
    print("=" * 60)
    print("Testing Multimodal Embedding (Text + Image)")
    print("=" * 60)

    client = BedrockEmbeddingClient()

    # Use the first product (from current scraped data)
    test_image = "data/images/1075.jpg"
    test_text = "K-7 電源插座 配件"

    if not os.path.exists(test_image):
        print(f"✗ Test image not found: {test_image}")
        return

    print(f"\nTest text: {test_text}")
    print(f"Test image: {test_image}")

    embedding = client.get_multimodal_embedding(
        text=test_text,
        image_path=test_image
    )

    if embedding:
        print(f"\n✓ Successfully generated multimodal embedding!")
        print(f"  Dimension: {len(embedding)}")
        print(f"  First 5 values: {embedding[:5]}")
    else:
        print("\n✗ Failed to generate multimodal embedding")

    print("\n" + "=" * 60)


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("AWS Bedrock Embedding Tests")
    print("=" * 60)
    print("\nNote: Make sure you have:")
    print("1. Set up AWS credentials in .env file")
    print("2. Enabled Bedrock access in your AWS account")
    print("3. Run the scraper to download product images")
    print("\n" + "=" * 60)

    # Test text embedding
    test_text_embedding()
    print("\n")

    # Test image embedding
    test_image_embedding()
    print("\n")

    # Test multimodal embedding
    test_multimodal_embedding()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
    print("\nIf all tests passed, you can now run:")
    print("  uv run python -m embeddings.batch_embed")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

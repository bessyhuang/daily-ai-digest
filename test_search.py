"""
Test script for vector search functionality
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from search.query_handler import QueryHandler


def test_text_search():
    """Test text-based search"""
    print("=" * 60)
    print("測試：文字搜尋")
    print("=" * 60)

    handler = QueryHandler()
    handler.load_vector_store()

    # Test query
    query = "電源插座"
    print(f"\n搜尋關鍵字: {query}\n")

    results = handler.search_by_text(query, top_k=5)

    print(f"找到 {len(results)} 個結果:\n")
    for i, product in enumerate(results, 1):
        print(f"{i}. {product['name']}")
        print(f"   分類: {product['category']}")
        print(f"   相似度: {product['similarity']:.4f}")
        print(f"   ID: {product['product_id']}")
        print()

    print("=" * 60)


def test_image_search():
    """Test image-based search"""
    print("\n" + "=" * 60)
    print("測試：圖片搜尋")
    print("=" * 60)

    handler = QueryHandler()
    handler.load_vector_store()

    # Use first product image
    test_image = "data/images/1075.jpg"
    print(f"\n查詢圖片: {test_image}\n")

    results = handler.search_by_image(image_path=test_image, top_k=5)

    print(f"找到 {len(results)} 個結果:\n")
    for i, product in enumerate(results, 1):
        print(f"{i}. {product['name']}")
        print(f"   分類: {product['category']}")
        print(f"   相似度: {product['similarity']:.4f}")
        print(f"   ID: {product['product_id']}")
        if i == 1:
            print("   ⭐ (查詢圖片本身)")
        print()

    print("=" * 60)


def test_similar_products():
    """Test finding similar products"""
    print("\n" + "=" * 60)
    print("測試：找相似產品")
    print("=" * 60)

    handler = QueryHandler()
    handler.load_vector_store()

    # Get reference product
    product_id = "1075"
    reference_product = handler.get_product(product_id)

    print(f"\n參考產品: {reference_product['name']}")
    print(f"分類: {reference_product['category']}")
    print(f"\n尋找相似產品...\n")

    results = handler.search_similar(product_id, top_k=5)

    print(f"找到 {len(results)} 個相似產品:\n")
    for i, product in enumerate(results, 1):
        print(f"{i}. {product['name']}")
        print(f"   分類: {product['category']}")
        print(f"   相似度: {product['similarity']:.4f}")
        print(f"   ID: {product['product_id']}")
        print()

    print("=" * 60)


def test_multimodal_search():
    """Test multimodal search (text + image)"""
    print("\n" + "=" * 60)
    print("測試：混合搜尋（文字 + 圖片）")
    print("=" * 60)

    handler = QueryHandler()
    handler.load_vector_store()

    # Test with text and image
    test_image = "data/images/1075.jpg"
    query_text = "電源相關配件"

    print(f"\n查詢文字: {query_text}")
    print(f"查詢圖片: {test_image}\n")

    results = handler.search_multimodal(
        query_text=query_text,
        image_path=test_image,
        top_k=5
    )

    print(f"找到 {len(results)} 個結果:\n")
    for i, product in enumerate(results, 1):
        print(f"{i}. {product['name']}")
        print(f"   分類: {product['category']}")
        print(f"   相似度: {product['similarity']:.4f}")
        print(f"   ID: {product['product_id']}")
        print()

    print("=" * 60)


def test_stats():
    """Test getting statistics"""
    print("\n" + "=" * 60)
    print("向量資料庫統計")
    print("=" * 60)

    handler = QueryHandler()
    handler.load_vector_store()

    stats = handler.get_stats()

    print(f"\n總產品數: {stats['total_products']}")
    print(f"向量維度: {stats['embedding_dimension']}")
    print(f"總向量數: {stats['total_embeddings']}")
    print(f"\n產品分類 ({len(stats['categories'])} 個):")
    for category in stats['categories']:
        print(f"  - {category}")

    print("\n" + "=" * 60)


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("向量搜尋功能測試")
    print("=" * 60)

    try:
        # Test 1: Stats
        test_stats()

        # Test 2: Text search
        test_text_search()

        # Test 3: Image search
        test_image_search()

        # Test 4: Similar products
        test_similar_products()

        # Test 5: Multimodal search
        test_multimodal_search()

        print("\n" + "=" * 60)
        print("✅ 所有測試完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

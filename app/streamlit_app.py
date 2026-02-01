"""
Streamlit UI for U-Chance AI Visual Search
"""
import sys
import os
from pathlib import Path

import streamlit as st
from PIL import Image

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from search.query_handler import QueryHandler


# Page config
st.set_page_config(
    page_title="優誠傢俱 AI 搜尋",
    page_icon="🔍",
    layout="wide"
)


@st.cache_resource
def load_query_handler():
    """Load and cache query handler"""
    handler = QueryHandler()
    handler.load_vector_store()
    return handler


def display_product_card(product: dict, show_similarity: bool = True, card_id: str = ""):
    """Display a product card"""
    col1, col2 = st.columns([1, 2])

    with col1:
        # Display image
        if product.get('local_image_path') and os.path.exists(product['local_image_path']):
            try:
                image = Image.open(product['local_image_path'])
                st.image(image, use_container_width=True)
            except Exception as e:
                st.error(f"無法載入圖片: {e}")
        else:
            st.info("圖片不可用")

    with col2:
        # Product info
        st.subheader(product['name'])
        st.write(f"**分類**: {product['category']}")

        if show_similarity and 'similarity' in product:
            similarity_pct = product['similarity'] * 100
            st.metric("相似度", f"{similarity_pct:.1f}%")

        # Description (truncated)
        if product.get('description'):
            desc = product['description']
            if len(desc) > 150:
                desc = desc[:150] + "..."
            st.write(desc)

        # Links
        col_a, col_b = st.columns(2)
        with col_a:
            # Use card_id to make button key unique
            btn_key = f"similar_{product['product_id']}_{card_id}"
            if st.button("🔍 找相似產品", key=btn_key):
                st.session_state.search_mode = "similar"
                st.session_state.similar_product_id = product['product_id']
                st.rerun()

        with col_b:
            if product.get('detail_url'):
                st.link_button("📄 產品詳情", product['detail_url'])


def main():
    """Main application"""

    # Title
    st.title("🔍 優誠傢俱 AI 視覺搜尋")
    st.markdown("使用 AI 找到最適合的辦公傢俱")

    # Load handler
    try:
        handler = load_query_handler()
    except Exception as e:
        st.error(f"載入失敗: {e}")
        st.stop()

    # Sidebar - Stats
    with st.sidebar:
        st.header("📊 資料庫統計")
        stats = handler.get_stats()
        st.metric("產品數量", stats['total_products'])
        st.metric("產品分類", len(stats['categories']))

        st.markdown("---")
        st.subheader("產品分類")
        for category in stats['categories']:
            st.write(f"• {category}")

        st.markdown("---")
        st.info("""
        **搜尋方式**
        1. 📝 文字搜尋
        2. 🖼️ 圖片搜尋
        3. 🎨 混合搜尋
        """)

    # Search mode tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 文字搜尋", "🖼️ 圖片搜尋", "🎨 混合搜尋", "📚 瀏覽所有"])

    # Tab 1: Text Search
    with tab1:
        st.header("文字搜尋")
        query_text = st.text_input(
            "輸入關鍵字",
            placeholder="例如：升降桌、電源插座、主管桌...",
            key="text_search_input"
        )

        col1, col2 = st.columns([1, 3])
        with col1:
            top_k = st.number_input("顯示結果數", min_value=1, max_value=20, value=6, key="text_top_k")

        if st.button("🔍 搜尋", key="text_search_btn", type="primary"):
            if query_text:
                with st.spinner("搜尋中..."):
                    try:
                        results = handler.search_by_text(query_text, top_k=top_k)

                        if results:
                            st.success(f"找到 {len(results)} 個相關產品")

                            # Display results in grid
                            cols = st.columns(3)
                            for idx, product in enumerate(results):
                                with cols[idx % 3]:
                                    with st.container(border=True):
                                        display_product_card(product, card_id=f"text_{idx}")
                        else:
                            st.warning("沒有找到相關產品")
                    except Exception as e:
                        st.error(f"搜尋失敗: {e}")
            else:
                st.warning("請輸入搜尋關鍵字")

    # Tab 2: Image Search
    with tab2:
        st.header("圖片搜尋")
        st.write("上傳圖片找相似的產品")

        uploaded_file = st.file_uploader(
            "選擇圖片",
            type=['jpg', 'jpeg', 'png'],
            key="image_upload"
        )

        col1, col2 = st.columns([1, 3])
        with col1:
            top_k = st.number_input("顯示結果數", min_value=1, max_value=20, value=6, key="image_top_k")

        if uploaded_file:
            # Show uploaded image
            st.subheader("上傳的圖片")
            image = Image.open(uploaded_file)
            st.image(image, width=300)

            if st.button("🔍 搜尋相似產品", key="image_search_btn", type="primary"):
                with st.spinner("搜尋中..."):
                    try:
                        # Read image bytes
                        uploaded_file.seek(0)
                        image_bytes = uploaded_file.read()

                        results = handler.search_by_image(
                            image_bytes=image_bytes,
                            top_k=top_k
                        )

                        if results:
                            st.success(f"找到 {len(results)} 個相似產品")

                            # Display results
                            cols = st.columns(3)
                            for idx, product in enumerate(results):
                                with cols[idx % 3]:
                                    with st.container(border=True):
                                        display_product_card(product, card_id=f"img_{idx}")
                        else:
                            st.warning("沒有找到相似產品")
                    except Exception as e:
                        st.error(f"搜尋失敗: {e}")

    # Tab 3: Multimodal Search
    with tab3:
        st.header("混合搜尋（文字 + 圖片）")
        st.write("結合文字描述和圖片，找到最精確的產品")

        query_text = st.text_input(
            "文字描述",
            placeholder="例如：白色、木質、現代風格...",
            key="multimodal_text"
        )

        uploaded_file = st.file_uploader(
            "上傳參考圖片",
            type=['jpg', 'jpeg', 'png'],
            key="multimodal_image"
        )

        col1, col2 = st.columns([1, 3])
        with col1:
            top_k = st.number_input("顯示結果數", min_value=1, max_value=20, value=6, key="multimodal_top_k")

        if uploaded_file:
            st.subheader("參考圖片")
            image = Image.open(uploaded_file)
            st.image(image, width=300)

        if st.button("🔍 混合搜尋", key="multimodal_search_btn", type="primary"):
            if query_text or uploaded_file:
                with st.spinner("搜尋中..."):
                    try:
                        image_bytes = None
                        if uploaded_file:
                            uploaded_file.seek(0)
                            image_bytes = uploaded_file.read()

                        results = handler.search_multimodal(
                            query_text=query_text if query_text else None,
                            image_bytes=image_bytes,
                            top_k=top_k
                        )

                        if results:
                            st.success(f"找到 {len(results)} 個相關產品")

                            # Display results
                            cols = st.columns(3)
                            for idx, product in enumerate(results):
                                with cols[idx % 3]:
                                    with st.container(border=True):
                                        display_product_card(product, card_id=f"multi_{idx}")
                        else:
                            st.warning("沒有找到相關產品")
                    except Exception as e:
                        st.error(f"搜尋失敗: {e}")
            else:
                st.warning("請輸入文字描述或上傳圖片")

    # Tab 4: Browse All
    with tab4:
        st.header("瀏覽所有產品")

        # Filter by category
        all_products = handler.get_all_products()
        categories = ["全部"] + stats['categories']
        selected_category = st.selectbox("篩選分類", categories)

        # Filter products
        if selected_category != "全部":
            filtered_products = [p for p in all_products if p['category'] == selected_category]
        else:
            filtered_products = all_products

        st.write(f"顯示 {len(filtered_products)} 個產品")

        # Display products
        cols = st.columns(3)
        for idx, product in enumerate(filtered_products):
            with cols[idx % 3]:
                with st.container(border=True):
                    display_product_card(product, show_similarity=False, card_id=f"browse_{idx}")

    # Handle "find similar" from session state
    if st.session_state.get('search_mode') == 'similar':
        product_id = st.session_state.get('similar_product_id')
        if product_id:
            st.markdown("---")
            st.header("🔍 相似產品")

            reference_product = handler.get_product(product_id)
            st.subheader(f"基於: {reference_product['name']}")

            with st.spinner("搜尋相似產品..."):
                try:
                    results = handler.search_similar(product_id, top_k=6)

                    if results:
                        st.success(f"找到 {len(results)} 個相似產品")

                        cols = st.columns(3)
                        for idx, product in enumerate(results):
                            with cols[idx % 3]:
                                with st.container(border=True):
                                    display_product_card(product, card_id=f"similar_{idx}")
                    else:
                        st.warning("沒有找到相似產品")
                except Exception as e:
                    st.error(f"搜尋失敗: {e}")

            # Reset state
            if st.button("返回"):
                st.session_state.search_mode = None
                st.session_state.similar_product_id = None
                st.rerun()


if __name__ == "__main__":
    # Initialize session state
    if 'search_mode' not in st.session_state:
        st.session_state.search_mode = None
    if 'similar_product_id' not in st.session_state:
        st.session_state.similar_product_id = None

    main()

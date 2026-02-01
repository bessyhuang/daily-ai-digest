# 優誠傢俱 AI 視覺搜尋 POC

## 專案目標

為台灣辦公傢俱網站 https://www.u-chance.com.tw/ 建立 AI 視覺搜尋功能，讓使用者可以：
1. 上傳圖片找相似產品
2. 用自然語言描述搜尋（如「白色升降桌」）
3. 點擊產品圖找類似款式

## 技術架構

```
使用者介面 (Streamlit)
       ↓
Amazon Bedrock (Titan Multimodal Embeddings)
       ↓
向量資料庫 (PostgreSQL + pgvector 或 純 numpy POC)
       ↓
產品資料 (爬蟲取得)
```

## Phase 1：資料爬取

### 目標網站結構
- 產品列表：`https://www.u-chance.com.tw/products/all/{page}` (共 81 頁)
- 產品詳情：`https://www.u-chance.com.tw/products_detail/{id}`
- 圖片路徑：`https://www.u-chance.com.tw/upload/products/...`

### 需要爬取的資料
```python
{
    "product_id": "1076",
    "name": "L-1 片狀全玻高隔間",
    "category": "高隔間",
    "description": "黑 .銀清玻 / 表面局部磨砂處理",
    "image_url": "https://www.u-chance.com.tw/upload/products/...",
    "detail_url": "https://www.u-chance.com.tw/products_detail/1076"
}
```

### 爬蟲需求
- 使用 requests + BeautifulSoup 或 Playwright
- 遵守 robots.txt，加入延遲避免被封
- 儲存為 JSON + 下載圖片到本地

## Phase 2：Embedding 生成

### AWS Bedrock 設定
- Model: `amazon.titan-embed-image-v1`
- Region: `us-east-1` (或其他支援 Bedrock 的區域)
- 輸出維度: 1024 (預設) 或 384 (較小)

### 程式碼範例
```python
import boto3
import base64
import json

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def get_embedding(image_path=None, text=None):
    body = {}
    
    if image_path:
        with open(image_path, 'rb') as f:
            body["inputImage"] = base64.b64encode(f.read()).decode()
    
    if text:
        body["inputText"] = text
    
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-image-v1",
        body=json.dumps(body)
    )
    
    result = json.loads(response['body'].read())
    return result['embedding']
```

### 成本估算
- 圖片: $0.00006/張
- 1000 張產品圖 ≈ $0.06

## Phase 3：向量搜尋

### POC 簡易版 (numpy)
```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class SimpleVectorSearch:
    def __init__(self):
        self.embeddings = []  # List of numpy arrays
        self.metadata = []    # List of product info dicts
    
    def add(self, embedding, product_info):
        self.embeddings.append(embedding)
        self.metadata.append(product_info)
    
    def search(self, query_embedding, top_k=5):
        if not self.embeddings:
            return []
        
        embeddings_matrix = np.array(self.embeddings)
        query = np.array(query_embedding).reshape(1, -1)
        
        similarities = cosine_similarity(query, embeddings_matrix)[0]
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                **self.metadata[idx],
                'similarity': float(similarities[idx])
            })
        return results
```

### 進階版 (PostgreSQL + pgvector)
```sql
-- 需要先安裝 pgvector 擴展
CREATE EXTENSION vector;

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(50) UNIQUE,
    name VARCHAR(255),
    category VARCHAR(100),
    description TEXT,
    image_url VARCHAR(500),
    embedding vector(1024)
);

-- 搜尋查詢
SELECT product_id, name, image_url,
       1 - (embedding <=> $1::vector) as similarity
FROM products
ORDER BY embedding <=> $1::vector
LIMIT 10;
```

## Phase 4：Streamlit UI

### 基本功能
```python
import streamlit as st

st.title("優誠傢俱 AI 搜尋")

# 搜尋方式選擇
search_type = st.radio("搜尋方式", ["文字搜尋", "圖片搜尋"])

if search_type == "文字搜尋":
    query = st.text_input("輸入關鍵字", placeholder="例如：白色升降桌")
    if query:
        # 取得文字 embedding
        embedding = get_embedding(text=query)
        results = vector_db.search(embedding, top_k=12)
        display_results(results)

elif search_type == "圖片搜尋":
    uploaded_file = st.file_uploader("上傳圖片", type=['jpg', 'jpeg', 'png'])
    if uploaded_file:
        # 取得圖片 embedding
        embedding = get_embedding(image_bytes=uploaded_file.read())
        results = vector_db.search(embedding, top_k=12)
        display_results(results)

def display_results(results):
    cols = st.columns(4)
    for i, product in enumerate(results):
        with cols[i % 4]:
            st.image(product['image_url'])
            st.write(f"**{product['name']}**")
            st.write(f"相似度: {product['similarity']:.2%}")
            st.write(f"[查看詳情]({product['detail_url']})")
```

## 專案結構

```
u-chance-ai-search/
├── README.md
├── requirements.txt
├── config.py                 # AWS 設定、常數
├── scraper/
│   ├── __init__.py
│   ├── product_scraper.py    # 爬蟲主程式
│   └── utils.py              # 輔助函數
├── embeddings/
│   ├── __init__.py
│   ├── bedrock_client.py     # Bedrock API 封裝
│   └── batch_embed.py        # 批次產生 embedding
├── search/
│   ├── __init__.py
│   ├── vector_store.py       # 向量儲存與搜尋
│   └── query_handler.py      # 搜尋邏輯
├── app/
│   └── streamlit_app.py      # Streamlit UI
├── data/
│   ├── products.json         # 產品資料
│   ├── embeddings.npy        # Embedding 向量
│   └── images/               # 下載的產品圖片
└── notebooks/
    └── poc_exploration.ipynb # 測試用 notebook
```

## requirements.txt

```
# Web scraping
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0

# AWS
boto3>=1.34.0

# Vector search
numpy>=1.24.0
scikit-learn>=1.3.0

# UI
streamlit>=1.29.0
Pillow>=10.0.0

# Optional: PostgreSQL
# psycopg2-binary>=2.9.0
# pgvector>=0.2.0

# Development
python-dotenv>=1.0.0
tqdm>=4.66.0
```

## 環境變數 (.env)

```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1

# Optional: PostgreSQL
# DATABASE_URL=postgresql://user:pass@localhost:5432/uchance
```

## 開發步驟

### Step 1: 爬取產品資料
```bash
python -m scraper.product_scraper
# 輸出: data/products.json + data/images/
```

### Step 2: 產生 Embeddings
```bash
python -m embeddings.batch_embed
# 輸出: data/embeddings.npy
```

### Step 3: 啟動 UI
```bash
streamlit run app/streamlit_app.py
```

## 注意事項

1. **AWS 權限**: 需要 `bedrock:InvokeModel` 權限
2. **爬蟲禮儀**: 加入 1-2 秒延遲，避免對網站造成負擔
3. **圖片大小**: Titan 限制 25MB，需檢查並調整
4. **中文支援**: Titan 對中文效果有限，可考慮同時用英文描述

## 預期成果

- [ ] 成功爬取 1000+ 產品資料
- [ ] 產生所有產品的 embedding
- [ ] Streamlit UI 可正常搜尋
- [ ] 文字搜尋「升降桌」能找到相關產品
- [ ] 上傳椅子圖片能找到類似椅子
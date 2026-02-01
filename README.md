# 優誠傢俱 AI 視覺搜尋 POC

為台灣辦公傢俱網站 [優誠傢俱](https://www.u-chance.com.tw/) 建立 AI 視覺搜尋功能。

## 功能

1. 上傳圖片找相似產品
2. 用自然語言描述搜尋（如「白色升降桌」）
3. 點擊產品圖找類似款式

## 技術架構

- **網頁爬蟲**: requests + BeautifulSoup
- **向量嵌入**: Amazon Bedrock Titan Multimodal Embeddings
- **向量搜尋**: numpy (POC) 或 PostgreSQL + pgvector
- **使用者介面**: Streamlit

## 專案結構

```
daily-ai-digest/
├── README.md
├── requirements.txt
├── config.py                 # AWS 設定、常數
├── .env.example              # 環境變數範本
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

## 安裝

### 1. 安裝 uv（如果尚未安裝）

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 安裝套件

```bash
uv sync
```

這會自動建立虛擬環境並安裝所有依賴套件。

### 3. 設定環境變數

複製 `.env.example` 為 `.env` 並填入你的 AWS 憑證：

```bash
cp .env.example .env
```

編輯 `.env` 檔案：

```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
```

## 使用方法

### Step 1: 爬取產品資料

```bash
uv run python -m scraper.product_scraper
```

這會：
- 爬取所有產品頁面（共 81 頁）
- 下載產品圖片到 `data/images/`
- 儲存產品資訊到 `data/products.json`

**注意**: 完整爬取可能需要較長時間。測試時可以先修改 `product_scraper.py` 中的範圍：

```python
# 測試用：只爬取前 2 頁
scraper.scrape_all_products(start_page=1, end_page=2)
```

### Step 2: 產生 Embeddings

```bash
uv run python -m embeddings.batch_embed
```

輸出: `data/embeddings.npy`

### Step 3: 啟動 UI

```bash
uv run streamlit run app/streamlit_app.py
```

## 爬蟲功能說明

### 目標網站結構

- 產品列表: `https://www.u-chance.com.tw/products/all/{page}` (共 81 頁)
- 產品詳情: `https://www.u-chance.com.tw/products_detail/{id}`
- 圖片路徑: `https://www.u-chance.com.tw/upload/products/...`

### 爬取資料格式

```json
{
  "product_id": "1076",
  "name": "L-1 片狀全玻高隔間",
  "category": "高隔間",
  "description": "黑 .銀清玻 / 表面局部磨砂處理",
  "image_url": "https://www.u-chance.com.tw/upload/products/...",
  "detail_url": "https://www.u-chance.com.tw/products_detail/1076",
  "local_image_path": "data/images/1076.jpg"
}
```

### 爬蟲特性

- 遵守爬蟲禮儀，每個請求間隔 1.5 秒
- 自動重試失敗的請求
- 支援斷點續爬
- 顯示進度條

## 注意事項

1. **AWS 權限**: 確保你的 AWS 帳戶有 `bedrock:InvokeModel` 權限
2. **爬蟲禮儀**: 預設延遲 1.5 秒，請勿修改為更短的時間
3. **圖片大小**: Amazon Titan 限制 25MB，大圖片會自動跳過
4. **中文支援**: Titan 對中文效果有限，建議同時使用英文描述

## 開發狀態

- [x] Step 1: 產品資料爬取
- [ ] Step 2: Embeddings 生成
- [ ] Step 3: 向量搜尋功能
- [ ] Step 4: Streamlit UI

## 成本估算

- 圖片 embedding: $0.00006/張
- 1000 張產品圖 ≈ $0.06

## License

MIT

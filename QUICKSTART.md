# 快速開始

## 環境設定

```bash
# 1. 安裝 uv（如果尚未安裝）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 安裝專案依賴
uv sync

# 3. 設定環境變數
cp .env.example .env
# 然後編輯 .env 填入你的 AWS 憑證
```

## Step 1: 執行爬蟲

```bash
# 測試模式（前 2 頁，config.py 中設定 TOTAL_PAGES = 2）
uv run python -m scraper.product_scraper

# 完整爬取（需修改 config.py 設定 TOTAL_PAGES = 81）
uv run python -m scraper.product_scraper
```

輸出：
- 產品資料: `data/products.json`
- 產品圖片: `data/images/*.png`, `*.jpg`

## Step 2: 產生 Embeddings

```bash
# 測試 AWS Bedrock 連線（建議先執行）
uv run python test_embeddings.py

# 批次產生所有產品的 embeddings
uv run python -m embeddings.batch_embed
```

輸出：
- Embedding 向量: `data/embeddings.npy`
- Metadata: `data/embeddings_metadata.json`

**注意事項**：
- 確保 `.env` 檔案中已設定 AWS 憑證
- 需要有 Bedrock 的 `InvokeModel` 權限
- 24 個產品約需 3-5 分鐘生成
- 費用: ~$0.0015 (24 張圖片 × $0.00006)

## 下一步

- [ ] Step 3: 建立向量搜尋
- [ ] Step 4: 建立 Streamlit UI

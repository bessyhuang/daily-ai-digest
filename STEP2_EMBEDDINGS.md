# Step 2: Embeddings 生成

## 概述

使用 AWS Bedrock 的 Titan Multimodal Embeddings 模型將產品圖片和文字描述轉換為向量。

## 已實作檔案

### 1. `embeddings/bedrock_client.py`

AWS Bedrock 客戶端封裝，提供三種 embedding 方法：

- `get_text_embedding(text)` - 純文字 embedding
- `get_image_embedding(image_path/image_bytes)` - 純圖片 embedding
- `get_multimodal_embedding(text, image)` - 圖文混合 embedding

**特點**：
- 自動從環境變數讀取 AWS 憑證
- 完整的錯誤處理
- 支援檔案路徑或 bytes 輸入

### 2. `embeddings/batch_embed.py`

批次處理所有產品的 embedding 生成：

- 讀取 `data/products.json`
- 為每個產品生成 multimodal embedding（圖片 + 文字描述）
- 儲存為 numpy 陣列（`data/embeddings.npy`）
- 產生 metadata 檔案記錄成功/失敗狀態

**特點**：
- 顯示進度條
- 失敗產品使用零向量填充
- 可設定 API 呼叫延遲避免限流

### 3. `test_embeddings.py`

測試腳本，驗證 AWS Bedrock 連線是否正常：

- 測試文字 embedding
- 測試圖片 embedding
- 測試 multimodal embedding

## 使用方式

### 1. 設定 AWS 憑證

編輯 `.env` 檔案：

```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
```

### 2. 測試連線

```bash
uv run python test_embeddings.py
```

應該會看到三個測試都成功：

```
✓ Successfully generated text embedding!
✓ Successfully generated image embedding!
✓ Successfully generated multimodal embedding!
```

### 3. 批次生成 Embeddings

```bash
uv run python -m embeddings.batch_embed
```

輸出範例：

```
Loaded 24 products
Generating embeddings for 24 products...
Model: amazon.titan-embed-image-v1
Embedding dimension: 1024

Generating embeddings: 100%|████████| 24/24 [00:30<00:00]

Successfully generated 24/24 embeddings
Saved embeddings to data/embeddings.npy
Shape: (24, 1024)
Size: 96.00 KB
```

## 輸出檔案

### `data/embeddings.npy`

NumPy 陣列檔案，shape 為 `(n_products, 1024)`：
- 每個產品一個 1024 維的向量
- 使用 float32 格式節省空間
- 可用 `np.load('data/embeddings.npy')` 讀取

### `data/embeddings_metadata.json`

Metadata 檔案，記錄：

```json
{
  "total_products": 24,
  "successful_embeddings": 24,
  "failed_products": [],
  "embedding_dimension": 1024,
  "model_id": "amazon.titan-embed-image-v1"
}
```

## 技術細節

### Titan Multimodal Embeddings

- **Model ID**: `amazon.titan-embed-image-v1`
- **維度**: 1024
- **輸入**: 文字、圖片或兩者
- **定價**: $0.00006 / 圖片

### 生成策略

本專案使用 **multimodal embedding**：

```python
text = f"{product_name} - {category} - {description}"
embedding = client.get_multimodal_embedding(
    text=text,
    image_path=image_path
)
```

**優點**：
- 結合視覺和語義資訊
- 提升搜尋準確度
- 支援文字和圖片查詢

## 成本估算

| 產品數量 | 費用 (USD) |
|---------|-----------|
| 24      | $0.00144  |
| 100     | $0.006    |
| 1000    | $0.06     |

## 常見問題

### Q1: 為什麼要用 multimodal embedding？

同時使用圖片和文字能獲得更好的語義理解，讓搜尋結果更準確。

### Q2: 如果某些產品沒有圖片怎麼辦？

程式會自動跳過並使用零向量填充，記錄在 `failed_products` 中。

### Q3: 可以只用圖片或只用文字嗎？

可以，修改 `batch_embed.py` 中的 `generate_product_embedding` 方法即可。

### Q4: 生成速度太慢怎麼辦？

可以調整 `batch_embed.py` 中的 `delay` 參數，但不建議設太低以避免被限流。

## 下一步

完成 embedding 生成後，可以進行：

1. **Step 3: 向量搜尋** - 建立搜尋引擎
2. **Step 4: Streamlit UI** - 建立使用者介面

執行：

```bash
# 查看快速開始指南
cat QUICKSTART.md
```

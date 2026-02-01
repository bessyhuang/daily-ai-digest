# 爬蟲更新說明

## 更新日期
2026-01-29

## 更新內容

### 修正的選擇器

針對 u-chance.com.tw 網站的實際 HTML 結構，更新了以下選擇器：

1. **產品名稱**: 從 `h1` 標籤取得
2. **產品分類**: 從 `h2` 標籤取得
3. **產品描述**: 從 `.products-detail` div 取得
4. **產品圖片**: 過濾只取得 `/products/` 路徑的圖片（排除 site_info）

### 測試結果

成功抓取產品 ID 383 的資料：

```json
{
  "product_id": "383",
  "name": "DS-A9035T_主桌+側桌櫃+袖櫃",
  "category": "高階主管桌",
  "description": "詳細介紹DS-A9035T-H主桌栓木J1色197*90*75優惠價：73800定價：123000...",
  "image_url": "https://www.u-chance.com.tw/upload/products/t_20230129235432d45aq.png",
  "detail_url": "https://www.u-chance.com.tw/products_detail/383"
}
```

### 新增測試腳本

建立 `test_scraper.py` 用於測試爬蟲功能：

```bash
# 測試單一產品
uv run python test_scraper.py
```

測試包含：
- 抓取產品詳細頁面
- 下載產品圖片
- 抓取產品列表頁

## 使用方式

### 測試單一產品

```bash
uv run python test_scraper.py
```

### 爬取所有產品

```bash
# 測試模式（前 2 頁）
# 編輯 scraper/product_scraper.py 第 238 行
uv run python -m scraper.product_scraper

# 完整爬取（81 頁）
uv run python -m scraper.product_scraper
```

## 網站結構分析

### 產品列表頁
- URL: `https://www.u-chance.com.tw/products/all/{page}`
- 每頁約 12 個產品
- 共 81 頁

### 產品詳細頁
- URL: `https://www.u-chance.com.tw/products_detail/{id}`
- H1: 產品名稱
- H2: 產品分類
- .products-detail: 產品詳細說明
- img[src*="products"]: 產品圖片

## 注意事項

1. 爬蟲已設定 1.5 秒延遲，請勿縮短以避免對伺服器造成壓力
2. 圖片會自動下載到 `data/images/` 目錄
3. 產品資料會儲存到 `data/products.json`
4. 支援 PNG 和 JPG 圖片格式

"""
Configuration file for U-Chance AI Search POC
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
BEDROCK_MODEL_ID = 'amazon.titan-embed-image-v1'

# Scraping Configuration
BASE_URL = 'https://www.u-chance.com.tw'
PRODUCTS_LIST_URL = f'{BASE_URL}/products/all/'
PRODUCTS_DETAIL_URL = f'{BASE_URL}/products_detail/'
TOTAL_PAGES = 2 # 81
REQUEST_DELAY = 1.5  # seconds between requests

# Data Storage
DATA_DIR = 'data'
IMAGES_DIR = os.path.join(DATA_DIR, 'images')
PRODUCTS_JSON = os.path.join(DATA_DIR, 'products.json')
EMBEDDINGS_FILE = os.path.join(DATA_DIR, 'embeddings.npy')

# Search Configuration
TOP_K_RESULTS = 12
SIMILARITY_THRESHOLD = 0.5

# Optional: PostgreSQL Configuration
DATABASE_URL = os.getenv('DATABASE_URL')

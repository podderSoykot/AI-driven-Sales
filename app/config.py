from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).parent.parent

MODEL_NAME = "all-MiniLM-L6-v2"

DEFAULT_TOP_K = 10
MAX_TOP_K = 50
SIMILARITY_THRESHOLD = 0.0

API_TITLE = "Adaptive Transformer Search (ATS) API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "AI-powered semantic search engine for eCommerce products"

PRODUCTS_DATA_PATH = BASE_DIR / "data" / "products.json"


# Adaptive Transformer Search (ATS) Backend

An AI-powered semantic search engine for eCommerce products using transformer-based embeddings and FAISS for fast similarity search.

## Features

- **Semantic Search**: Uses transformer models (sentence-transformers) to understand query intent and find relevant products
- **Fast Vector Search**: FAISS index for efficient similarity search
- **Relevance Ranking**: Cosine similarity-based scoring for accurate results
- **Filtering**: Support for category, price range, and other filters
- **RESTful API**: Clean FastAPI endpoints with automatic documentation

## Architecture

- **Framework**: FastAPI (Python)
- **AI/ML**: sentence-transformers (`all-MiniLM-L6-v2`)
- **Vector Search**: FAISS (Facebook AI Similarity Search)
- **Data Models**: Pydantic for type validation

## Installation

1. **Clone or navigate to the project directory**

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## Usage

### Start the Server

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### API Endpoints

#### 1. Health Check
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "products_indexed": 15
}
```

#### 2. Search Products
```http
POST /search
Content-Type: application/json

{
  "query": "wireless headphones",
  "top_k": 10,
  "category": "Electronics",
  "min_price": 50.0,
  "max_price": 200.0
}
```

Response:
```json
{
  "query": "wireless headphones",
  "results": [
    {
      "product": {
        "id": "prod_001",
        "title": "Wireless Bluetooth Headphones",
        "description": "...",
        "category": "Electronics",
        "price": 199.99,
        ...
      },
      "score": 0.85,
      "rank": 1
    }
  ],
  "total_results": 1,
  "top_k": 10
}
```

#### 3. Get Product by ID
```http
GET /products/{product_id}
```

#### 4. Index New Products
```http
POST /index/products
Content-Type: application/json

[
  {
    "id": "prod_016",
    "title": "New Product",
    "description": "Product description",
    "category": "Electronics",
    "price": 99.99
  }
]
```

## Example Queries

Try these semantic search queries to see the AI in action:

- `"headphones for music"` - Finds audio products
- `"workout gear"` - Finds fitness-related items
- `"something to carry my laptop"` - Finds bags and backpacks
- `"device to charge my phone"` - Finds charging accessories
- `"comfortable shoes for running"` - Finds running shoes

The search engine understands intent and context, not just keyword matching!

## Configuration

Edit `app/config.py` to customize:

- **Model**: Change `MODEL_NAME` to use different transformer models
  - `all-MiniLM-L6-v2` (default) - Fast and lightweight
  - `ms-marco-MiniLM-L-6-v3` - Better for eCommerce search
- **Search Parameters**: Adjust `DEFAULT_TOP_K`, `MAX_TOP_K`, `SIMILARITY_THRESHOLD`

## Project Structure

```
caseStudy/
├── app/                 # Main application package
│   ├── __init__.py      # Package initialization
│   ├── main.py          # FastAPI application setup
│   ├── config.py        # Configuration settings
│   ├── api/             # API routes and endpoints
│   │   ├── __init__.py
│   │   └── routes.py    # API route handlers
│   ├── core/            # Core business logic
│   │   ├── __init__.py
│   │   └── search_engine.py  # Search engine implementation
│   └── models/          # Data models and schemas
│       ├── __init__.py
│       └── schemas.py   # Pydantic models
├── data/                # Data files
│   └── products.json    # Sample product data
├── tests/               # Test suite
│   └── __init__.py
├── main.py              # Entry point (runs app.main:app)
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## How It Works

1. **Product Indexing**: On startup, products are loaded and their embeddings are generated using the transformer model
2. **Embedding Generation**: Each product's title, description, category, brand, and tags are combined and converted to a vector embedding
3. **FAISS Index**: Embeddings are stored in a FAISS index for fast similarity search
4. **Query Processing**: User queries are converted to embeddings using the same model
5. **Similarity Search**: FAISS finds the most similar product embeddings using cosine similarity
6. **Ranking & Filtering**: Results are ranked by relevance score and filtered by any specified criteria

## Performance

- **Model Loading**: ~2-5 seconds on first startup
- **Indexing**: ~1-2 seconds for 15 products
- **Search**: <50ms per query (after indexing)

## Extending the System

- **Database Integration**: Replace JSON file with PostgreSQL, MongoDB, etc.
- **Advanced Filtering**: Add more filter options (brand, rating, availability)
- **Query Expansion**: Implement query expansion for better results
- **Multi-language**: Use multilingual transformer models
- **Caching**: Add Redis for query result caching
- **Analytics**: Track search queries and popular products

## License

This is a case study implementation for educational purposes.


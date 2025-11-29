import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router, set_search_engine
from app.models.schemas import Product
from app.core.search_engine import AdaptiveTransformerSearch
from app.config import API_TITLE, API_VERSION, API_DESCRIPTION, PRODUCTS_DATA_PATH

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

search_engine = AdaptiveTransformerSearch()
set_search_engine(search_engine)

app.include_router(router)


@app.on_event("startup")
async def startup_event():
    try:
        products_path = PRODUCTS_DATA_PATH
        if products_path.exists():
            with open(products_path, 'r', encoding='utf-8') as f:
                products_data = json.load(f)
                products = [Product(**item) for item in products_data]
                search_engine.load_products(products)
                search_engine.index_products()
                print(f"✓ Successfully loaded and indexed {len(products)} products")
        else:
            print(f"⚠ Warning: {products_path} not found. Starting with empty index.")
    except Exception as e:
        print(f"⚠ Error loading products: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


import json
from typing import List
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    Product,
    SearchQuery,
    SearchResponse,
    HealthResponse
)
from app.core.search_engine import AdaptiveTransformerSearch
from app.config import API_TITLE, API_VERSION, API_DESCRIPTION

router = APIRouter()

search_engine: AdaptiveTransformerSearch = None


def set_search_engine(engine: AdaptiveTransformerSearch):
    global search_engine
    search_engine = engine


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    return HealthResponse(
        status="healthy",
        model_loaded=search_engine.model is not None if search_engine else False,
        products_indexed=search_engine.get_indexed_count() if search_engine else 0
    )


@router.post("/search", response_model=SearchResponse, tags=["Search"])
async def search_products(query: SearchQuery):
    try:
        if not search_engine or not search_engine._is_indexed:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Search index not ready. Please wait for initialization."
            )
        
        results = search_engine.search(
            query=query.query,
            top_k=query.top_k,
            category=query.category,
            min_price=query.min_price,
            max_price=query.max_price
        )
        
        return SearchResponse(
            query=query.query,
            results=results,
            total_results=len(results),
            top_k=query.top_k
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid search request: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {str(e)}"
        )


@router.get("/products/{product_id}", response_model=Product, tags=["Products"])
async def get_product(product_id: str):
    if not search_engine:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search engine not initialized"
        )
    
    product = search_engine.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found"
        )
    return product


@router.post("/index/products", response_model=dict, tags=["Indexing"])
async def index_products(products: List[Product]):
    try:
        if not search_engine:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Search engine not initialized"
            )
        
        if not products:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Products list cannot be empty"
            )
        
        indexed_count = 0
        errors = []
        for product in products:
            try:
                search_engine.add_product(product)
                indexed_count += 1
            except ValueError as e:
                errors.append(f"Product {product.id}: {str(e)}")
        
        if errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Indexing completed with errors. Indexed: {indexed_count}/{len(products)}. Errors: {'; '.join(errors)}"
            )
        
        return {
            "message": f"Successfully indexed {indexed_count} product(s)",
            "total_indexed": search_engine.get_indexed_count()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Indexing error: {str(e)}"
        )


@router.get("/", tags=["Info"])
async def root():
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "description": API_DESCRIPTION,
        "docs": "/docs",
        "health": "/health"
    }


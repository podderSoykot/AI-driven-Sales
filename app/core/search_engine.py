import json
import os
from typing import List, Tuple, Optional
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from app.models.schemas import Product, SearchResult
from app.config import MODEL_NAME, DEFAULT_TOP_K, MAX_TOP_K


class AdaptiveTransformerSearch:
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or MODEL_NAME
        print(f"Loading transformer model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        self.products: List[Product] = []
        self.product_embeddings: np.ndarray = None
        self.index: faiss.Index = None
        self._is_indexed = False
    
    def load_products(self, products: List[Product]):
        if not products:
            raise ValueError("Products list cannot be empty")
        product_ids = [p.id for p in products]
        if len(product_ids) != len(set(product_ids)):
            duplicates = [pid for pid in product_ids if product_ids.count(pid) > 1]
            raise ValueError(f"Duplicate product IDs found: {set(duplicates)}")
        
        self.products = products
        print(f"Loaded {len(products)} products")
    
    def index_products(self):
        if not self.products:
            raise ValueError("No products loaded. Please load products first.")
        
        print("Generating embeddings for products...")
        
        searchable_texts = []
        for product in self.products:
            text_parts = [product.title, product.description, product.category]
            if product.brand:
                text_parts.append(product.brand)
            if product.tags:
                text_parts.extend(product.tags)
            searchable_text = " ".join(text_parts)
            searchable_texts.append(searchable_text)
        
        embeddings = self.model.encode(
            searchable_texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        self.product_embeddings = embeddings.astype('float32')
        
        faiss.normalize_L2(self.product_embeddings)
        
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.index.add(self.product_embeddings)
        
        self._is_indexed = True
        print(f"Indexed {len(self.products)} products successfully")
    
    def search(
        self,
        query: str,
        top_k: int = None,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[SearchResult]:
        if not self._is_indexed:
            raise ValueError("Products not indexed. Please call index_products() first.")
        
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")
        
        if min_price is not None and max_price is not None and min_price > max_price:
            raise ValueError("min_price cannot be greater than max_price")
        
        top_k = top_k or DEFAULT_TOP_K
        top_k = min(top_k, len(self.products), MAX_TOP_K)
        
        if top_k <= 0:
            return []
        
        query_embedding = self.model.encode(query, convert_to_numpy=True).astype('float32')
        query_embedding = query_embedding.reshape(1, -1)
        faiss.normalize_L2(query_embedding)
        
        scores, indices = self.index.search(query_embedding, min(top_k * 2, len(self.products)))
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx >= len(self.products):
                continue
            
            product = self.products[idx]
            
            if category and product.category.lower() != category.lower():
                continue
            if min_price is not None and product.price < min_price:
                continue
            if max_price is not None and product.price > max_price:
                continue
            
            normalized_score = float(max(0, min(1, score)))
            
            results.append(SearchResult(
                product=product,
                score=normalized_score,
                rank=len(results) + 1
            ))
            
            if len(results) >= top_k:
                break
        
        return results
    
    def add_product(self, product: Product):
        if self.get_product_by_id(product.id) is not None:
            raise ValueError(f"Product with ID '{product.id}' already exists in the index")
        
        self.products.append(product)
        
        text_parts = [product.title, product.description, product.category]
        if product.brand:
            text_parts.append(product.brand)
        if product.tags:
            text_parts.extend(product.tags)
        searchable_text = " ".join(text_parts)
        
        embedding = self.model.encode(searchable_text, convert_to_numpy=True).astype('float32')
        embedding = embedding.reshape(1, -1)
        faiss.normalize_L2(embedding)
        
        if self.index is None:
            self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.index.add(embedding)
        
        if self.product_embeddings is None:
            self.product_embeddings = embedding
        else:
            self.product_embeddings = np.vstack([self.product_embeddings, embedding])
        
        self._is_indexed = True
    
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        for product in self.products:
            if product.id == product_id:
                return product
        return None
    
    def get_indexed_count(self) -> int:
        return len(self.products) if self._is_indexed else 0


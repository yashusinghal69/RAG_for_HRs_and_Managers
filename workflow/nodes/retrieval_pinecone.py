from typing import Dict, Any, List
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
import numpy as np
from settings import (
    OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME
)

def document_retriever_node(state: Dict[str, Any]) -> Dict[str, Any]:
     
    print("🔍 Modern Hybrid Retrieval with Access Control: Dense + Sparse + Re-ranking...")
    
    query = state.get("enhanced_query", state["query"])
    user_role = state.get("user_role", "employee")   
    
    print(f"🔐 Filtering for user role: {user_role}")
    
    # Create embeddings once to save costs
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model="text-embedding-ada-002")
    query_embedding = embeddings.embed_query(query)
    
    dense_chunks = perform_dense_search(query, user_role, query_embedding=query_embedding)
     
    sparse_chunks = perform_sparse_search(query, user_role)
    
    hybrid_chunks = reciprocal_rank_fusion(dense_chunks, sparse_chunks, query, query_embedding=query_embedding, embeddings=embeddings)
    
    state["retrieved_chunks"] = hybrid_chunks
    return state


def perform_dense_search(query: str, user_role: str = "employee", top_k: int = 15, query_embedding: List[float] = None) -> List[Dict[str, Any]]:
  
    print(f"🧠 Performing dense semantic search with access control...")
    
    
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)
    
    metadata_filter = create_access_filter(user_role)
    print(f"🔐 Applying metadata filter: {metadata_filter}")
    
    search_results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter=metadata_filter  
    )
    
    retrieved_chunks = []
    for match in search_results.matches:
        metadata = match.metadata
        
        formatted_chunk = {
            "content": metadata.get("content", ""),
            "metadata": {
                "source": metadata.get("source"),
                "page": metadata.get("page"),
                "document_type": metadata.get("document_type"),
                "department": metadata.get("department"),
                "chunk_id": metadata.get("chunk_id", ""),
            },
            "score": match.score,
            "search_type": "dense",
            "rank": len(retrieved_chunks) + 1
        }
        retrieved_chunks.append(formatted_chunk)
    
    print(f"✅ Dense search retrieved {len(retrieved_chunks)} authorized chunks")
    return retrieved_chunks


def create_access_filter(user_role: str) -> Dict[str, Any]:
    
    if user_role == "hr":
        allowed_sources = ["novacorp_employee_handbook.txt", "novacorp_managers_guide.txt", "novacorp_hr_legal_manual.txt"]
    elif user_role == "manager":
        allowed_sources = ["novacorp_employee_handbook.txt", "novacorp_managers_guide.txt"]
    else:  
        allowed_sources = ["novacorp_employee_handbook.txt"]

    filter_conditions = {
        "source": {"$in": allowed_sources}
    }
    
    return filter_conditions


def perform_sparse_search(query: str, user_role: str = "employee", top_k: int = 15) -> List[Dict[str, Any]]:
 
    print(f"📝 Performing sparse TF-IDF search with access control...")
    
    tfidf_path = "tfidf_vectorizer.pkl"
    corpus_path = "document_corpus.pkl"
    tfidf_matrix_path = "tfidf_matrix.pkl"
    
    if not all(os.path.exists(path) for path in [tfidf_path, corpus_path, tfidf_matrix_path]):
        print("⚠️ TF-IDF index not found, creating from Pinecone data...")
        create_sparse_index()
 
    with open(tfidf_path, 'rb') as f:
        tfidf_vectorizer = pickle.load(f)
    
    with open(corpus_path, 'rb') as f:
        corpus_docs = pickle.load(f)
        
    with open(tfidf_matrix_path, 'rb') as f:
        tfidf_matrix = pickle.load(f)
    
    filtered_docs = []
    filtered_indices = []
    
    print(f"🔍 Total documents in corpus: {len(corpus_docs)}")
    
    for idx, doc in enumerate(corpus_docs):
        if is_document_accessible(doc, user_role):
            filtered_docs.append(doc)
            filtered_indices.append(idx)
    
    print(f"✅ Documents after access filtering: {len(filtered_docs)}")
    
    filtered_tfidf_matrix = tfidf_matrix[filtered_indices]
    
    query_vector = tfidf_vectorizer.transform([query.lower()])
 
    similarities = cosine_similarity(query_vector, filtered_tfidf_matrix).flatten()

    top_indices = np.argsort(similarities)[::-1][:top_k]
    
    retrieved_chunks = []
    for rank, idx in enumerate(top_indices):
        if similarities[idx] > 0.01:  # Minimum similarity threshold
            doc = filtered_docs[idx]
            doc_source = doc["metadata"].get("source", "unknown")
            print(f"📄 Retrieved chunk {rank+1}: source='{doc_source}', similarity={similarities[idx]:.4f}")
            
            formatted_chunk = {
                "content": doc["content"],
                "metadata": doc["metadata"],
                "score": float(similarities[idx]),
                "search_type": "sparse",
                "rank": rank + 1
            }
            retrieved_chunks.append(formatted_chunk)
    
    print(f"✅ Sparse search retrieved {len(retrieved_chunks)} authorized chunks")
    return retrieved_chunks



def is_document_accessible(doc: Dict[str, Any], user_role: str) -> bool:
    """Check if document is accessible based on user role and document source"""
    
    doc_source = doc["metadata"].get("source", "")
    
  
    if user_role == "hr":
 
        allowed_sources = ["novacorp_employee_handbook.txt", "novacorp_managers_guide.txt", "novacorp_hr_legal_manual.txt"]
    elif user_role == "manager":
 
        allowed_sources = ["novacorp_employee_handbook.txt", "novacorp_managers_guide.txt"]
    else:   
        allowed_sources = ["novacorp_employee_handbook.txt"]
    
    return doc_source in allowed_sources
        

def create_sparse_index():
    """Create TF-IDF sparse index from Pinecone data"""
    print("🔧 Creating TF-IDF sparse index from Pinecone data...")
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)
        
        # Get all documents from Pinecone
        query_result = index.query(
            vector=[0.0] * 1536,   
            top_k=10000, 
            include_metadata=True
        )
        
        corpus_texts = []
        corpus_docs = []
        
        for match in query_result.matches:
            metadata = match.metadata
            content = metadata.get("content", "")
            
            if content:
                corpus_texts.append(content.lower())
                
                # Store document with metadata
                doc = {
                    "content": content,
                    "metadata": {
                        "source": metadata.get("source"),
                        "page": metadata.get("page"),
                        "document_type": metadata.get("document_type"),
                        "department": metadata.get("department"),
                        "chunk_id": metadata.get("chunk_id", ""),
                    }
                }
                corpus_docs.append(doc)
        
        # Create TF-IDF vectorizer
        tfidf_vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 3),
            stop_words='english',
            min_df=2,
            max_df=0.95,
            sublinear_tf=True,
            norm='l2'
        )
        
        # Fit and transform the corpus
        tfidf_matrix = tfidf_vectorizer.fit_transform(corpus_texts)
        
        # Save components
        with open("tfidf_vectorizer.pkl", 'wb') as f:
            pickle.dump(tfidf_vectorizer, f)
        
        with open("document_corpus.pkl", 'wb') as f:
            pickle.dump(corpus_docs, f)
            
        with open("tfidf_matrix.pkl", 'wb') as f:
            pickle.dump(tfidf_matrix, f)
        
        print(f"✅ TF-IDF index created with {len(corpus_docs)} documents and {tfidf_matrix.shape[1]} features")
        
    except Exception as e:
        print(f"❌ Failed to create TF-IDF index: {e}")



def reciprocal_rank_fusion(dense_chunks: List[Dict], sparse_chunks: List[Dict], query: str, k: int = 60, query_embedding: List[float] = None, embeddings: OpenAIEmbeddings = None) -> List[Dict]:
 
    print("🔄 Applying Reciprocal Rank Fusion...")
    print(f"📊 Input: {len(dense_chunks)} dense chunks, {len(sparse_chunks)} sparse chunks")
    
    # Create document scoring map
    doc_scores = {}
    
    # Process dense search results
    for rank, chunk in enumerate(dense_chunks, 1):
        chunk_id = chunk["metadata"].get("chunk_id") or f"dense_{rank}_{hash(chunk['content'][:100])}"
        rrf_score = 1.0 / (k + rank)
        
        if chunk_id not in doc_scores:
            doc_scores[chunk_id] = {
                "chunk": chunk,
                "dense_rrf": rrf_score,
                "sparse_rrf": 0.0,
                "dense_rank": rank,
                "sparse_rank": None
            }
        else:
            doc_scores[chunk_id]["dense_rrf"] = rrf_score
            doc_scores[chunk_id]["dense_rank"] = rank
    
    # Process sparse search results
    for rank, chunk in enumerate(sparse_chunks, 1):
        chunk_id = chunk["metadata"].get("chunk_id") or f"sparse_{rank}_{hash(chunk['content'][:100])}"
        rrf_score = 1.0 / (k + rank)
        
        if chunk_id not in doc_scores:
            doc_scores[chunk_id] = {
                "chunk": chunk,
                "dense_rrf": 0.0,
                "sparse_rrf": rrf_score,
                "dense_rank": None,
                "sparse_rank": rank
            }
        else:
            doc_scores[chunk_id]["sparse_rrf"] = rrf_score
            doc_scores[chunk_id]["sparse_rank"] = rank
    
 
    
    final_results = []
    for chunk_id, scores in doc_scores.items():
        
        rrf_score = scores["dense_rrf"] + scores["sparse_rrf"]
        
        # Semantic similarity boost for re-ranking
        chunk_content = scores["chunk"]["content"]
        chunk_embedding = embeddings.embed_query(chunk_content[:500])  # Limit content for efficiency
        
        # Calculate cosine similarity
        similarity = np.dot(query_embedding, chunk_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding)
        )
        
        # Final hybrid score with semantic boost
        final_score = rrf_score + (0.1 * similarity)  # Small semantic boost
        
        # Create enhanced result
        enhanced_chunk = scores["chunk"].copy()
        enhanced_chunk.update({
            "rrf_score": rrf_score,
            "semantic_similarity": similarity,
            "final_score": final_score,
            "dense_rank": scores["dense_rank"],
            "sparse_rank": scores["sparse_rank"],
            "search_type": "hybrid_rrf"
        })
        
        final_results.append(enhanced_chunk)
    
    # Sort by final score and return top results
    final_results.sort(key=lambda x: x["final_score"], reverse=True)
    top_results = final_results[:8]
    
    print(f"✅ RRF fusion: {len(doc_scores)} unique docs → {len(top_results)} final results")
    
    if top_results:
        top_result = top_results[0]
        print(f"🏆 Top result: RRF={top_result['rrf_score']:.4f}, Semantic={top_result['semantic_similarity']:.4f}, Final={top_result['final_score']:.4f}")
    
    return top_results

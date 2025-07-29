import os
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

def create_embeddings_for_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

    embeddings_model = OpenAIEmbeddings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model="text-embedding-ada-002"  
    )
    
    embedded_chunks = []
    print(f"Creating embeddings for {len(chunks)} chunks...")
   
    batch_size = 50
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i + batch_size]
        
        batch_texts = [chunk["content"] for chunk in batch_chunks]
        batch_embeddings = embeddings_model.embed_documents(batch_texts)

        for chunk, embedding in zip(batch_chunks, batch_embeddings):
            embedded_chunk = chunk.copy()
            embedded_chunk["embedding"] = embedding
            embedded_chunks.append(embedded_chunk)
        
        print(f"Processed batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}")
            
    successful_embeddings = len([chunk for chunk in embedded_chunks if chunk["embedding"] is not None])
    print(f"Successfully created embeddings for {successful_embeddings}/{len(chunks)} chunks")
    
    return embedded_chunks


def validate_embeddings(embedded_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:

    total_chunks = len(embedded_chunks)
    valid_embeddings = 0
    invalid_embeddings = 0
    embedding_dimensions = None
    
    for chunk in embedded_chunks:
        if chunk["embedding"] is not None:
            valid_embeddings += 1
            if embedding_dimensions is None:
                embedding_dimensions = len(chunk["embedding"])
        else:
            invalid_embeddings += 1
    
    validation_stats = {
        "total_chunks": total_chunks,
        "valid_embeddings": valid_embeddings,
        "invalid_embeddings": invalid_embeddings,
        "success_rate": round((valid_embeddings / total_chunks) * 100, 2) if total_chunks > 0 else 0,
        "embedding_dimensions": embedding_dimensions
    }
    
    return validation_stats


def prepare_chunks_for_vector_db(embedded_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

    vector_db_chunks = []
    
    for chunk in embedded_chunks:
        if chunk["embedding"] is None:
            print(f"Skipping chunk without embedding: {chunk['metadata'].get('chunk_id', 'unknown')}")
            continue
        
        vector_chunk = {
            "id": chunk["metadata"]["chunk_id"],
            "content": chunk["content"],
            "embedding": chunk["embedding"],
            "metadata": {
                
                "source": chunk["metadata"]["source"],
                "page": chunk["metadata"]["page"],
                "chunk_index": chunk["metadata"]["chunk_index"],
                
                "access_level": chunk["metadata"]["access_level"],
                "allowed_roles": ",".join(chunk["metadata"]["allowed_roles"]),
                
                "document_type": chunk["metadata"]["document_type"],
                "department": chunk["metadata"]["department"],
 
                "chunk_size": chunk["metadata"]["chunk_size"],
                "total_chunks": chunk["metadata"]["total_chunks"]
            }
        }
        
        vector_db_chunks.append(vector_chunk)
    
    print(f"Prepared {len(vector_db_chunks)} chunks for vector database storage")
    return vector_db_chunks


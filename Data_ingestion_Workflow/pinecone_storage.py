import os
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec, CloudProvider, AwsRegion, Metric
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()


def delete_existing_index() -> bool:

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX_NAME")
    
    if pc.has_index(index_name):
        pc.delete_index(index_name)
        print(f"Deleted existing index: {index_name}")
    return True
   

def initialize_pinecone_connection():
     
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX_NAME")
    
    if not pc.has_index(index_name):
        print(f"Creating new Pinecone index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=1536,  
            metric=Metric.COSINE,
            spec=ServerlessSpec(
                cloud=CloudProvider.AWS,
                region=AwsRegion.US_EAST_1
            )
        )
        print(f"Created Pinecone index: {index_name}")
    
    index = pc.Index(index_name)
    print(f"Initialized Pinecone connection to index: {index_name}")
    return index
 

def store_chunks_in_pinecone(vector_db_chunks: List[Dict[str, Any]]) -> bool:
 
    delete_existing_index()
    index = initialize_pinecone_connection()
    
    print(f"Storing {len(vector_db_chunks)} chunks in Pinecone...")
    
    vectors = []
    for chunk in vector_db_chunks:
        metadata = chunk["metadata"]
        
        allowed_roles = metadata.get("allowed_roles", ["employee"])
        if isinstance(allowed_roles, list):
            allowed_roles = ",".join(allowed_roles)
        
        vectors.append({
            "id": chunk["id"],
            "values": chunk["embedding"],
            "metadata": {
                "content": chunk["content"],
                "source": metadata.get("source", ""),
                "page": metadata.get("page", 0),
                "access_level": metadata.get("access_level", "public"),
                "allowed_roles": allowed_roles,
                "document_type": metadata.get("document_type", ""),
                "department": metadata.get("department", ""),
                "chunk_index": metadata.get("chunk_index", 0),
                "chunk_size": metadata.get("chunk_size", 0),
                "total_chunks": metadata.get("total_chunks", 0)
            }
        })
    
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch)
        print(f"Uploaded batch {i//batch_size + 1}/{(len(vectors) + batch_size - 1)//batch_size}")
    
    print(f"✅ Successfully stored {len(vectors)} chunks with access control")
    return True

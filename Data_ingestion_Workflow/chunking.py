import os
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter


def chunk_documents(documents: List[Dict[str, Any]], use_semantic: bool = True) -> List[Dict[str, Any]]:
  
    print("🧠 Using chunking for better results...")
        
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,           
        chunk_overlap=100,        
        length_function=len,
        separators=["\n\n\n", "\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""],
        keep_separator=True,
        add_start_index=True      
    )
    
    chunked_documents = []
    
    for doc in documents:
        
        text_chunks = text_splitter.split_text(doc["content"])
        
 
        for chunk_index, chunk_text in enumerate(text_chunks):
            chunk_metadata = doc["metadata"].copy()
            
            chunk_metadata["chunk_index"] = chunk_index
            chunk_metadata["total_chunks"] = len(text_chunks)
            chunk_metadata["chunk_size"] = len(chunk_text)
     
            chunk_id = f"{chunk_metadata['source']}_page_{chunk_metadata['page']}_chunk_{chunk_index}"
            chunk_metadata["chunk_id"] = chunk_id
       
            chunk_doc = {
                "content": chunk_text.strip(),  # Remove extra whitespace
                "metadata": chunk_metadata
            }
            
            chunked_documents.append(chunk_doc)
    
    print(f"✅ Created {len(chunked_documents)} optimized chunks from {len(documents)} documents")
    
    return chunked_documents


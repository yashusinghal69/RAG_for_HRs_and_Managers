import os
import time
from typing import Dict, Any
from dotenv import load_dotenv
from pdf_extractor import extract_pdfs_from_documents_folder
from metadata_enrichment import enrich_document_metadata
from chunking import chunk_documents 
from embedding import create_embeddings_for_chunks, prepare_chunks_for_vector_db, validate_embeddings
from pinecone_storage import store_chunks_in_pinecone
load_dotenv()

def run_complete_ingestion_pipeline() -> Dict[str, Any]:

    print("=" * 80)
    print("STARTING HR RAG DATA INGESTION PIPELINE")
    print("=" * 80)

    print("\n🔍 STEP 1: PDF EXTRACTION")
    print("-" * 40)

    documents = extract_pdfs_from_documents_folder()

    print("\n📝 STEP 2: METADATA ENRICHMENT")
    print("-" * 40)

    enriched_docs = enrich_document_metadata(documents)

    print("\n✂️ STEP 3: DOCUMENT CHUNKING")
    print("-" * 40)
    
    chunks = chunk_documents(enriched_docs)
 
    print("\n🧠 STEP 4: EMBEDDING CREATION")
    print("-" * 40)
    
    embedded_chunks = create_embeddings_for_chunks(chunks)
    embedding_validation = validate_embeddings(embedded_chunks)
    vector_db_chunks = prepare_chunks_for_vector_db(embedded_chunks)
    
    print("\n💾 STEP 5: PINECONE STORAGE")
    print("-" * 40)

    store_chunks_in_pinecone(vector_db_chunks)
    
    print("\n✅ PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":

    run_complete_ingestion_pipeline()


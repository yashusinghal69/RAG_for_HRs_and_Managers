from typing import Dict, Any
from langchain_openai import ChatOpenAI
from utils.prompts import DOCUMENT_GRADER_PROMPT, QUERY_ENHANCER_PROMPT
from utils.helpers import extract_text_from_chunks
from  settings import OPENAI_API_KEY 

def grade_document_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("📊 Grading document relevance...")
 
    question = state["query"]
    chunks = state["retrieved_chunks"]   
    
    # Extract text from chunks
    documents = extract_text_from_chunks(chunks)  
    
    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model="gpt-4.1-mini",
        temperature=0
    )
    
    # Grade relevance
    prompt = DOCUMENT_GRADER_PROMPT.format(
        question=question,
        documents=documents
    )
    
    response = llm.invoke(prompt)
    grade = response.content.strip().lower()
    
    print(f"✅ Document grade: {grade}")
    
    state["document_grade"] = grade
    return state


def query_enhancer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("🔄 Enhancing query...")
  
    original_query = state["query"]
    retry_count = state.get("retry_count", 0)
    
    # Initialize LLM
    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model="gpt-4o-mini",
        temperature=0.3
    )
    
    # Enhance query
    prompt = QUERY_ENHANCER_PROMPT.format(query=original_query)
    response = llm.invoke(prompt)
    enhanced_query = response.content.strip()
    
    print(f"✅ Enhanced query: {enhanced_query}...")
    
    state["enhanced_query"] = enhanced_query
    state["retry_count"] = retry_count + 1
    
    return state
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from utils.prompts import HALLUCINATION_CHECK_PROMPT, RELEVANCE_CHECK_PROMPT
from utils.helpers import extract_text_from_chunks
from settings import OPENAI_API_KEY 


def hallucination_check_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("🔍 Checking for hallucinations...")
   
    answer = state["generated_answer"]
    chunks = state["retrieved_chunks"]
    
    # Extract source documents
    documents = extract_text_from_chunks(chunks)
    
    # Initialize LLM
    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model="gpt-4o-mini",
        temperature=0
    )
    
    # Check for hallucinations
    prompt = HALLUCINATION_CHECK_PROMPT.format(
        answer=answer,
        documents=documents
    )
    
    response = llm.invoke(prompt)
    check_result = response.content.strip().lower()
    
    print(f"✅ Hallucination check: {check_result}")
    
    state["hallucination_check"] = check_result
    return state


def relevance_check_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("🎯 Checking answer relevance...")

    question = state["query"]
    answer = state["generated_answer"]
    
   
    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model="gpt-4o-mini",
        temperature=0
    )
    
    
    prompt = RELEVANCE_CHECK_PROMPT.format(
        question=question,
        answer=answer
    )
    
    response = llm.invoke(prompt)
    check_result = response.content.strip().lower()
    
    print(f"✅ Relevance check: {check_result}")
    
    state["relevance_check"] = check_result
    return state
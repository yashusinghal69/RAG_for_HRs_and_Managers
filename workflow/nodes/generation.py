from typing import Dict, Any
from langchain_openai import ChatOpenAI
from utils.prompts import ANSWER_GENERATION_PROMPT
from utils.helpers import extract_text_from_chunks
from  settings import OPENAI_API_KEY

def generation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate answer using retrieved context."""
    print("📝 Generating answer...")
    
    question = state["query"]
    chunks = state["retrieved_chunks"]
    user_role = state["user_role"]
    
    # Extract context from chunks
    context = extract_text_from_chunks(chunks)
    
    # Initialize LLM
    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model="gpt-4o-mini",
    )
    
    # Generate answer
    prompt = ANSWER_GENERATION_PROMPT.format(
        user_role=user_role,
        question=question,
        context=context
    )
    
    response = llm.invoke(prompt)
    answer = response.content.strip()
    
    print(f"✅ Generated answer ({len(answer)} chars)")
    
    state["generated_answer"] = answer
    state["generation_retry_count"] = state.get("generation_retry_count", 0) + 1
    
    return state
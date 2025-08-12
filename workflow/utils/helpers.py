from typing import List, Dict, Any
import re
from datetime import datetime
from settings import SENSITIVE_KEYWORDS

def parse_user_role(user_id: str) -> str:
    """
    Parse user role from user_id.
    Now handles direct role strings from frontend: 'employee', 'hr', 'manager'
    Also handles legacy format: 'EMP123', 'HR456', 'MGR789'
    """
    user_id = user_id.lower().strip()
    
    # Direct role mapping (from frontend dropdown)
    if user_id in ["employee", "hr", "manager"]:
        return user_id
    
    # Legacy format with prefixes
    if user_id.startswith("emp"):
        return "employee"
    elif user_id.startswith("mgr"):
        return "manager"
    elif user_id.startswith("hr"):
        return "hr"
    else:
        # Default to employee if unrecognized
        return "employee"

def get_authorized_access_levels(user_role: str) -> List[str]:
  
    access_mapping = {
        "employee": ["public"],
        "manager": ["public", "manager"],
        "hr": ["public", "manager", "hr"]
    }
    return access_mapping.get(user_role, ["public"])


def extract_text_from_chunks(chunks: List[Dict[str, Any]]) -> str:
 
    texts = []
    for chunk in chunks:
        content = chunk.get("content", "")
        metadata = chunk.get("metadata", {})
        source = metadata.get("source", "Unknown")
        page = metadata.get("page", "Unknown")
        texts.append(f"[Source: {source}, Page: {page}]\n{content}")
    return "\n\n".join(texts)


def check_sensitive_content(text: str) -> bool:
 
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in SENSITIVE_KEYWORDS)


def calculate_confidence_components(state: Dict[str, Any]) -> Dict[str, float]:

    retrieval_scores = [chunk.get("score", 0.0) for chunk in state.get("retrieved_chunks", [])]
    retrieval_confidence = sum(retrieval_scores) / len(retrieval_scores) if retrieval_scores else 0.0
    
    # Document confidence
    document_confidence = 1.0 if state.get("document_grade") == "yes" else 0.0
    
    # Hallucination confidence
    hallucination_confidence = 1.0 if state.get("hallucination_check") == "no" else 0.0
    
    # Relevance confidence
    relevance_confidence = 1.0 if state.get("relevance_check") == "yes" else 0.0
    
    # Source confidence (based on number of sources)
    num_sources = len(state.get("retrieved_chunks", []))
    source_confidence = min(num_sources / 5.0, 1.0)  # Max confidence at 5+ sources
    
    return {
        "retrieval": retrieval_confidence,
        "document": document_confidence,
        "hallucination": hallucination_confidence,
        "relevance": relevance_confidence,
        "source": source_confidence
    }



def format_final_response(state: Dict[str, Any], response_type: str) -> Dict[str, Any]:
 
    base_response = {
        "timestamp": datetime.now().isoformat(),
        "user_role": state.get("user_role"),
        "status": response_type
    }
    
    if response_type == "success":
        sources = []
        for chunk in state.get("retrieved_chunks", []):
            metadata = chunk.get("metadata", {})
            sources.append({
                "source": metadata.get("source"),
                "page": metadata.get("page"),
                "section": metadata.get("chunk_id")
            })
        
        base_response.update({
            "answer": state.get("generated_answer"),
            "confidence_score": state.get("confidence_score"),
            "confidence_level": state.get("confidence_level"),
            "sources": sources
        })
    
    elif response_type == "access_denied":
        base_response.update({
            "message": f"Access denied. Your role '{state.get('user_role')}' does not have permission to access the requested information.",
            "available_access_levels": state.get("authorized_access_levels", [])
        })
    
    elif response_type == "escalated":
        escalation_info = state.get("escalation_info", {})
        base_response.update({
            "message": "Your query has been escalated to HR Business Partners for review.",
            "escalation_id": escalation_info.get("id"),
            "escalation_reason": escalation_info.get("reason"),
            "expected_response_time": "24-48 hours",
            "partial_answer": state.get("generated_answer") if state.get("confidence_score", 0) > 0.4 else None
        })
    
    elif response_type == "irrelevant_query":
        base_response.update({
            "message": "I couldn't find relevant information in our HR documents to answer your query. Please try rephrasing your question or contact HR directly."
        })
    
    return base_response
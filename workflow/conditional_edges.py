from typing import Dict, Any

def check_document_relevance(state: Dict[str, Any]) -> str:
    print("🔀 Checking document relevance...")
 
    if state["document_grade"] == "yes":
        print("✅ Documents relevant → generate_answer")
        return "generate_answer"
    
    # Check retry limit
    if state.get("retry_count", 0) >= 1:
        print("❌ Retry limit reached → irrelevant_query")
        return "irrelevant_query"
    
    print("🔄 Not relevant → enhance_query")
    return "enhance_query"


def check_hallucination(state: Dict[str, Any]) -> str:
    """Route based on hallucination check."""
    print("🔀 Checking hallucinations...")
    
    if state["hallucination_check"] == "no":
        print("✅ No hallucinations → check_relevance")
        return "check_relevance"

    if state.get("generation_retry_count", 0) >= 2:
        print("❌ Generation retry limit → check_relevance")
        return "check_relevance"  
    
    print("🔄 Hallucinations detected → regenerate_answer")
    return "regenerate_answer"


def check_answer_relevance(state: Dict[str, Any]) -> str:
    print("🔀 Checking answer relevance...")
    
    if state["relevance_check"] == "yes":
        print("✅ Answer relevant → calculate_confidence")
        return "calculate_confidence"
    
    # Check retry limit
    if state.get("retry_count", 0) >= 1:
        print("❌ Retry limit reached → calculate_confidence")
        return "calculate_confidence"  # Proceed with low confidence
    
    print("🔄 Not relevant → enhance_query")
    return "enhance_query"


def check_escalation_needed(state: Dict[str, Any]) -> str:
    print("🔀 Checking escalation need...")
 
    if state["escalation_needed"]:
        print("🚨 Escalation required → escalate")
        return "escalate"
    
    print("✅ No escalation → final_answer")
    return "final_answer"
from typing import Dict, Any
from datetime import datetime
import uuid
from utils.helpers import check_sensitive_content
    
def escalation_check_node(state: Dict[str, Any]) -> Dict[str, Any]:

    print("⚠️ Checking escalation criteria...")
  
    confidence_score = state["confidence_score"]
    query = state["query"]
    answer = state["generated_answer"]
    user_role = state.get("user_role", "employee")  # Get user role
    
    escalation_needed = False
    escalation_reasons = []
    
    # Check confidence score (applies to all users)
    if confidence_score < 0.6:
        escalation_needed = True
        escalation_reasons.append("Low confidence score")
  
    # Check sensitive content - but only escalate for employee/manager, NOT HR
    if user_role in ["employee", "manager"]:  # Only escalate for non-HR users
        if check_sensitive_content(query) or check_sensitive_content(answer):
            escalation_needed = True
            escalation_reasons.append("Sensitive content detected")
    # HR users can ask about sensitive content without escalation
    
    state["escalation_needed"] = escalation_needed
    
    if escalation_needed:
        state["escalation_info"] = {
            "id": str(uuid.uuid4()),
            "reason": ", ".join(escalation_reasons),
            "timestamp": datetime.now().isoformat()
        }
        print(f"🚨 Escalation needed: {', '.join(escalation_reasons)}")
    else:
        print("✅ No escalation required")
    
    return state


def escalation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle escalation process."""
    print("🚨 Processing escalation...")
    
    # In production, this would:
    # 1. Send notifications to HRBP/Legal
    # 2. Log to audit system
    # 3. Create ticket in HR system
    
    # For now, we just format the escalation response
    state["status"] = "escalated"
    print("✅ Escalation response prepared")
    
    return state
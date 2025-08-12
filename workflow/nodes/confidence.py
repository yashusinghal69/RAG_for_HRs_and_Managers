from typing import Dict, Any
from utils.helpers import calculate_confidence_components

def confidence_score_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("🔢 Calculating confidence score...")
    
    components = calculate_confidence_components(state)

    weights = {
        "retrieval": 0.30,      # 30% - How well documents match query
        "document": 0.20,       # 20% - Are documents relevant to question
        "hallucination": 0.20,  # 20% - Is answer factually accurate
        "relevance": 0.20,      # 20% - Does answer address the question
        "source": 0.10          # 10% - Multiple sources increase confidence
    }
 
    confidence_score = 0.0
    for component, weight in weights.items():
        component_score = components.get(component, 0.0)
        weighted_contribution = component_score * weight
        confidence_score += weighted_contribution
    
    if confidence_score >= 0.8:
        confidence_level = "high"
    elif confidence_score >= 0.6:
        confidence_level = "medium"
    else:
        confidence_level = "low"
    
    print(f"✅ Confidence: {confidence_score:.3f} ({confidence_level})")
    
    state["confidence_score"] = round(confidence_score, 3)
    state["confidence_level"] = confidence_level
    state["confidence_components"] = components
    
    return state



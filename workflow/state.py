from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime

class WorkflowState(TypedDict):
    # Input
    query: str
    user_id: str
    timestamp: datetime
    
    # Authorization
    user_role: str
    authorized_access_levels: List[str]
    
    # Retrieval
    retrieved_chunks: List[Dict[str, Any]]
    
    # Processing
    document_grade: str
    enhanced_query: Optional[str]
    retry_count: int
    generation_retry_count: int
    
    # Generation
    generated_answer: str
    hallucination_check: str
    relevance_check: str
    
    # Confidence & Escalation
    confidence_score: float
    confidence_level: str
    escalation_needed: bool
    escalation_info: Optional[Dict[str, Any]]
    
    # Output
    final_response: Dict[str, Any]
    status: str
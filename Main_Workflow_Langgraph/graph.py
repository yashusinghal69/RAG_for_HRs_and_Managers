from langgraph.graph import StateGraph, END
from state import WorkflowState
from conditional_edges import (
    check_document_relevance,
    check_hallucination, check_answer_relevance, check_escalation_needed
)
from nodes.authorization import user_query_node, authorization_node
from nodes.retrieval_pinecone import document_retriever_node
from nodes.grading import grade_document_node, query_enhancer_node
from nodes.generation import generation_node
from nodes.validation import hallucination_check_node, relevance_check_node
from nodes.confidence import confidence_score_node
from nodes.escalation import escalation_check_node, escalation_node
from utils.helpers import format_final_response
from datetime import datetime
from IPython.display import Image, display


def create_workflow_graph():
  
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("user_query", user_query_node)
    workflow.add_node("authorization", authorization_node)
    workflow.add_node("document_retriever", document_retriever_node)
    workflow.add_node("grade_document", grade_document_node)
    workflow.add_node("query_enhancer", query_enhancer_node)
    workflow.add_node("generation", generation_node)
    workflow.add_node("hallucination_checker", hallucination_check_node)
    workflow.add_node("relevance_checker", relevance_check_node)
    workflow.add_node("confidence_calculator", confidence_score_node)
    workflow.add_node("escalation_check", escalation_check_node)
    workflow.add_node("escalation", escalation_node)
    
    workflow.add_node("irrelevant_query", lambda x: {**x, "status": "irrelevant_query"})
    workflow.add_node("final_answer", lambda x: {**x, "status": "success"})
    
    workflow.set_entry_point("user_query")
    
    workflow.add_edge("user_query", "authorization")
    workflow.add_edge("authorization", "document_retriever")
    workflow.add_edge("document_retriever", "grade_document")
    
    workflow.add_conditional_edges(
        "grade_document",
        check_document_relevance,
        {
            "generate_answer": "generation",
            "enhance_query": "query_enhancer",
            "irrelevant_query": "irrelevant_query"
        }
    )
    
    workflow.add_edge("query_enhancer", "document_retriever")
    
    workflow.add_conditional_edges(
        "hallucination_checker",
        check_hallucination,
        {
            "check_relevance": "relevance_checker",
            "regenerate_answer": "generation"
        }
    )
    
    workflow.add_edge("generation", "hallucination_checker")
    
    workflow.add_conditional_edges(
        "relevance_checker",
        check_answer_relevance,
        {
            "calculate_confidence": "confidence_calculator",
            "enhance_query": "query_enhancer"
        }
    )
    
    workflow.add_edge("confidence_calculator", "escalation_check")
    
    workflow.add_conditional_edges(
        "escalation_check",
        check_escalation_needed,
        {
            "escalate": "escalation",
            "final_answer": "final_answer"
        }
    )
 
    workflow.add_edge("irrelevant_query", END)
    workflow.add_edge("escalation", END)
    workflow.add_edge("final_answer", END)
    
    return workflow.compile()

def run_workflow(query: str, user_id: str):

    app = create_workflow_graph()
   
    # png_data = app.get_graph().draw_mermaid_png()
    # with open('graph_diagram.png', 'wb') as f:
    #     f.write(png_data)
    
    initial_state = {
        "query": query,
        "user_id": user_id,
        "timestamp": datetime.now(),
        "retry_count": 0,
        "generation_retry_count": 0
    }
    
    final_state = app.invoke(initial_state)
    
    # Format final response
    response = format_final_response(final_state, final_state["status"])
    return response
    
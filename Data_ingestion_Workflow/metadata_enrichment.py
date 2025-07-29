from typing import List, Dict, Any

def enrich_document_metadata(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    
    enriched_documents = []
    for doc in documents:
        enriched_metadata = doc["metadata"].copy()
         
        access_level = enriched_metadata["access_level"]
        enriched_metadata["allowed_roles"] = get_allowed_roles(access_level)
         
        enriched_metadata["department"] = get_department_from_document_type(enriched_metadata["document_type"])
        
        enriched_doc = {
            "content": doc["content"],
            "metadata": enriched_metadata
        }
        enriched_documents.append(enriched_doc)
    
    print(f"Enriched metadata for {len(enriched_documents)} documents")
    return enriched_documents


def get_allowed_roles(access_level: str) -> List[str]:
 
    access_permissions = {
        "public": ["employee", "manager", "hr"],   
        "manager": ["manager", "hr"],              
        "hr": ["hr"]                              
    }
    return access_permissions.get(access_level, ["hr"])

def get_department_from_document_type(document_type: str) -> str:
 
    department_mapping = {
        "employee_handbook": "general",
        "manager_guide": "management",
        "hr_legal_manual": "hr_legal"
    }
    return department_mapping.get(document_type, "general")
 
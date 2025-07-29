import os
from pathlib import Path
from typing import List, Dict, Any
import chardet

def extract_pdfs_from_documents_folder(documents_folder: str = "Documents") -> List[Dict[str, Any]]:

    workspace_root = Path(__file__).parent.parent
    documents_path = workspace_root / documents_folder
    
    extracted_documents = []
    access_mapping = {
        "novacorp_employee_handbook.txt": "public",
        "novacorp_managers_guide.txt": "manager",
        "novacorp_hr_legal_manual.txt": "hr"
    }
    for file_path in documents_path.glob("*.txt"):
        print(f"Processing: {file_path.name}")
        
        encoding = 'utf-8'
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding'] or 'utf-8'
        
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        
        access_level = access_mapping.get(file_path.name, "public")
        doc_type = get_document_type(file_path.name)
        

        document_data = {
            "content": content.strip(),
            "metadata": {
                "source": file_path.name,
                "page": 1,
                "access_level": access_level,
                "document_type": doc_type,
                "file_type": "text"
            }
        }
        extracted_documents.append(document_data)
                
    print(f"Successfully extracted {len(extracted_documents)} documents")
    return extracted_documents


def get_document_type(filename: str) -> str:
  
    filename_lower = filename.lower()
    if "employee_handbook" in filename_lower:
        return "employee_handbook"
    elif "manager" in filename_lower:
        return "manager_guide"
    elif "hr" in filename_lower or "legal" in filename_lower:
        return "hr_legal_manual"
    else:
        return "general"

import os
from dotenv import load_dotenv
 
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

 
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "hr-rag-index")

SENSITIVE_KEYWORDS = [
     
    "termination", "firing", "dismissal", "layoff", "downsizing", "redundancy",
    "suspension", "disciplinary", "misconduct", "violation", "breach",
    "insubordination", "tardiness", "absenteeism", "performance issues",
    
    
    "harassment", "discrimination", "bullying", "retaliation", "hostile work environment",
    "sexual harassment", "racial discrimination", "age discrimination", "gender discrimination",
    "disability discrimination", "religious discrimination", "workplace violence",
    "intimidation", "stalking", "unwanted advances", "inappropriate behavior",
    
  
    "legal action", "lawsuit", "litigation", "court", "attorney", "lawyer",
    "complaint", "grievance", "investigation", "whistleblower", "ethics violation",
    "regulatory compliance", "audit", "fine", "penalty", "settlement",
    "worker compensation", "unemployment claim", "wrongful termination",

    # Safety and health concerns
    "wage theft", "unpaid overtime", "salary dispute", "benefits denial",
    "pension issues", "401k problems", "payroll error", "compensation dispute",
    
    # Privacy and confidentiality
    "data breach", "privacy violation", "confidential information", "trade secrets",
    "non-disclosure", "background check", "drug test", "surveillance",

 
]
 

 
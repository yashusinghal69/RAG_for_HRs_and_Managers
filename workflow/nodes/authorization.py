from typing import Dict, Any
from utils.helpers import parse_user_role, get_authorized_access_levels

def user_query_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return state


def authorization_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Authorization node to determine user access levels based on role
    """
    print("Checking user authorization...")
    
    user_id = state["user_id"]
    print(f"Raw user_id received: '{user_id}' (type: {type(user_id)})")
    
    user_role = parse_user_role(user_id)
    print(f"Parsed user_role: '{user_role}'")
    
    authorized_access_levels = get_authorized_access_levels(user_role)
    
    print(f"User: {user_role} | Access: {authorized_access_levels}")
    
    # Update state
    state["user_role"] = user_role
    state["authorized_access_levels"] = authorized_access_levels
    
    return state

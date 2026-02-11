from typing import TypedDict, Literal, Optional, List, Dict, Any

class AgentState(TypedDict):
    """State object passed between agents in LangGraph workflow"""
    
    user_query: str
    conversation_history: Optional[List[Dict[str, str]]]
    
    route_decision: Optional[Dict[str, Any]]
    
    sql_result: Optional[str]
    rag_result: Optional[str]
    
    final_response: Optional[str]
    
    error: Optional[str]

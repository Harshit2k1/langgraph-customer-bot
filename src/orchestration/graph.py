from langgraph.graph import StateGraph, END
from src.orchestration.state import AgentState
from src.agents.router import RouterAgent
from src.agents.sql_agent import SQLAgent
from src.agents.rag_agent import RAGAgent
from openai import OpenAI
from src.config import Config

class MultiAgentOrchestrator:
    """LangGraph-based multi-agent orchestration"""
    
    def __init__(self):
        self.router = RouterAgent()
        self.sql_agent = SQLAgent()
        self.rag_agent = RAGAgent()
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        self.graph = self._build_graph()
    
    def _route_query(self, state: AgentState) -> AgentState:
        """Route the query to appropriate agent"""
        try:
            route_decision = self.router.route(state['user_query'])
            state['route_decision'] = route_decision
            print(f"Routing decision: {route_decision['agent']} (confidence: {route_decision['confidence']})")
        except Exception as e:
            state['error'] = f"Routing error: {str(e)}"
            state['route_decision'] = {'agent': 'RAG_AGENT', 'confidence': 'low'}
        
        return state
    
    def _call_sql_agent(self, state: AgentState) -> AgentState:
        """Execute SQL agent"""
        try:
            result = self.sql_agent.query(
                state['user_query'],
                state.get('conversation_history')
            )
            state['sql_result'] = result
        except Exception as e:
            state['sql_result'] = f"SQL agent error: {str(e)}"
        
        return state
    
    def _call_rag_agent(self, state: AgentState) -> AgentState:
        """Execute RAG agent"""
        try:
            result = self.rag_agent.query(
                state['user_query'],
                state.get('conversation_history')
            )
            state['rag_result'] = result
        except Exception as e:
            state['rag_result'] = f"RAG agent error: {str(e)}"
        
        return state
    
    def _call_both_agents(self, state: AgentState) -> AgentState:
        """Execute both SQL and RAG agents"""
        try:
            sql_result = self.sql_agent.query(
                state['user_query'],
                state.get('conversation_history')
            )
            state['sql_result'] = sql_result
            
            rag_result = self.rag_agent.query(
                state['user_query'],
                state.get('conversation_history')
            )
            state['rag_result'] = rag_result
            
        except Exception as e:
            state['error'] = f"Error calling both agents: {str(e)}"
        
        return state
    
    def _synthesize_response(self, state: AgentState) -> AgentState:
        """Combine results from agents"""
        
        if state.get('error'):
            state['final_response'] = f"Error: {state['error']}"
            return state
        
        route_decision = state.get('route_decision', {})
        agent_type = route_decision.get('agent', 'RAG_AGENT')
        
        if agent_type == 'SQL_AGENT':
            state['final_response'] = state.get('sql_result', 'No response from SQL agent')
        
        elif agent_type == 'RAG_AGENT':
            state['final_response'] = state.get('rag_result', 'No response from RAG agent')
        
        elif agent_type == 'BOTH':
            sql_result = state.get('sql_result', '')
            rag_result = state.get('rag_result', '')
            
            synthesis_prompt = f"""Combine these two responses into a single, coherent answer:

SQL Agent Response (Customer Data):
{sql_result}

RAG Agent Response (Policy Information):
{rag_result}

Provide a unified response that addresses the user's question completely."""

            try:
                response = self.client.chat.completions.create(
                    model=Config.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that combines information from multiple sources."},
                        {"role": "user", "content": synthesis_prompt}
                    ]
                )
                state['final_response'] = response.choices[0].message.content
            except Exception as e:
                state['final_response'] = f"{sql_result}\n\n{rag_result}"
        
        return state
    
    def _decide_next_step(self, state: AgentState) -> str:
        """Decide which agent to call based on routing decision"""
        agent = state.get('route_decision', {}).get('agent', 'RAG_AGENT')
        
        if agent == 'SQL_AGENT':
            return 'sql_agent'
        elif agent == 'RAG_AGENT':
            return 'rag_agent'
        elif agent == 'BOTH':
            return 'both_agents'
        else:
            return 'rag_agent'
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        workflow = StateGraph(AgentState)
        
        workflow.add_node("router", self._route_query)
        workflow.add_node("sql_agent", self._call_sql_agent)
        workflow.add_node("rag_agent", self._call_rag_agent)
        workflow.add_node("both_agents", self._call_both_agents)
        workflow.add_node("synthesize", self._synthesize_response)
        
        workflow.set_entry_point("router")
        
        workflow.add_conditional_edges(
            "router",
            self._decide_next_step,
            {
                "sql_agent": "sql_agent",
                "rag_agent": "rag_agent",
                "both_agents": "both_agents"
            }
        )
        
        workflow.add_edge("sql_agent", "synthesize")
        workflow.add_edge("rag_agent", "synthesize")
        workflow.add_edge("both_agents", "synthesize")
        
        workflow.add_edge("synthesize", END)
        
        return workflow.compile()
    
    def query(self, user_query: str, conversation_history=None) -> str:
        """Execute the multi-agent workflow"""
        
        initial_state = AgentState(
            user_query=user_query,
            conversation_history=conversation_history,
            route_decision=None,
            sql_result=None,
            rag_result=None,
            final_response=None,
            error=None
        )
        
        try:
            result = self.graph.invoke(initial_state)
            return result.get('final_response', 'No response generated')
        except Exception as e:
            return f"Orchestration error: {str(e)}"

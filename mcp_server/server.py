import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.sql_agent import SQLAgent
from src.agents.rag_agent import RAGAgent
from src.orchestration.graph import MultiAgentOrchestrator
from src.config import Config

app = Server("customer-support-mcp")

orchestrator = None
sql_agent = None
rag_agent = None

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for the MCP client"""
    return [
        Tool(
            name="query_customer_data",
            description="Query customer database using natural language. Returns customer profiles, support tickets, account information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query about customers or support tickets"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="query_policy_documents",
            description="Search company policy documents (refund, privacy, terms, support). Returns information from uploaded PDFs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Question about company policies or procedures"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="query_multi_agent",
            description="Intelligent routing to SQL or RAG agent based on query intent. Handles complex queries requiring both database and document data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Any customer support related query"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_system_stats",
            description="Get current system statistics including customer count, ticket count, and document count.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls from MCP client"""
    
    global orchestrator, sql_agent, rag_agent
    
    if orchestrator is None:
        try:
            Config.validate()
            orchestrator = MultiAgentOrchestrator()
            sql_agent = orchestrator.sql_agent
            rag_agent = orchestrator.rag_agent
        except Exception as e:
            return [TextContent(type="text", text=f"Error initializing system: {str(e)}")]
    
    try:
        if name == "query_customer_data":
            query = arguments.get("query", "")
            result = sql_agent.query(query)
            return [TextContent(type="text", text=result)]
        
        elif name == "query_policy_documents":
            query = arguments.get("query", "")
            result = rag_agent.query(query)
            return [TextContent(type="text", text=result)]
        
        elif name == "query_multi_agent":
            query = arguments.get("query", "")
            result = orchestrator.query(query)
            return [TextContent(type="text", text=result)]
        
        elif name == "get_system_stats":
            sql_stats = sql_agent.get_database_stats()
            vector_stats = rag_agent.vector_store.get_collection_stats()
            
            stats_text = f"""System Statistics:
- Customers: {sql_stats.get('customers', 'N/A')}
- Support Tickets: {sql_stats.get('tickets', 'N/A')}
- Policy Documents: {vector_stats.get('total_documents', 'N/A')}
- Database Status: {sql_stats.get('status', 'unknown')}
"""
            return [TextContent(type="text", text=stats_text)]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error executing tool: {str(e)}")]

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())

from openai import OpenAI
from src.config import Config
from src.database.sql_db import SQLDatabase
import json

class SQLAgent:
    """SQL agent using OpenAI function calling for natural language to SQL"""
    
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set")
        
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.db = SQLDatabase()
        self.schema = self.db.get_schema_info()
    
    def get_tools_definition(self):
        """Define SQL query function for OpenAI function calling"""
        schema_description = json.dumps(self.schema, indent=2)
        
        return [
            {
                "type": "function",
                "function": {
                    "name": "execute_sql_query",
                    "description": f"""Execute a SQL SELECT query on the customer support database. 
                    
Database Schema:
{schema_description}

Use JOINs to combine data from both tables when needed. Always use proper WHERE clauses for filtering.""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "A valid SQLite SELECT query. Only SELECT statements are allowed."
                            },
                            "reasoning": {
                                "type": "string",
                                "description": "Brief explanation of what this query will retrieve"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    def _strip_tool_json_prefix(self, text: str) -> str:
        """Remove tool JSON blobs and tool chatter from model output."""
        if not text:
            return text

        cleaned = text.lstrip()
        decoder = json.JSONDecoder()
        tool_keys = {"query", "reasoning", "success", "row_count", "results", "error"}

        while cleaned:
            try:
                parsed, index = decoder.raw_decode(cleaned)
            except json.JSONDecodeError:
                break

            if isinstance(parsed, dict) and tool_keys.intersection(parsed.keys()):
                cleaned = cleaned[index:].lstrip()
                continue

            break

        filtered_lines = []
        for line in cleaned.splitlines():
            stripped = line.strip()
            if not stripped:
                filtered_lines.append(line)
                continue
            if "executing sql query" in stripped.lower():
                continue
            if stripped.startswith("{") and stripped.endswith("}"):
                try:
                    parsed = json.loads(stripped)
                    if isinstance(parsed, dict) and tool_keys.intersection(parsed.keys()):
                        continue
                except json.JSONDecodeError:
                    pass
            if any(key in stripped for key in ('"query"', '"results"', '"row_count"', '"success"')):
                continue
            filtered_lines.append(line)

        return "\n".join(filtered_lines).strip()
    
    def execute_sql_query(self, query, reasoning=None):
        """Execute SQL query with validation"""
        is_valid, message = self.db.validate_query(query)
        
        if not is_valid:
            return {"error": message, "query": query}
        
        result = self.db.execute_query(query)
        
        if isinstance(result, dict) and "error" in result:
            return result
        
        return {
            "success": True,
            "query": query,
            "reasoning": reasoning,
            "row_count": len(result) if isinstance(result, list) else 0,
            "results": result
        }
    
    def query(self, user_question, conversation_history=None):
        """Process natural language query using function calling"""
        
        system_prompt = f"""You are a SQL expert assistant for a customer support system. 
Generate and execute SQL queries to answer questions about customer data and support tickets.

Database Schema:
{json.dumps(self.schema, indent=2)}

When answering:
1. Use the execute_sql_query function to get data
2. Format results in a clear, user-friendly way
3. If multiple rows are returned, summarize key information
4. Include relevant details like customer names, ticket IDs, dates
5. If no results found, explain that clearly

Always use proper JOINs when information spans multiple tables."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if conversation_history:
            messages.extend(conversation_history[-Config.MEMORY_WINDOW:])
        
        messages.append({"role": "user", "content": user_question})
        
        try:
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=messages,
                tools=self.get_tools_definition(),
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            
            if not response_message.tool_calls:
                return response_message.content
            
            messages.append(response_message)
            
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                
                if function_name == "execute_sql_query":
                    function_args = json.loads(tool_call.function.arguments)
                    sql_query = function_args.get("query")
                    reasoning = function_args.get("reasoning")
                    
                    function_response = self.execute_sql_query(sql_query, reasoning)
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": json.dumps(function_response)
                    })

            messages.append({
                "role": "system",
                "content": (
                    "Provide a user-facing answer only. "
                    "Do not include raw JSON, SQL, tool call arguments, or tool outputs."
                )
            })
            
            final_response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=messages
            )
            
            content = final_response.choices[0].message.content
            return self._strip_tool_json_prefix(content)
            
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    def get_database_stats(self):
        """Get current database statistics"""
        return self.db.test_connection()

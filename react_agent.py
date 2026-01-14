If you mention a tool or say you can use a tool, you MUST immediately use it by emitting an Action and Action Input.
Never describe tool usage without performing it.
"""
ReAct Agent Implementation
A from-scratch implementation of a Reasoning and Acting agent without using any agentic libraries.
Uses OpenRouter API for LLM reasoning and includes 4 tools with HTTP capabilities.
"""

import os
import json
import requests
from datetime import datetime
from typing import List, Dict, Any, Callable
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Tool:
    """Base class for agent tools"""
    def __init__(self, name: str, description: str, function: Callable):
        self.name = name
        self.description = description
        self.function = function
    
    def execute(self, **kwargs) -> str:
        """Execute the tool function"""
        try:
            result = self.function(**kwargs)
            return str(result)
        except Exception as e:
            return f"Error executing {self.name}: {str(e)}"

class ReActAgent:
    """
    ReAct (Reasoning and Acting) Agent
    Implements the ReAct pattern: Thought -> Action -> Observation loop
    """
    
    def __init__(self, api_key: str, model: str = "openai/gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.tools = {}
        self.conversation_history = []
        self.max_iterations = 10
        
        # Initialize tools
        self._setup_tools()
        
    def _setup_tools(self):
        """Setup all available tools for the agent"""
        
        # Tool 1: Calculator (local computation)
        def calculator(expression: str) -> str:
            """Evaluate a mathematical expression"""
            try:
                # Safe evaluation of basic math expressions using restricted eval
                # Only allow basic arithmetic operations
                allowed_names = {}
                allowed_builtins = {}
                result = eval(expression, {"__builtins__": allowed_builtins}, allowed_names)
                return f"The result of {expression} is {result}"
            except (SyntaxError, NameError, TypeError) as e:
                return f"Error calculating {expression}: {str(e)}"
        
        # Tool 2: Current time/date (local utility)
        def get_current_time(timezone: str = "UTC") -> str:
            """Get current date and time"""
            now = datetime.now()
            return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')} {timezone}"
        
        # Tool 3: Weather API (HTTP JSON service - National Weather Service)
        def get_weather(latitude: float, longitude: float) -> str:
            """
            Get weather forecast from National Weather Service API
            Example: latitude=38.8894, longitude=-77.0352 (Washington DC)
            """
            try:
                # First, get the grid point
                points_url = f"https://api.weather.gov/points/{latitude},{longitude}"
                headers = {"User-Agent": "ReActAgent/1.0"}
                response = requests.get(points_url, headers=headers, timeout=10)
                
                if response.status_code != 200:
                    return f"Weather API error: Status {response.status_code}"
                
                data = response.json()
                forecast_url = data['properties']['forecast']
                
                # Get the forecast
                forecast_response = requests.get(forecast_url, headers=headers, timeout=10)
                if forecast_response.status_code != 200:
                    return f"Forecast API error: Status {forecast_response.status_code}"
                
                forecast_data = forecast_response.json()
                periods = forecast_data['properties']['periods'][:3]  # Get first 3 periods
                
                result = f"Weather forecast for coordinates ({latitude}, {longitude}):\n"
                for period in periods:
                    result += f"- {period['name']}: {period['temperature']}°{period['temperatureUnit']} - {period['shortForecast']}\n"
                
                return result
            except Exception as e:
                return f"Error fetching weather: {str(e)}"
        
        # Tool 4: arXiv API (HTTP service for research papers)
        def search_arxiv(query: str, max_results: int = 3) -> str:
            """
            Search for research papers on arXiv
            Returns titles, authors, and summaries
            """
            try:
                base_url = "http://export.arxiv.org/api/query"
                params = {
                    "search_query": f"all:{query}",
                    "start": 0,
                    "max_results": max_results
                }
                
                response = requests.get(base_url, params=params, timeout=10)
                if response.status_code != 200:
                    return f"arXiv API error: Status {response.status_code}"
                
                # Parse XML response (arXiv returns XML, not JSON, but it's still structured data)
                content = response.text
                
                # Simple parsing for demonstration
                entries = content.split("<entry>")[1:]  # Skip first split
                
                if not entries:
                    return f"No papers found for query: {query}"
                
                result = f"Found {len(entries)} papers for '{query}':\n\n"
                for i, entry in enumerate(entries[:max_results], 1):
                    # Extract title
                    title_start = entry.find("<title>") + 7
                    title_end = entry.find("</title>")
                    title = entry[title_start:title_end].strip()
                    
                    # Extract authors
                    author_entries = entry.split("<name>")[1:]
                    authors = []
                    for author_entry in author_entries[:3]:  # First 3 authors
                        author_end = author_entry.find("</name>")
                        authors.append(author_entry[:author_end].strip())
                    
                    # Extract summary (first 200 chars)
                    summary_start = entry.find("<summary>") + 9
                    summary_end = entry.find("</summary>")
                    summary = entry[summary_start:summary_end].strip()[:200] + "..."
                    
                    result += f"{i}. {title}\n"
                    result += f"   Authors: {', '.join(authors)}\n"
                    result += f"   Summary: {summary}\n\n"
                
                return result
            except Exception as e:
                return f"Error searching arXiv: {str(e)}"
        
        # Register tools
        self.tools["calculator"] = Tool(
            "calculator",
            "Evaluates mathematical expressions. Input: expression (string). Example: calculator(expression='2 + 2 * 5')",
            calculator
        )
        
        self.tools["get_current_time"] = Tool(
            "get_current_time",
            "Returns current date and time. Input: timezone (optional, defaults to UTC). Example: get_current_time(timezone='UTC')",
            get_current_time
        )
        
        self.tools["get_weather"] = Tool(
            "get_weather",
            "Gets weather forecast from National Weather Service for US locations. Input: latitude (float), longitude (float). Example: get_weather(latitude=38.8894, longitude=-77.0352)",
            get_weather
        )
        
        self.tools["search_arxiv"] = Tool(
            "search_arxiv",
            "Searches for research papers on arXiv. Input: query (string), max_results (optional, default 3). Example: search_arxiv(query='machine learning', max_results=3)",
            search_arxiv
        )
    
    def _get_tool_descriptions(self) -> str:
        """Generate a formatted string of all available tools"""
        descriptions = []
        for tool_name, tool in self.tools.items():
            descriptions.append(f"- {tool_name}: {tool.description}")
        return "\n".join(descriptions)
    
    def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        """Call OpenRouter API to get LLM response"""
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return f"Error: API returned status {response.status_code}: {response.text}"
            
            response_data = response.json()
            return response_data["choices"][0]["message"]["content"]
            
        except Exception as e:
            return f"Error calling LLM: {str(e)}"

    def run(self, user_query: str) -> str:
        system_prompt = f"""You are a helpful ReAct agent.

Available tools:
{self._get_tool_descriptions()}

If you mention a tool or say you can use a tool, you MUST immediately use it by emitting an Action and Action Input.
Never describe tool usage without performing it.

To use a tool, respond with:
Thought: [your reasoning about what to do next]
Action: [tool_name]
Action Input: {{"param_name": "param_value"}}

When you have enough information to answer the question, respond with:
Thought: [your reasoning]
Final Answer: [your complete answer to the user's question]

Always think step by step and use tools when you need information."""
        
        messages = []
        messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_query})

        steps = 0
        while steps < self.max_iterations:
            response_text = self._call_llm(messages)
            messages.append({"role": "assistant", "content": response_text})

            if "Final Answer:" in response_text:
                return response_text.split("Final Answer:", 1)[1].strip()

            tool_name, tool_input = self._parse_action(response_text)
            # If no tool was chosen, assume the model answered directly
            if not tool_name:
                return response_text
            if tool_input is None:
                tool_input = {}

            tool = self.tools.get(tool_name)
            if not tool:
                messages.append({"role": "user", "content": f"Observation: Tool '{tool_name}' not found."})
                steps += 1
                continue

            observation = tool.execute(**tool_input)
            messages.append({"role": "user", "content": f"Observation: {observation}"})

            steps += 1

        return "I couldn't complete the task within the iteration limit."

    
    def _parse_action(self, llm_response: str) -> tuple:
        """
        Parse the LLM response to extract action and parameters
        Expected format includes lines like:
        Action: tool_name
        Action Input: {"param": "value"}
        """
        lines = llm_response.strip().split("\n")
        action = None
        action_input = None
        
        for i, line in enumerate(lines):
            if line.startswith("Action:"):
                action = line.replace("Action:", "").strip()
            elif line.startswith("Action Input:"):
                input_str = line.replace("Action Input:", "").strip()
                try:
                    action_input = json.loads(input_str)
                except json.JSONDecodeError:
                    # If not valid JSON, treat as string
                    action_input = {"input": input_str}
        
        return action, action_input
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Return the conversation history for debugging"""
        return self.conversation_history

def main():
    """CLI interface for the ReAct agent"""
    print("=" * 60)
    print("ReAct Agent - Interactive CLI")
    print("=" * 60)
    print()
    
    # Check for API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY not found in environment variables.")
        print("Please create a .env file with your OpenRouter API key.")
        print("Example: OPENROUTER_API_KEY=your_api_key_here")
        return
    
    # Initialize agent
    print("Initializing ReAct Agent...")
    agent = ReActAgent(api_key)
    print("Agent ready!")
    print()
    print("Available tools:")
    print("- calculator: Evaluate mathematical expressions")
    print("- get_current_time: Get current date and time")
    print("- get_weather: Get weather forecast (US locations)")
    print("- search_arxiv: Search for research papers")
    print()
    print("Type 'quit' or 'exit' to end the session.")
    print("Type 'history' to see the conversation history.")
    print()
    
    # Main interaction loop
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
            
            if user_input.lower() == 'history':
                print("\nConversation History:")
                print(json.dumps(agent.get_conversation_history(), indent=2))
                print()
                continue
            
            print("\nAgent is thinking...")
            response = agent.run(user_input)
            print(f"\nAgent: {response}")
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print()


if __name__ == "__main__":
    main()

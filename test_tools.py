"""
Test script for ReAct Agent tools
Tests each tool independently to verify functionality
"""

import os
os.environ["OPENROUTER_API_KEY"] = "test_key"  # Set dummy key for testing

from react_agent import ReActAgent

def test_tools():
    """Test all tools independently"""
    print("Testing ReAct Agent Tools")
    print("=" * 60)
    
    # Create agent (won't call LLM in these tests)
    agent = ReActAgent("dummy_key")
    
    # Test 1: Calculator
    print("\n1. Testing Calculator Tool:")
    calc_tool = agent.tools["calculator"]
    result = calc_tool.execute(expression="2 + 2")
    print(f"   2 + 2 = {result}")
    
    result = calc_tool.execute(expression="10 * 5 + 3")
    print(f"   10 * 5 + 3 = {result}")
    
    # Test 2: Current Time
    print("\n2. Testing Current Time Tool:")
    time_tool = agent.tools["get_current_time"]
    result = time_tool.execute()
    print(f"   Current time: {result}")
    
    # Test 3: Weather API (may fail without internet or for non-US coords)
    print("\n3. Testing Weather API Tool:")
    weather_tool = agent.tools["get_weather"]
    print("   Testing with Washington DC coordinates (38.8894, -77.0352)...")
    result = weather_tool.execute(latitude=38.8894, longitude=-77.0352)
    print(f"   Result: {result[:200]}...")  # Print first 200 chars
    
    # Test 4: arXiv Search
    print("\n4. Testing arXiv Search Tool:")
    arxiv_tool = agent.tools["search_arxiv"]
    print("   Searching for 'quantum computing'...")
    result = arxiv_tool.execute(query="quantum computing", max_results=2)
    print(f"   Result: {result[:300]}...")  # Print first 300 chars
    
    print("\n" + "=" * 60)
    print("Tool testing complete!")
    print("\nAll tools are registered:")
    for tool_name in agent.tools.keys():
        print(f"  ✓ {tool_name}")

if __name__ == "__main__":
    test_tools()

# ReAct Agent - Second Computer Science Assignment

A from-scratch implementation of a **ReAct (Reasoning and Acting) Agent** without using any agentic libraries. This agent uses the ReAct pattern to combine reasoning and acting in an iterative loop to accomplish tasks.

## 🎯 What is a ReAct Agent?

ReAct is an agent paradigm that interleaves **Reasoning** (thinking through problems) with **Acting** (using tools to gather information). The agent follows this pattern:

1. **Thought**: Reason about what to do next
2. **Action**: Use a tool to gather information
3. **Observation**: Observe the result of the action
4. Repeat until the task is complete

This allows the agent to dynamically adapt its strategy based on the information it gathers, making it more capable than simple single-step prediction models.

## 📋 Features

- **Pure Python Implementation**: No agentic frameworks (LangChain, AutoGPT, etc.)
- **OpenRouter Integration**: Uses OpenRouter API for LLM reasoning
- **4 Diverse Tools**:
  - **Calculator**: Local computation for mathematical expressions
  - **Current Time**: Local utility to get date and time
  - **Weather API**: HTTP JSON service using National Weather Service
  - **arXiv Search**: HTTP service to search research papers
- **Interactive CLI**: User-friendly command-line interface
- **Full ReAct Loop**: Implements complete reasoning and acting cycle

## 🛠️ Tools Explained

### 1. Calculator (Local Computation)
Evaluates mathematical expressions using Python's eval in a safe, restricted environment.

**Example**: "What is 25 * 4 + 100?"

### 2. Current Time (Local Utility)
Returns the current date and time from the system.

**Example**: "What time is it?"

### 3. Weather API (HTTP JSON Service)
Uses the National Weather Service API to fetch weather forecasts for US locations using latitude/longitude coordinates. Returns structured JSON data with temperature and conditions.

**Example**: "What's the weather like in Washington DC?" (coordinates: 38.8894, -77.0352)

### 4. arXiv API (HTTP Service)
Searches for academic research papers on arXiv.org and returns titles, authors, and summaries.

**Example**: "Find recent papers about machine learning"

## 🚀 Setup Instructions

### Prerequisites
- Python 3.7 or higher
- OpenRouter API key (get one at https://openrouter.ai/)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/Chris5934/Second-Assignment-Comp-Sci.git
cd Second-Assignment-Comp-Sci
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` and add your OpenRouter API key:
```
OPENROUTER_API_KEY=your_actual_api_key_here
```

## 💻 Usage

### Running the Interactive CLI

```bash
python react_agent.py
```

### Example Interactions

**Example 1: Mathematical Calculation**
```
You: What is 15 * 23 + 100?
Agent: The result is 445.
```

**Example 2: Weather Query**
```
You: What's the weather forecast for Washington DC?
Agent: The weather in Washington DC (38.8894, -77.0352) shows:
- Tonight: 45°F - Partly Cloudy
- Tomorrow: 62°F - Sunny
- Tomorrow Night: 48°F - Clear
```

**Example 3: Research Papers**
```
You: Find papers about neural networks
Agent: I found 3 papers about neural networks:
1. "Deep Neural Networks for Image Recognition"
   Authors: Smith, J., Johnson, A.
   Summary: This paper presents a novel approach...
...
```

**Example 4: Multi-tool Query**
```
You: What time is it and what's 50 divided by 2?
Agent: It's currently 2026-01-12 21:30:45 UTC, and 50 divided by 2 equals 25.
```

## 🔧 How It Works

### The ReAct Loop

```python
# Simplified pseudocode
messages = [system_prompt, user_query]

for iteration in range(max_iterations):
    # 1. REASONING: LLM thinks about what to do
    llm_response = call_llm(messages)
    
    # 2. Check if task is complete
    if "Final Answer:" in llm_response:
        return final_answer
    
    # 3. ACTING: Parse and execute action
    action, params = parse_action(llm_response)
    observation = execute_tool(action, params)
    
    # 4. Add observation to context
    messages.append(observation)
    # Loop continues with new information
```

### Architecture

```
User Query
    ↓
[LLM Reasoning] → Thought: "I need to use calculator"
    ↓
[Action Selection] → Action: calculator
    ↓
[Tool Execution] → Result: 42
    ↓
[Observation] → "The result is 42"
    ↓
[LLM Reasoning] → Thought: "I have the answer"
    ↓
Final Answer: "The answer is 42"
```

## 📝 Code Structure

- **`react_agent.py`**: Main implementation
  - `Tool` class: Base class for tools
  - `ReActAgent` class: Core agent logic
  - `main()`: CLI interface
- **`requirements.txt`**: Python dependencies
- **`.env.example`**: Environment variable template
- **`.gitignore`**: Git ignore rules

## 🎓 Learning Points

This implementation demonstrates:

1. **Tool-based AI Architecture**: How to give LLMs access to external capabilities
2. **ReAct Pattern**: The reasoning-acting loop for autonomous agents
3. **API Integration**: Working with both local tools and HTTP services
4. **Prompt Engineering**: Structuring prompts to guide LLM behavior
5. **Error Handling**: Graceful failure management in agent systems

## 🔒 Security Notes

- API keys are stored in `.env` and never committed to git
- Calculator uses restricted eval to prevent code injection
- HTTP requests have timeouts to prevent hanging
- Tool execution is wrapped in try-except for error handling

## 🚧 Limitations

- Maximum 10 iterations per query (prevents infinite loops)
- Weather API only works for US locations
- Calculator is restricted to basic math expressions
- Requires internet connection for HTTP-based tools

## 📚 References

- **ReAct Paper**: [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- **Lecture Slides**: [What are Agents?](https://blog.yetanotheruseless.com/static/what-are-agents.html)
- **OpenRouter API**: https://openrouter.ai/
- **National Weather Service API**: https://www.weather.gov/documentation/services-web-api
- **arXiv API**: https://arxiv.org/help/api/

## 👤 Author

Christine Gandiya (Chris5934)

## 📄 License

This is an educational project for Computer Science coursework.
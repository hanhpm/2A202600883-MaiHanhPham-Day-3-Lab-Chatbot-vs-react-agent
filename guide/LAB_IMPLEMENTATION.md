# Lunch Ordering System: Chatbot vs ReAct Agent

## Overview

Hệ thống so sánh giữa **Baseline Chatbot** (không dùng tools) và **ReAct Agent** (dùng tools).

**Baseline Chatbot**: Trả lời trực tiếp từ LLM, không gọi tools, nhanh nhưng hạn chế.
**ReAct Agent**: Sử dụng Thought-Action-Observation loop để gọi tools, chậm hơn nhưng mạnh hơn.

---

## Project Structure

```
.
├── src/
│   ├── agent/
│   │   └── agent.py           # ReAct agent loop (Thought-Action-Observation)
│   ├── chatbot/
│   │   └── chatbot.py          # Baseline chatbot (no tools)
│   ├── core/
│   │   ├── llm_provider.py     # Base LLM provider interface
│   │   ├── openai_provider.py  # OpenAI provider (template)
│   │   ├── gemini_provider.py  # Gemini provider (template)
│   │   └── mock_provider.py    # Mock provider for offline testing
│   ├── tools/
│   │   ├── menu_tool.py        # Search menu items
│   │   ├── order_tool.py       # Add/update orders
│   │   ├── bill_tool.py        # Calculate bills & split costs
│   │   └── user_tool.py        # Manage team members
│   └── telemetry/
│       ├── logger.py           # JSONL logger for events
│       └── metrics.py          # Metrics tracker (tokens, latency, cost)
├── tests/
│   ├── test_tools.py           # Tests for all tools (20 tests)
│   ├── test_chatbot.py         # Tests for chatbot (8 tests)
│   └── test_agent.py           # Tests for agent (12 tests)
├── data/
│   ├── menu.json               # Mock menu data
│   └── members.json            # Mock team members
├── logs/
│   └── agent_telemetry_*.jsonl # JSONL telemetry logs
├── demo.py                     # Demo script (run both chatbot & agent)
├── pytest.ini                  # Pytest config
├── requirements.txt            # Main requirements
├── requirements-dev.txt        # Dev requirements (pytest)
├── metrics_summary.json        # Exported metrics
└── README.md                   # This file
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements-dev.txt
```

### 2. Run demo (chatbot + agent)

```bash
python demo.py
```

Output:
- Chatbot responses
- Agent responses with metrics
- Telemetry logs
- Metrics summary JSON

### 3. Run tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_tools.py -v
python -m pytest tests/test_chatbot.py -v
python -m pytest tests/test_agent.py -v
```

---

## Component Details

### Mock LLM Provider (`src/core/mock_provider.py`)

**Purpose**: Simulate LLM responses without API keys (offline testing).

**Usage**:
```python
from src.core.mock_provider import MockLLMProvider

llm = MockLLMProvider(model_name="mock-model")
response, usage = llm.generate(prompt, system_prompt="...")
```

**Returns**:
- `response`: String with Thought-Action-Observation format
- `usage`: Dict with token counts

### Tools

#### MenuTool (`search_menu`)
```python
menu_tool.search_menu(max_price=50000, spicy=False, category="rice")
# Returns: {"items": [...], "count": int}
```

#### OrderTool (`add_order`, `update_order`, `mark_paid`, etc.)
```python
order_tool.add_order("Minh", "M01", note="ít cơm")
# Returns: {"status": "success", "message": "...", "data": {...}}
```

#### BillTool (`summarize_orders`, `split_bill`)
```python
bill_tool.summarize_orders()  # Lists all orders with prices
bill_tool.split_bill()        # Calculates cost per person
```

#### UserTool (`check_missing_orders`, `check_unpaid`)
```python
user_tool.check_missing_orders(orders)  # Who hasn't ordered
user_tool.check_unpaid(orders)          # Who hasn't paid
```

### Baseline Chatbot (`src/chatbot/chatbot.py`)

**No tool calling**, just LLM responses.

```python
from src.core.mock_provider import MockLLMProvider
from src.chatbot.chatbot import BaselineChatbot

llm = MockLLMProvider()
chatbot = BaselineChatbot(llm)
response = chatbot.chat("Gợi ý món dưới 50k")
```

### ReAct Agent (`src/agent/agent.py`)

**Thought → Action → Observation → Final Answer**

```python
from src.core.mock_provider import MockLLMProvider
from src.agent.agent import ReActAgent

llm = MockLLMProvider()
tools = {
    "search_menu": menu_tool.search_menu,
    "add_order": order_tool.add_order,
    # ... more tools
}
agent = ReActAgent(llm, tools, max_steps=5)
response, metrics = agent.run("Gợi ý món dưới 50k không cay")
print(response)
print(metrics)  # {"steps": 1, "status": "success", ...}
```

### Telemetry

#### JSONL Logger
```python
from src.telemetry.logger import logger

logger.log_event("EVENT_TYPE", {"key": "value"})
logs = logger.read_logs()  # Returns all logged events
```

#### Metrics Tracker
```python
from src.telemetry.metrics import tracker

tracker.track_request("mock", "model-name", usage, latency_ms)
summary = tracker.get_summary()
tracker.export_metrics_summary("metrics.json")
```

---

## Test Coverage

### Tools Tests (20 tests)
- ✅ MenuTool: load, search by price/spicy/category
- ✅ OrderTool: add, update, list, mark paid
- ✅ BillTool: summarize, split bill, payment status
- ✅ UserTool: check missing, check unpaid

### Chatbot Tests (8 tests)
- ✅ Initialization, greeting, menu questions
- ✅ Conversation history tracking
- ✅ No tool calling

### Agent Tests (12 tests)
- ✅ Initialization, system prompt
- ✅ Search menu, add order, multiple steps
- ✅ Action parsing, error handling
- ✅ Tool execution, max steps
- ✅ Agent vs Chatbot comparison

**Total: 40 tests, All passing ✅**

---

## Example: Full Flow

```python
# Setup
from src.core.mock_provider import MockLLMProvider
from src.agent.agent import ReActAgent
from src.tools.menu_tool import MenuTool
from src.tools.order_tool import OrderTool
# ... import other tools

# Initialize
llm = MockLLMProvider()
menu_tool = MenuTool("data/menu.json")
order_tool = OrderTool()
# ... setup other tools

tools = {
    "search_menu": menu_tool.search_menu,
    "add_order": order_tool.add_order,
    # ... other tools
}

agent = ReActAgent(llm, tools)

# Run
response, metrics = agent.run("Gợi ý món dưới 50k không cay")

# Output
# Response: "Bạn có thể chọn cơm gà 45k hoặc bún thịt nướng 50k..."
# Metrics: {
#     "steps": 1,
#     "status": "success",
#     "total_tokens": 290,
#     "errors": []
# }
```

---

## Logging & Metrics

### JSONL Log Format

```json
{
  "timestamp": "2026-06-01T15:19:52.889688",
  "event_type": "AGENT_START",
  "data": {
    "input": "Gợi ý món dưới 50k không cay",
    "model": "mock-agent"
  }
}
```

### Event Types

- `AGENT_START`: Agent started
- `AGENT_STEP`: Agent took a step
- `AGENT_END`: Agent finished
- `AGENT_ERROR`: Error occurred
- `LLM_METRIC`: LLM usage tracked
- `METRICS_EXPORTED`: Metrics saved

### Metrics Summary

```json
{
  "total_requests": 3,
  "total_tokens": 869,
  "total_cost_estimate": 0.0087,
  "avg_latency_ms": 100.0,
  "max_latency_ms": 100,
  "min_latency_ms": 100
}
```

---

## Chatbot vs Agent Comparison

| Aspect | Chatbot | Agent |
|--------|---------|-------|
| **Tool Calling** | ❌ None | ✅ Yes (search_menu, add_order, etc.) |
| **Reasoning** | ❌ Direct | ✅ Thought-Action-Observation |
| **Data Accuracy** | ❌ May hallucinate | ✅ Uses real tools |
| **Multi-step** | ❌ Limited | ✅ Full loop support |
| **Speed** | ✅ Fast | ❌ Slower (multiple steps) |
| **Cost** | ✅ Cheaper | ❌ More expensive |
| **Reliability** | ❌ Lower | ✅ Higher |

---

## Use Cases

### When to use Chatbot
- Simple Q&A about menu
- General guidance (not tool-dependent)
- Cost is critical
- Speed is critical

### When to use Agent
- Complex multi-step tasks
- Need real data (actual menu, bills)
- Need to track orders
- Need to handle edge cases (missing users, unpaid bills)

---

## Future Enhancements

1. **Connect to real LLM** (OpenAI, Gemini, Anthropic)
2. **Connect to real database** (menu, orders, users)
3. **Add more tools** (payment integration, notifications)
4. **Add supervision** (review actions before execution)
5. **Fine-tune prompt** based on logged failures
6. **Add observability** (traces, spans for debugging)

---

## Troubleshooting

### Tests fail
```bash
# Check if pytest is installed
pip install pytest

# Run with verbose output
python -m pytest tests/ -vv
```

### Mock responses look generic
Edit `src/core/mock_provider.py` to customize responses for specific prompts.

### No logs generated
Check `logs/` directory for `.jsonl` files created during demo.

---

## Author & Lab

- **Course**: AI in Action Lab
- **Topic**: Chatbot vs ReAct Agent comparison
- **Duration**: 3 days
- **Level**: Intermediate

---

## References

- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903)
- [Agents can retrieve and reason from Long-context Documents](https://arxiv.org/abs/2303.01497)

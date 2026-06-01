# 🚀 Quick Start Guide

## Installation (1 minute)

```bash
# Go to project directory
cd /mnt/e/Downloads/Lab_Handson_AI_Action/2A202600883-MaiHanhPham-Day-3-Lab-Chatbot-vs-react-agent

# Install test dependencies
pip install pytest -q
```

## Run Demo (1 minute)

```bash
python demo.py
```

**Output:**
- 🤖 Chatbot responses
- 🧠 Agent responses with step-by-step reasoning
- 📊 Metrics summary (tokens, latency, cost)
- 📝 JSONL telemetry logs

## Run Tests (30 seconds)

```bash
# All tests (40 tests)
python -m pytest tests/ -v

# Just tools
python -m pytest tests/test_tools.py -v

# Just chatbot
python -m pytest tests/test_chatbot.py -v

# Just agent
python -m pytest tests/test_agent.py -v
```

**Result:** ✅ 40/40 PASSED

## Use in Your Code

### Chatbot Example
```python
from src.core.mock_provider import MockLLMProvider
from src.chatbot.chatbot import BaselineChatbot

llm = MockLLMProvider()
chatbot = BaselineChatbot(llm)

response = chatbot.chat("Gợi ý món dưới 50k")
print(response)
```

### Agent Example
```python
from src.core.mock_provider import MockLLMProvider
from src.agent.agent import ReActAgent
from src.tools.menu_tool import MenuTool

llm = MockLLMProvider()
menu_tool = MenuTool("data/menu.json")

tools = {
    "search_menu": menu_tool.search_menu,
}

agent = ReActAgent(llm, tools, max_steps=5)
response, metrics = agent.run("Gợi ý món dưới 50k không cay")

print(response)    # Agent's final answer
print(metrics)     # Execution metrics
```

## File Locations

| Component | File |
|-----------|------|
| Chatbot | `src/chatbot/chatbot.py` |
| Agent | `src/agent/agent.py` |
| Tools | `src/tools/*.py` |
| Telemetry | `src/telemetry/*.py` |
| Tests | `tests/*.py` |
| Data | `data/menu.json`, `data/members.json` |
| Logs | `logs/agent_telemetry_*.jsonl` |
| Demo | `demo.py` |

## Next Steps

1. ✅ Run `python demo.py` to see it work
2. ✅ Run `python -m pytest tests/ -v` to verify tests
3. 📖 Read `LAB_IMPLEMENTATION.md` for full documentation
4. 🔧 Modify mock responses in `src/core/mock_provider.py`
5. 🧠 Add more tools to `src/tools/`
6. 🔗 Connect to real LLM (OpenAI, Gemini, etc.)

## Troubleshooting

**Import errors?**
```bash
# Make sure you're in the right directory
cd /mnt/e/Downloads/Lab_Handson_AI_Action/2A202600883-MaiHanhPham-Day-3-Lab-Chatbot-vs-react-agent
python demo.py
```

**Pytest not found?**
```bash
pip install pytest
```

**Want to see logs?**
```bash
ls logs/
head -20 logs/agent_telemetry_*.jsonl
cat metrics_summary.json
```

## Key Features

✨ **40 Pytest Tests** - All passing
🤖 **Mock LLM** - No API key needed
🧠 **ReAct Agent** - Full Thought-Action-Observation loop
🛠️ **5 Tools** - Menu, Order, Bill, User, Payment
📊 **JSONL Logs** - Structured telemetry
⚡ **Fast** - ~2 seconds to run all tests
📖 **Well Documented** - Comprehensive guides

## Architecture Overview

```
User Input
    ↓
LLM (Mock Provider)
    ↓
Agent Loop (max 5 steps)
    ├─ Parse Thought-Action-Observation
    ├─ Execute Tools (Menu, Order, Bill, User)
    └─ Accumulate Scratchpad
    ↓
Final Answer + Metrics
    ↓
Telemetry Logs (JSONL)
    ↓
Metrics Summary (JSON)
```

## Difference: Chatbot vs Agent

| | Chatbot | Agent |
|---|---------|-------|
| **Tool Use** | ❌ | ✅ |
| **Reasoning** | Direct | Step-by-step |
| **Speed** | 🟢 Fast | 🟠 Slower |
| **Reliability** | 🟠 Medium | 🟢 High |
| **Cost** | 🟢 Low | 🟠 Higher |

---

**Ready?** → `python demo.py` 🚀

# 🔑 Setup OpenAI Guide

## Step 1: Get OpenAI API Key

1. Truy cập [platform.openai.com](https://platform.openai.com/api/keys)
2. Đăng nhập hoặc tạo tài khoản
3. Tạo API key mới
4. Copy API key (bắt đầu với `sk-...`)

## Step 2: Cài đặt OpenAI Package

```bash
pip install openai
```

## Step 3: Tạo .env File

Tạo file `.env` trong thư mục lab:

```bash
# Option 1: Tạo thủ công
cat > .env << 'EOF'
OPENAI_API_KEY=sk-YOUR_API_KEY_HERE
EOF

# Option 2: Edit bằng VS Code
# Mở .env hoặc copy từ .env.example
```

**File .env content:**
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
```

⚠️ **QUAN TRỌNG**: Đừng push `.env` lên GitHub! Thêm vào `.gitignore`:
```bash
echo ".env" >> .gitignore
```

## Step 4: Chạy với OpenAI

### Demo đầy đủ (Chatbot + Agent)
```bash
python demo_openai.py
```

### Chạy trong Python code
```python
from src.core.openai_provider import OpenAIProvider
from src.chatbot.chatbot import BaselineChatbot
from src.agent.agent import ReActAgent

# Create LLM provider
llm = OpenAIProvider(model_name="gpt-4o-mini")

# Use with Chatbot
chatbot = BaselineChatbot(llm)
response = chatbot.chat("Gợi ý món dưới 50k")
print(response)

# Use with Agent
from src.tools.menu_tool import MenuTool
menu_tool = MenuTool("data/menu.json")
tools = {"search_menu": menu_tool.search_menu}
agent = ReActAgent(llm, tools)
response, metrics = agent.run("Gợi ý món dưới 50k không cay")
print(f"Response: {response}")
print(f"Tokens: {metrics['total_tokens']}")
```

## Troubleshooting

### Error: "API key is invalid"
```bash
# Check if .env is loaded correctly
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

### Error: "Module 'openai' not found"
```bash
pip install openai
```

### Error: "401 Unauthorized"
- Kiểm tra API key có đúng không
- Đảm bảo file `.env` ở đúng thư mục
- Tài khoản OpenAI có credit

### High cost warning
- Dùng `gpt-4o-mini` để tiết kiệm (rẻ hơn `gpt-4o`)
- `gpt-4o-mini` đủ tốt cho demo
- Mỗi request ~300-400 tokens

## Models Available

| Model | Cost | Speed | Quality |
|-------|------|-------|---------|
| `gpt-4o-mini` | 💰 | ⚡⚡⚡ | ⭐⭐⭐ |
| `gpt-4o` | 💰💰 | ⚡⚡ | ⭐⭐⭐⭐ |
| `gpt-4-turbo` | 💰💰💰 | ⚡ | ⭐⭐⭐⭐ |

👉 Khuyên dùng: `gpt-4o-mini` để demo

## Cost Estimation

- **Menu search**: ~50 tokens = $0.0001
- **Full conversation**: ~300 tokens = $0.0006
- **10 conversations**: ~3000 tokens = $0.006

*Tính theo giá gpt-4o-mini (May 2024)*

## Comparison: Mock vs OpenAI

| Aspect | Mock | OpenAI |
|--------|------|--------|
| **Speed** | Instant | 1-2 seconds |
| **Cost** | Free | $0.0001-0.001 |
| **Realism** | Fake patterns | Real responses |
| **API Key** | None | Required |
| **Best for** | Testing/Development | Production |

## Next Steps

1. ✅ Setup `.env` với API key
2. ✅ `pip install openai`
3. ✅ `python demo_openai.py`
4. 📊 Xem JSONL logs tại `logs/`
5. 💰 Check OpenAI billing dashboard

## Debugging

### See full request/response
```python
from src.core.openai_provider import OpenAIProvider
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

llm = OpenAIProvider()
response, usage = llm.generate("Test prompt")
print(f"Response: {response}")
print(f"Usage: {usage}")
```

### Check tokens before spending money
```python
from src.core.openai_provider import OpenAIProvider

llm = OpenAIProvider()
response, usage = llm.generate("Short test", system_prompt="Be brief")
print(f"Total tokens used: {usage['total_tokens']}")
print(f"Cost estimate: ${usage['total_tokens'] * 0.000001}")
```

---

**Status**: Ready to use OpenAI! 🚀

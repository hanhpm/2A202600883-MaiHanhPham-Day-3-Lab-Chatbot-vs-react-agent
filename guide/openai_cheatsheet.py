#!/usr/bin/env python3
"""
Cheat Sheet: Chạy Chatbot/Agent với OpenAI

Tóm tắt: 3 bước để chạy với OpenAI API thực
"""

print("""
╔══════════════════════════════════════════════════════════════════╗
║  🔑 CHẠY VỚI OPENAI API - HƯỚNG DẪN TẮT                        ║
╚══════════════════════════════════════════════════════════════════╝

STEP 1️⃣  - CẢI ĐẶT
───────────────────────────────────────────────────────────────
# Cài openai package
pip install openai

# Copy .env.example → .env
cp .env.example .env

# Edit .env, thay YOUR_KEY_HERE bằng API key thật
# OPENAI_API_KEY=sk-proj-xxxxx...


STEP 2️⃣  - LẤY API KEY
───────────────────────────────────────────────────────────────
1. Vào https://platform.openai.com/api/keys
2. Đăng nhập tài khoản OpenAI
3. Tạo "Create new secret key"
4. Copy (bắt đầu với "sk-...")
5. Paste vào .env


STEP 3️⃣  - CHẠY
───────────────────────────────────────────────────────────────
python demo_openai.py


═══════════════════════════════════════════════════════════════════

📝 SO SÁNH: MOCK vs OPENAI

Demo Mock (free, nhanh):
  $ python demo.py

Demo OpenAI (real, trả tiền):
  $ python demo_openai.py


═══════════════════════════════════════════════════════════════════

💻 SỬ DỤNG TRONG CODE
───────────────────────────────────────────────────────────────

# Mock (không cần API key)
from src.core.mock_provider import MockLLMProvider
llm = MockLLMProvider()

# OpenAI (cần .env hoặc OPENAI_API_KEY env var)
from src.core.openai_provider import OpenAIProvider
llm = OpenAIProvider(model_name="gpt-4o-mini")


═══════════════════════════════════════════════════════════════════

🤖 CHATBOT
───────────────────────────────────────────────────────────────

from src.core.openai_provider import OpenAIProvider
from src.chatbot.chatbot import BaselineChatbot

llm = OpenAIProvider()
chatbot = BaselineChatbot(llm)

response = chatbot.chat("Gợi ý món dưới 50k")
print(response)


═══════════════════════════════════════════════════════════════════

🧠 AGENT (dùng tools)
───────────────────────────────────────────────────────────────

from src.core.openai_provider import OpenAIProvider
from src.agent.agent import ReActAgent
from src.tools.menu_tool import MenuTool

llm = OpenAIProvider()
menu_tool = MenuTool("data/menu.json")
tools = {"search_menu": menu_tool.search_menu}

agent = ReActAgent(llm, tools)
response, metrics = agent.run("Gợi ý món dưới 50k không cay")

print(response)
print(f"Tokens: {metrics['total_tokens']}")


═══════════════════════════════════════════════════════════════════

💰 TÍNH CHI PHÍ
───────────────────────────────────────────────────────────────

Model: gpt-4o-mini (rẻ nhất)
- Mỗi request: ~300-400 tokens
- Chi phí: $0.0001-0.0002 mỗi request
- 100 requests: ~$0.01-0.02

👉 Khuyên dùng gpt-4o-mini để test


═══════════════════════════════════════════════════════════════════

🆘 LỖI THƯỜNG GẶP
───────────────────────────────────────────────────────────────

❌ "API key is invalid"
   → Kiểm tra .env có OPENAI_API_KEY không
   → Kiểm tra API key có đúng không (sk-...)

❌ "Module 'openai' not found"
   → pip install openai

❌ "401 Unauthorized"  
   → API key sai hoặc hết credit
   → Check OpenAI billing: https://platform.openai.com/account/billing/overview

❌ "Rate limit exceeded"
   → Chờ 1 phút, rồi thử lại


═══════════════════════════════════════════════════════════════════

📚 TÀI LIỆU CHI TIẾT
───────────────────────────────────────────────────────────────

👉 SETUP_OPENAI.md       - Hướng dẫn chi tiết setup
👉 demo_openai.py        - Script chạy với OpenAI
👉 LAB_IMPLEMENTATION.md - Tài liệu lab đầy đủ


═══════════════════════════════════════════════════════════════════

🎯 QUICK COMMANDS
───────────────────────────────────────────────────────────────

# Setup
pip install openai
cp .env.example .env
# Edit .env → thêm API key

# Chạy mock (free)
python demo.py

# Chạy OpenAI (trả tiền)
python demo_openai.py

# Chạy tests
pytest tests/ -v

# Xem logs
ls logs/
cat logs/agent_telemetry_*.jsonl


═══════════════════════════════════════════════════════════════════

✅ XỬ XONG! Sẵn sàng chạy với OpenAI? 🚀

""")

#!/usr/bin/env python3
"""
Demo script: Run chatbot and agent with REAL OpenAI API.

SETUP:
1. pip install openai
2. Create .env file with: OPENAI_API_KEY=sk-...
3. python demo_openai.py
"""

import os
from dotenv import load_dotenv
from src.chatbot.chatbot import BaselineChatbot
from src.agent.agent import ReActAgent
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker

# Setup tools
from src.tools.menu_tool import MenuTool
from src.tools.order_tool import OrderTool
from src.tools.bill_tool import BillTool
from src.tools.user_tool import UserTool

# Load .env file
load_dotenv()

# Use OpenAI instead of mock
from src.core.openai_provider import OpenAIProvider


def setup_agent_tools():
    """Initialize and connect all tools."""
    menu_tool = MenuTool(menu_path="data/menu.json")
    order_tool = OrderTool()
    bill_tool = BillTool()
    user_tool = UserTool(members_path="data/members.json")

    # Share menu data
    menu_data = menu_tool.menu
    order_tool.set_menu(menu_data)
    bill_tool.set_menu(menu_data)

    tools = {
        "search_menu": menu_tool.search_menu,
        "add_order": order_tool.add_order,
        "update_order": order_tool.update_order,
        "get_order": order_tool.get_order,
        "list_orders": order_tool.list_orders,
        "mark_paid": order_tool.mark_paid,
        "clear_orders": order_tool.clear_orders,
        "summarize_orders": lambda: (
            bill_tool.summarize_orders() if order_tool.orders else {"orders": [], "total": 0}
        ),
        "split_bill": lambda: (
            bill_tool.split_bill() if order_tool.orders else {"total": 0, "per_user": {}}
        ),
        "get_payment_status": lambda: bill_tool.get_payment_status(),
        "check_missing_orders": lambda: user_tool.check_missing_orders(order_tool.orders),
        "check_unpaid": lambda: user_tool.check_unpaid(order_tool.orders),
        "get_members": user_tool.get_members,
    }

    return tools, order_tool


def demo_chatbot_openai():
    """Demo baseline chatbot with OpenAI."""
    print("\n" + "=" * 70)
    print("BASELINE CHATBOT DEMO (with OpenAI)")
    print("=" * 70)

    try:
        llm = OpenAIProvider(model_name="gpt-4o-mini")
        chatbot = BaselineChatbot(llm)

        test_prompts = [
            "Xin chào, tôi muốn đặt cơm trưa",
            "Gợi ý món dưới 50k không cay",
            "Tôi thích ăn cơm gà",
        ]
        
        # test_prompts = [
        # "Xin chào, tôi muốn đặt cơm trưa",
        # "Gợi ý món trên 50k",
        # "Tôi thích ăn mỳ ",
        # ]

        for prompt in test_prompts:
            print(f"\n📝 User: {prompt}")
            response = chatbot.chat(prompt)
            print(f"🤖 Chatbot: {response[:200]}...")  # First 200 chars
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you have:")
        print("   1. pip install openai")
        print("   2. OPENAI_API_KEY in .env file")


def demo_agent_openai():
    """Demo ReAct agent with OpenAI."""
    print("\n" + "=" * 70)
    print("REACT AGENT DEMO (with OpenAI)")
    print("=" * 70)

    try:
        llm = OpenAIProvider(model_name="gpt-4o-mini")
        tools, order_tool = setup_agent_tools()
        agent = ReActAgent(llm, tools, max_steps=5)

        test_prompts = [
            "Gợi ý món dưới 50k không cay",
            "Thêm một đơn cho Minh: Cơm gà, ít cơm",
            "Ai chưa chọn món?",
        ]
        # test_prompts = [
        # "Gợi ý món trên 50k không cay",
        # "Thêm một đơn cho Minh: Phở, thêm cay",
        # "Ai chưa chọn món?",
        # ]

        results = []

        for prompt in test_prompts:
            print(f"\n📝 User: {prompt}")
            response, metrics = agent.run(prompt)
            print(f"🧠 Agent: {response[:200]}...")  # First 200 chars
            print(f"📊 Metrics: steps={metrics['steps']}, status={metrics['status']}, tokens={metrics.get('total_tokens', 0)}")

            results.append({"prompt": prompt, "response": response, "metrics": metrics})

            # Track metrics
            if metrics.get("total_tokens"):
                tracker.track_request("openai", "gpt-4o-mini",
                                    {"total_tokens": metrics["total_tokens"]}, 
                                    100)

        return results

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you have:")
        print("   1. pip install openai")
        print("   2. OPENAI_API_KEY in .env file")


def show_metrics():
    """Show metrics summary."""
    print("\n" + "=" * 70)
    print("METRICS SUMMARY")
    print("=" * 70)

    summary = tracker.get_summary()
    import json
    print(json.dumps(summary, indent=2))


def main():
    """Run full demo with OpenAI."""
    print("\n" + "=" * 70)
    print("LUNCH ORDERING SYSTEM: CHATBOT vs REACT AGENT (OpenAI Edition)")
    print("=" * 70)
    print("\n⏳ Note: This will make real API calls to OpenAI")
    print("💰 You will be charged based on token usage")
    print("🔑 API Key from: OPENAI_API_KEY environment variable\n")

    # Demo chatbot
    demo_chatbot_openai()

    # Demo agent
    demo_agent_openai()

    # Show metrics
    show_metrics()

    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()

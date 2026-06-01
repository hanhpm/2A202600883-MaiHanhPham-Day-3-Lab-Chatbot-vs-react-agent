#!/usr/bin/env python3
"""
Demo script: Run both chatbot and agent on lunch ordering tasks.
Shows comparison and generates metrics + logs.
"""

import json
from pathlib import Path
from src.core.mock_provider import MockLLMProvider
from src.chatbot.chatbot import BaselineChatbot
from src.agent.agent import ReActAgent
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker

# Setup tools for agent
from src.tools.menu_tool import MenuTool
from src.tools.order_tool import OrderTool
from src.tools.bill_tool import BillTool
from src.tools.user_tool import UserTool


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


def demo_chatbot():
    """Demo baseline chatbot."""
    print("\n" + "=" * 60)
    print("BASELINE CHATBOT DEMO")
    print("=" * 60)

    llm = MockLLMProvider(model_name="mock-chatbot")
    chatbot = BaselineChatbot(llm)

    # test_prompts = [
    #     "Xin chào, tôi muốn đặt cơm trưa",
    #     "Gợi ý món dưới 50k không cay",
    #     "Tôi thích ăn cơm gà",
    # ]
    test_prompts = [
        "Xin chào, tôi muốn đặt cơm trưa",
        "Gợi ý món trên 50k",
        "Tôi thích ăn mỳ ",
    ]
    

    for prompt in test_prompts:
        print(f"\nUser: {prompt}")
        response = chatbot.chat(prompt)
        print(f"Chatbot: {response}")

    print(f"\nConversation history length: {len(chatbot.conversation_history)}")


def demo_agent():
    """Demo ReAct agent."""
    print("\n" + "=" * 60)
    print("REACT AGENT DEMO")
    print("=" * 60)

    llm = MockLLMProvider(model_name="mock-agent")
    tools, order_tool = setup_agent_tools()
    agent = ReActAgent(llm, tools, max_steps=5)

    # test_prompts = [
    #     "Gợi ý món dưới 50k không cay",
    #     "Thêm một đơn cho Minh: Cơm gà, ít cơm",
    #     "Ai chưa chọn món?",
    # ]
    test_prompts = [
        "Gợi ý món trên 50k không cay",
        "Thêm một đơn cho Minh: Phở đi",
        "Ai chưa chọn món?",
    ]

    results = []

    for prompt in test_prompts:
        print(f"\nUser: {prompt}")
        response, metrics = agent.run(prompt)
        print(f"Agent: {response}")
        print(f"Metrics: steps={metrics['steps']}, status={metrics['status']}")

        results.append({"prompt": prompt, "response": response, "metrics": metrics})

        # Track metrics
        if metrics.get("total_tokens"):
            tracker.track_request("mock", "mock-agent", 
                                {"total_tokens": metrics["total_tokens"]}, 100)

    return results


def generate_metrics_report():
    """Generate and export metrics summary."""
    print("\n" + "=" * 60)
    print("METRICS SUMMARY")
    print("=" * 60)

    summary = tracker.get_summary()
    print(json.dumps(summary, indent=2))

    # Export metrics
    tracker.export_metrics_summary("metrics_summary.json")
    print("\nMetrics exported to: metrics_summary.json")


def show_logs():
    """Read and display JSONL logs."""
    print("\n" + "=" * 60)
    print("TELEMETRY LOGS (JSONL)")
    print("=" * 60)

    logs = logger.read_logs()
    print(f"Total events logged: {len(logs)}")

    # Show sample logs
    for i, log in enumerate(logs[:5]):
        print(f"\nLog {i+1}:")
        print(json.dumps(log, indent=2, ensure_ascii=False))

    print(f"\nLog file: {logger.get_log_file_path()}")


def main():
    """Run full demo."""
    print("\n" + "=" * 70)
    print("LUNCH ORDERING SYSTEM: CHATBOT vs REACT AGENT")
    print("=" * 70)

    # Demo chatbot
    demo_chatbot()

    # Demo agent
    demo_agent()

    # Show metrics
    generate_metrics_report()

    # Show logs
    show_logs()

    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()

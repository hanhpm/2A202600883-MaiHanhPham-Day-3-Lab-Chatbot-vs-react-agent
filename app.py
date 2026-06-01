#!/usr/bin/env python3
"""
Flask web demo: side-by-side comparison of Baseline Chatbot vs ReAct Agent
for the lunch ordering domain.

Run:
    pip install -r requirements.txt
    python app.py
    open http://localhost:5000
"""

import os
import threading
from typing import Tuple

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from src.agent.agent import ReActAgent
from src.chatbot.chatbot import BaselineChatbot
from src.core.mock_provider import MockLLMProvider
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker
from src.tools.bill_tool import BillTool
from src.tools.menu_tool import MenuTool
from src.tools.order_tool import OrderTool
from src.tools.user_tool import UserTool

load_dotenv()

app = Flask(__name__)


class AppState:
    """Holds singletons for chatbot, agent, tools, and current provider."""

    def __init__(self):
        self.lock = threading.Lock()
        self.provider_name = "mock"
        self.menu_tool = MenuTool(menu_path="data/menu.json")
        self.user_tool = UserTool(members_path="data/members.json")
        self.order_tool = OrderTool()
        self.bill_tool = BillTool()

        menu_data = self.menu_tool.menu
        self.order_tool.set_menu(menu_data)
        self.bill_tool.set_menu(menu_data)

        self.tools = self._build_tools()
        self.chatbot, self.agent = self._build_brains(self.provider_name)

    def _build_tools(self):
        return {
            "search_menu": self.menu_tool.search_menu,
            "add_order": self.order_tool.add_order,
            "update_order": self.order_tool.update_order,
            "get_order": self.order_tool.get_order,
            "list_orders": self.order_tool.list_orders,
            "mark_paid": self.order_tool.mark_paid,
            "clear_orders": self.order_tool.clear_orders,
            "summarize_orders": lambda: (
                self._bill_with_orders().summarize_orders()
                if self.order_tool.orders
                else {"orders": [], "total": 0}
            ),
            "split_bill": lambda: (
                self._bill_with_orders().split_bill()
                if self.order_tool.orders
                else {"total": 0, "per_user": {}}
            ),
            "get_payment_status": lambda: self._bill_with_orders().get_payment_status(),
            "check_missing_orders": lambda: self.user_tool.check_missing_orders(
                self.order_tool.orders
            ),
            "check_unpaid": lambda: self.user_tool.check_unpaid(self.order_tool.orders),
            "get_members": self.user_tool.get_members,
        }

    def _bill_with_orders(self) -> BillTool:
        self.bill_tool.set_orders(self.order_tool.orders)
        return self.bill_tool

    def _build_brains(self, provider_name: str) -> Tuple[BaselineChatbot, ReActAgent]:
        llm = self._make_provider(provider_name)
        return BaselineChatbot(llm), ReActAgent(llm, self.tools, max_steps=5)

    def _make_provider(self, name: str):
        name = (name or "mock").lower()
        if name == "openai":
            from src.core.openai_provider import OpenAIProvider

            return OpenAIProvider(model_name=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
        if name == "gemini":
            from src.core.gemini_provider import GeminiProvider

            return GeminiProvider(model_name=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
        if name == "local":
            from src.core.local_provider import LocalProvider

            path = os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf")
            return LocalProvider(model_path=path)
        return MockLLMProvider(model_name="mock-model")

    def set_provider(self, name: str):
        with self.lock:
            self.provider_name = name
            self.chatbot, self.agent = self._build_brains(name)

    def reset(self):
        with self.lock:
            self.order_tool.clear_orders()
            self.chatbot.clear_history()

    def state_snapshot(self) -> dict:
        bill = self._bill_with_orders()
        summary = bill.summarize_orders() if self.order_tool.orders else {
            "orders": [], "total": 0, "count": 0, "status": "success"
        }
        return {
            "provider": self.provider_name,
            "orders": self.order_tool.orders,
            "summary": summary,
            "members": self.user_tool.members,
            "missing": self.user_tool.check_missing_orders(self.order_tool.orders),
            "payment": bill.get_payment_status(),
        }


TOOL_WHITELIST = {
    "summarize_orders",
    "split_bill",
    "get_payment_status",
    "check_missing_orders",
    "check_unpaid",
    "mark_paid",
    "clear_orders",
    "list_orders",
    "get_members",
}


state = AppState()


@app.route("/")
def index():
    return render_template(
        "index.html",
        menu=state.menu_tool.menu,
        members=state.user_tool.members,
        provider=state.provider_name,
    )


@app.route("/api/chat", methods=["POST"])
def api_chat():
    payload = request.get_json(force=True)
    user_input = (payload or {}).get("message", "").strip()
    if not user_input:
        return jsonify({"error": "message is required"}), 400
    with state.lock:
        response = state.chatbot.chat(user_input)
    return jsonify({
        "response": response,
        "history_len": len(state.chatbot.conversation_history),
    })


@app.route("/api/agent", methods=["POST"])
def api_agent():
    payload = request.get_json(force=True)
    user_input = (payload or {}).get("message", "").strip()
    if not user_input:
        return jsonify({"error": "message is required"}), 400
    with state.lock:
        response, metrics = state.agent.run(user_input)
        if metrics.get("total_tokens"):
            tracker.track_request(
                state.provider_name,
                state.agent.llm.model_name,
                {"total_tokens": metrics["total_tokens"]},
                100,
            )
    return jsonify({
        "response": response,
        "metrics": {k: v for k, v in metrics.items() if k != "trace"},
        "trace": metrics.get("trace", []),
    })


@app.route("/api/provider", methods=["POST"])
def api_provider():
    payload = request.get_json(force=True)
    name = (payload or {}).get("provider", "mock")
    try:
        state.set_provider(name)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"provider": state.provider_name})


@app.route("/api/reset", methods=["POST"])
def api_reset():
    state.reset()
    return jsonify({"status": "ok"})


@app.route("/api/state")
def api_state():
    return jsonify(state.state_snapshot())


@app.route("/api/tool/<name>", methods=["POST"])
def api_tool(name):
    """Direct tool invocation (no LLM). Used by quick-action buttons."""
    if name not in TOOL_WHITELIST:
        return jsonify({"error": f"Tool '{name}' is not exposed via this endpoint"}), 403
    if name not in state.tools:
        return jsonify({"error": f"Tool '{name}' not registered"}), 404
    args = request.get_json(silent=True) or {}
    try:
        with state.lock:
            result = state.tools[name](**args)
    except TypeError as e:
        return jsonify({"error": f"Invalid args: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"tool": name, "result": result})


@app.route("/api/logs/tail")
def api_logs_tail():
    n = int(request.args.get("n", 20))
    logs = logger.read_logs()
    return jsonify({"events": logs[-n:], "file": logger.get_log_file_path()})


@app.route("/api/metrics")
def api_metrics():
    return jsonify(tracker.get_summary())


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

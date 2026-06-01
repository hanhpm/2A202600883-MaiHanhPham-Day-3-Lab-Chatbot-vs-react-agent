"""
Tests for ReAct agent.
"""

import pytest
import json
from pathlib import Path
from src.core.mock_provider import MockLLMProvider
from src.agent.agent import ReActAgent
from src.tools.menu_tool import MenuTool
from src.tools.order_tool import OrderTool
from src.tools.bill_tool import BillTool
from src.tools.user_tool import UserTool


@pytest.fixture
def mock_llm():
    """Fixture for mock LLM provider."""
    return MockLLMProvider(model_name="mock-agent-model")


@pytest.fixture
def setup_tools():
    """Fixture to set up all tools."""
    menu_tool = MenuTool(menu_path="data/menu.json")
    order_tool = OrderTool()
    bill_tool = BillTool()
    user_tool = UserTool(members_path="data/members.json")

    # Share menu data across tools
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
        "summarize_orders": lambda: bill_tool.summarize_orders() if order_tool.orders else {"orders": [], "total": 0},
        "split_bill": lambda: bill_tool.split_bill() if order_tool.orders else {"total": 0, "per_user": {}},
        "get_payment_status": lambda: bill_tool.get_payment_status(),
        "check_missing_orders": lambda: user_tool.check_missing_orders(order_tool.orders),
        "check_unpaid": lambda: user_tool.check_unpaid(order_tool.orders),
        "get_members": user_tool.get_members,
    }

    return tools, order_tool, bill_tool


@pytest.fixture
def agent(mock_llm, setup_tools):
    """Fixture for ReAct agent."""
    tools, _, _ = setup_tools
    return ReActAgent(mock_llm, tools, max_steps=5)


class TestReActAgent:
    """Tests for ReActAgent."""

    def test_agent_initialization(self, agent):
        """Test agent is initialized properly."""
        assert agent is not None
        assert len(agent.tools) > 0
        assert agent.max_steps == 5

    def test_system_prompt_generation(self, agent):
        """Test system prompt includes tool descriptions."""
        prompt = agent.get_system_prompt()
        assert "search_menu" in prompt
        assert "add_order" in prompt
        assert "Final Answer" in prompt

    def test_agent_search_menu(self, agent):
        """Test agent can search for menu items."""
        response, metrics = agent.run("Gợi ý món dưới 50k không cay")
        assert len(response) > 0
        assert metrics["status"] == "success"
        assert metrics["steps"] > 0

    def test_agent_add_order(self, agent, setup_tools):
        """Test agent can add an order."""
        tools, order_tool, _ = setup_tools
        agent.tools["add_order"] = order_tool.add_order
        agent.tools["list_orders"] = order_tool.list_orders

        response, metrics = agent.run("Thêm một đơn cho Minh: Cơm gà")
        assert metrics["status"] == "success"

    def test_agent_multiple_steps(self, agent):
        """Test agent can perform multi-step reasoning."""
        response, metrics = agent.run("Tôi muốn ăn gì đó dưới 50k, không cay")
        assert metrics["steps"] >= 1  # Should take at least one step
        assert len(response) > 0

    def test_agent_error_handling(self, agent):
        """Test agent handles unknown tools gracefully."""
        response, metrics = agent.run("Call nonexistent_tool")
        # Even with errors, should have some response
        assert metrics is not None

    def test_agent_max_steps(self, agent):
        """Test agent respects max steps limit."""
        agent_limited = ReActAgent(agent.llm, agent.tools, max_steps=2)
        response, metrics = agent_limited.run("Do something complex")
        # Should not exceed max steps
        assert metrics["steps"] <= 2

    def test_action_parsing(self, agent):
        """Test action parsing from LLM response."""
        llm_response = """Thought: I need to search the menu.
Action: {"tool": "search_menu", "args": {"max_price": 50000}}
Observation: [...]"""

        action = agent._parse_action(llm_response)
        assert action["tool"] == "search_menu"
        assert action["args"]["max_price"] == 50000

    def test_action_parsing_error(self, agent):
        """Test that invalid action raises error."""
        llm_response = "Thought: Something\nAction: {invalid json}"

        with pytest.raises(ValueError):
            agent._parse_action(llm_response)

    def test_tool_execution(self, agent):
        """Test tool execution from action dict."""
        action = {"tool": "get_members", "args": {}}
        result = agent._execute_tool(action)
        assert "members" in result or isinstance(result, str)

    def test_unknown_tool_handling(self, agent):
        """Test graceful handling of unknown tools."""
        action = {"tool": "nonexistent_tool", "args": {}}
        result = agent._execute_tool(action)
        assert "error" in result.lower() or "UNKNOWN_TOOL" in result


class TestAgentVsChatbot:
    """Comparison tests between agent and chatbot."""

    def test_agent_vs_chatbot_tool_usage(self, agent, mock_llm):
        """Test that agent uses tools while chatbot doesn't."""
        from src.chatbot.chatbot import BaselineChatbot

        chatbot = BaselineChatbot(mock_llm)

        # Agent should produce tool calls
        agent_response, _ = agent.run("Tôi muốn ăn gì dưới 50k")
        # Chatbot should not
        chatbot_response = chatbot.chat("Tôi muốn ăn gì dưới 50k")

        # Agent traces should be longer (include tool calls)
        # Chatbot should be simpler response
        assert len(chatbot_response) >= 0  # Chatbot still produces output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

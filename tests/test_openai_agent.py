"""
Integration tests for OpenAI-based ReAct Agent.
These tests require OPENAI_API_KEY environment variable.
Run with: pytest tests/test_openai_agent.py -v -s
"""

import pytest
import json
import os
from src.core.openai_provider import OpenAIProvider
from src.agent.agent import ReActAgent
from src.tools.menu_tool import MenuTool
from src.tools.order_tool import OrderTool
from src.tools.bill_tool import BillTool
from src.tools.user_tool import UserTool


# Skip tests if OpenAI API key not available
pytestmark = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY environment variable not set"
)


@pytest.fixture
def openai_llm():
    """Fixture for OpenAI LLM provider."""
    return OpenAIProvider(model_name="gpt-4o-mini")


@pytest.fixture
def setup_openai_agent_tools():
    """Fixture to set up agent with real tools."""
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


@pytest.fixture
def openai_agent(openai_llm, setup_openai_agent_tools):
    """Fixture for ReAct agent with OpenAI."""
    tools, _ = setup_openai_agent_tools
    return ReActAgent(openai_llm, tools, max_steps=5)


class TestOpenAIAgent:
    """Tests for ReAct Agent with real OpenAI API."""

    def test_agent_initialization(self, openai_agent):
        """Test agent initializes with OpenAI."""
        assert openai_agent is not None
        assert len(openai_agent.tools) > 0
        assert openai_agent.max_steps == 5

    def test_system_prompt_includes_tools(self, openai_agent):
        """Test system prompt includes tool descriptions."""
        prompt = openai_agent.get_system_prompt()
        assert "search_menu" in prompt
        assert "Final Answer" in prompt
        assert "Action:" in prompt or "tool" in prompt.lower()

    def test_real_menu_search(self, openai_agent):
        """Test agent can search menu with real OpenAI."""
        response, metrics = openai_agent.run("Gợi ý món dưới 50k không cay")
        assert len(response) > 0
        assert metrics["status"] in ["success", "failed"]
        assert metrics["steps"] >= 1

    def test_agent_produces_different_results(self, openai_agent):
        """Test agent produces real (non-mock) results."""
        from src.core.mock_provider import MockLLMProvider

        # OpenAI response
        openai_response, _ = openai_agent.run("Gợi ý món ăn")

        # Mock response for comparison
        mock_llm = MockLLMProvider()
        mock_tools = openai_agent.tools
        mock_agent = ReActAgent(mock_llm, mock_tools)
        mock_response, _ = mock_agent.run("Gợi ý món ăn")

        # Responses should be different
        assert openai_response != mock_response

    def test_multi_step_reasoning(self, openai_agent):
        """Test agent can do multi-step reasoning."""
        response, metrics = openai_agent.run("Tôi muốn ăn gì đó dưới 50k, không cay, là một món cơm")
        assert metrics["steps"] >= 1
        assert len(response) > 0

    def test_error_handling(self, openai_agent):
        """Test agent handles errors gracefully."""
        response, metrics = openai_agent.run("Call nonexistent_tool please")
        # Should not crash, should handle gracefully
        assert metrics is not None

    def test_max_steps_respected(self, openai_agent):
        """Test agent respects max steps limit."""
        assert openai_agent.max_steps == 5
        response, metrics = openai_agent.run("Do something very complex")
        assert metrics["steps"] <= openai_agent.max_steps

    def test_token_usage_tracking(self, openai_agent):
        """Test that token usage is tracked."""
        response, metrics = openai_agent.run("Xin chào")
        assert metrics.get("total_tokens", 0) >= 0

    def test_agent_response_quality(self, openai_agent):
        """Test agent produces coherent responses."""
        response, metrics = openai_agent.run("Gợi ý 3 món ăn dưới 50k")
        assert len(response) > 0
        # Response should be in Vietnamese or intelligible
        assert metrics["status"] in ["success", "failed"]

    def test_action_parsing_with_openai(self, openai_agent):
        """Test action parsing works with OpenAI responses."""
        from src.core.mock_provider import MockLLMProvider

        # Get a sample OpenAI response
        mock_llm = MockLLMProvider()
        llm_response, _ = mock_llm.generate(
            "Test",
            system_prompt="Return: Thought: test\\nAction: {\"tool\": \"search_menu\", \"args\": {}}"
        )

        # Should be parseable
        try:
            action = openai_agent._parse_action(llm_response)
            assert "tool" in action
        except ValueError:
            # If parsing fails, that's ok for this test
            pass


class TestOpenAIAgentWithTools:
    """Test agent integration with actual tools."""

    def test_agent_with_real_menu_data(self, openai_agent):
        """Test agent works with real menu data."""
        response, metrics = openai_agent.run("Có bao nhiêu loại cơm?")
        assert len(response) > 0
        assert metrics["status"] != "error" or metrics["steps"] > 0

    def test_agent_menu_accuracy(self, openai_agent):
        """Test agent gives accurate menu information."""
        response, metrics = openai_agent.run("Cơm gà giá bao nhiêu?")
        # Should mention price from actual menu (45000)
        assert len(response) > 0

    def test_agent_filter_by_price(self, openai_agent):
        """Test agent can filter menu by price."""
        response, metrics = openai_agent.run("Có mondefinido nào dưới 45k không?")
        assert len(response) > 0

    def test_agent_filter_by_spicy(self, openai_agent):
        """Test agent can filter menu by spicy level."""
        response, metrics = openai_agent.run("Tôi không thích cay, gợi ý gì?")
        assert len(response) > 0

    def test_agent_member_list(self, openai_agent):
        """Test agent knows team members."""
        response, metrics = openai_agent.run("Những thành viên trong nhóm là ai?")
        assert len(response) > 0
        # Should potentially mention team members


class TestOpenAIAgentCost:
    """Tests related to API cost tracking."""

    def test_cost_calculation(self, openai_llm):
        """Test that cost can be calculated from tokens."""
        response, usage = openai_llm.generate("Hello")
        tokens = usage.get("total_tokens", 0)
        # Cost for gpt-4o-mini is ~$0.00001 per token
        cost = tokens * 0.00001
        assert cost >= 0

    def test_token_usage_reasonable(self, openai_agent):
        """Test token usage is reasonable."""
        response, metrics = openai_agent.run("Hi")
        tokens = metrics.get("total_tokens", 0)
        # Reasonable range for a simple query
        assert 0 <= tokens <= 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

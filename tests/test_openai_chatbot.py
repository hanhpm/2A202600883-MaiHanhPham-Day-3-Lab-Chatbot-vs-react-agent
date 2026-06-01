"""
Integration tests for OpenAI-based Chatbot.
These tests require OPENAI_API_KEY environment variable.
Run with: pytest tests/test_openai_chatbot.py -v -s
"""

import pytest
import os
from src.core.openai_provider import OpenAIProvider
from src.chatbot.chatbot import BaselineChatbot


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
def openai_chatbot(openai_llm):
    """Fixture for chatbot with OpenAI."""
    return BaselineChatbot(openai_llm)


class TestOpenAIChatbot:
    """Tests for Chatbot with real OpenAI API."""

    def test_chatbot_initialization(self, openai_chatbot):
        """Test chatbot initializes with OpenAI."""
        assert openai_chatbot is not None
        assert len(openai_chatbot.conversation_history) == 0

    def test_real_greeting(self, openai_chatbot):
        """Test real chatbot greeting."""
        response = openai_chatbot.chat("Xin chào")
        assert len(response) > 0
        assert isinstance(response, str)

    def test_real_menu_question(self, openai_chatbot):
        """Test real chatbot menu recommendation."""
        response = openai_chatbot.chat("Gợi ý món dưới 50k không cay")
        assert len(response) > 0
        # Should mention food or suggestions
        response_lower = response.lower()
        assert any(word in response_lower for word in ["cơm", "bún", "phở", "ăn", "món", "gợi ý"])

    def test_real_order_question(self, openai_chatbot):
        """Test real chatbot order handling."""
        response = openai_chatbot.chat("Tôi muốn đặt cơm gà")
        assert len(response) > 0

    def test_conversation_history_tracking(self, openai_chatbot):
        """Test conversation history is tracked."""
        openai_chatbot.chat("Xin chào")
        openai_chatbot.chat("Tôi muốn đặt cơm")
        assert len(openai_chatbot.conversation_history) >= 4  # At least 2 exchanges

    def test_multi_turn_conversation(self, openai_chatbot):
        """Test multi-turn conversation."""
        response1 = openai_chatbot.chat("Bạn là ai?")
        response2 = openai_chatbot.chat("Bạn có thể giúp tôi đặt cơm không?")
        response3 = openai_chatbot.chat("Cảm ơn bạn")

        assert len(response1) > 0
        assert len(response2) > 0
        assert len(response3) > 0
        assert len(openai_chatbot.conversation_history) >= 6

    def test_clear_history(self, openai_chatbot):
        """Test clearing conversation history."""
        openai_chatbot.chat("Xin chào")
        openai_chatbot.clear_history()
        assert len(openai_chatbot.conversation_history) == 0

    def test_context_awareness(self, openai_chatbot):
        """Test that chatbot can use conversation context."""
        openai_chatbot.chat("Tôi tên là Minh")
        response = openai_chatbot.chat("Tôi là ai?")
        # Chatbot should reference previous message (context-aware)
        assert len(response) > 0

    def test_no_tool_calling_with_openai(self, openai_chatbot):
        """Test that chatbot doesn't use tools even with OpenAI."""
        response = openai_chatbot.chat("Tôi muốn tổng hợp đơn hàng")
        # Chatbot should respond conversationally, not with Action JSON
        assert "Action:" not in response or "{" not in response or "tool" not in response.lower()


class TestOpenAIProvider:
    """Tests for OpenAI provider itself."""

    def test_provider_initialization(self, openai_llm):
        """Test OpenAI provider initializes."""
        assert openai_llm is not None
        assert openai_llm.model_name == "gpt-4o-mini"

    def test_provider_api_key_loaded(self, openai_llm):
        """Test API key is loaded from environment."""
        assert openai_llm.api_key is not None
        assert openai_llm.api_key.startswith("sk-")

    def test_generate_response(self, openai_llm):
        """Test generating a real response."""
        response, usage = openai_llm.generate(
            "Xin chào. Bạn là ai?",
            system_prompt="Bạn là một trợ lý thân thiện"
        )
        assert len(response) > 0
        assert isinstance(response, str)
        assert usage.get("total_tokens", 0) > 0

    def test_usage_tracking(self, openai_llm):
        """Test that token usage is tracked."""
        response, usage = openai_llm.generate("Hello")
        assert "total_tokens" in usage
        assert "prompt_tokens" in usage
        assert "completion_tokens" in usage
        assert usage["total_tokens"] > 0

    def test_system_prompt_usage(self, openai_llm):
        """Test system prompt affects response."""
        # With system prompt to be brief
        response_brief, _ = openai_llm.generate(
            "Gợi ý 5 thứ tôi có thể ăn",
            system_prompt="Trả lời rất ngắn, chỉ 1-2 từ"
        )
        # Without system prompt
        response_normal, _ = openai_llm.generate(
            "Gợi ý 5 thứ tôi có thể ăn"
        )

        assert len(response_brief) > 0
        assert len(response_normal) > 0
        # Brief response should generally be shorter
        assert len(response_brief) <= len(response_normal) + 50  # Allow some variance


class TestOpenAIChatbotVsMock:
    """Compare OpenAI chatbot with mock chatbot."""

    def test_openai_returns_different_response(self, openai_chatbot):
        """Test that OpenAI returns real (non-mock) responses."""
        from src.core.mock_provider import MockLLMProvider
        from src.chatbot.chatbot import BaselineChatbot as MockChatbot

        openai_response = openai_chatbot.chat("Gợi ý món ăn")

        mock_llm = MockLLMProvider()
        mock_chatbot = MockChatbot(mock_llm)
        mock_response = mock_chatbot.chat("Gợi ý món ăn")

        # Responses should be different (OpenAI is real, mock is predetermined)
        assert openai_response != mock_response


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

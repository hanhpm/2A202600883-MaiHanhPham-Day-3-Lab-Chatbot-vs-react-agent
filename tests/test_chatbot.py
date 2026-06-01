"""
Tests for baseline chatbot.
"""

import pytest
from src.core.mock_provider import MockLLMProvider
from src.chatbot.chatbot import BaselineChatbot


@pytest.fixture
def mock_llm():
    """Fixture for mock LLM provider."""
    return MockLLMProvider(model_name="mock-lunch-ordering")


@pytest.fixture
def chatbot(mock_llm):
    """Fixture for baseline chatbot."""
    return BaselineChatbot(mock_llm)


class TestBaselineChatbot:
    """Tests for BaselineChatbot."""

    def test_chatbot_initialization(self, chatbot):
        """Test chatbot is initialized properly."""
        assert chatbot is not None
        assert len(chatbot.conversation_history) == 0

    def test_simple_greeting(self, chatbot):
        """Test chatbot responds to greeting."""
        response = chatbot.chat("Xin chào")
        assert len(response) > 0
        assert isinstance(response, str)

    def test_menu_question(self, chatbot):
        """Test chatbot handles menu inquiries."""
        response = chatbot.chat("Gợi ý món dưới 50k")
        assert len(response) > 0
        # Should have some content about food recommendations
        assert any(word in response.lower() for word in ["cơm", "bún", "phở"])

    def test_conversation_history(self, chatbot):
        """Test that conversation history is tracked."""
        chatbot.chat("Xin chào")
        chatbot.chat("Tôi muốn đặt cơm")
        assert len(chatbot.conversation_history) >= 4  # At least 2 user + 2 assistant messages

    def test_clear_history(self, chatbot):
        """Test clearing conversation history."""
        chatbot.chat("Xin chào")
        chatbot.clear_history()
        assert len(chatbot.conversation_history) == 0

    def test_get_history(self, chatbot):
        """Test retrieving conversation history."""
        chatbot.chat("Xin chào")
        history = chatbot.get_history()
        assert len(history) > 0
        assert "User:" in history[0] or "Assistant:" in history[0]

    def test_no_tool_calling(self, chatbot):
        """Test that chatbot doesn't make tool calls."""
        response = chatbot.chat("Tôi muốn tổng hợp đơn hàng")
        # Chatbot should respond without "Action:" pattern
        assert "Action:" not in response or "tool" not in response.lower()

    def test_multiple_turns(self, chatbot):
        """Test chatbot handles multiple conversation turns."""
        response1 = chatbot.chat("Bạn là ai?")
        response2 = chatbot.chat("Giúp tôi với")
        response3 = chatbot.chat("Cảm ơn bạn")

        assert len(response1) > 0
        assert len(response2) > 0
        assert len(response3) > 0

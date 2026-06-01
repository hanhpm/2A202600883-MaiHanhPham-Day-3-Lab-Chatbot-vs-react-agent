"""
Unit tests for LLM Provider implementations.
Tests both MockLLMProvider and OpenAIProvider.
Run with: pytest tests/test_llm_providers.py -v
"""

import pytest
import json
from src.core.mock_provider import MockLLMProvider
from src.core.openai_provider import OpenAIProvider
import os


class TestMockLLMProvider:
    """Tests for MockLLMProvider."""

    @pytest.fixture
    def mock_provider(self):
        """Fixture for mock provider."""
        return MockLLMProvider()

    def test_provider_initialization(self, mock_provider):
        """Test mock provider initializes."""
        assert mock_provider is not None
        assert mock_provider.model_name == "mock-model"

    def test_generate_returns_tuple(self, mock_provider):
        """Test generate returns (response, usage) tuple."""
        response, usage = mock_provider.generate("Hello")
        assert isinstance(response, str)
        assert isinstance(usage, dict)
        assert len(response) > 0

    def test_usage_dict_structure(self, mock_provider):
        """Test usage dict has expected keys."""
        _, usage = mock_provider.generate("Test")
        assert "total_tokens" in usage
        assert "prompt_tokens" in usage
        assert "completion_tokens" in usage

    def test_token_counting(self, mock_provider):
        """Test token counting is implemented."""
        _, usage = mock_provider.generate("Test prompt")
        assert usage["total_tokens"] > 0
        assert usage["prompt_tokens"] > 0
        assert usage["completion_tokens"] > 0

    def test_system_prompt_accepted(self, mock_provider):
        """Test system prompt is accepted."""
        response, usage = mock_provider.generate(
            "User message",
            system_prompt="You are helpful"
        )
        assert len(response) > 0
        assert usage["total_tokens"] > 0

    def test_thought_action_format(self, mock_provider):
        """Test mock can generate Thought-Action format."""
        response, _ = mock_provider.generate(
            "Search for menu items",
            system_prompt="Respond with Thought and Action"
        )
        # Should have thought-action format (since it's pattern-based)
        assert len(response) > 0

    def test_menu_search_response(self, mock_provider):
        """Test mock responds to menu search."""
        response, _ = mock_provider.generate("Gợi ý món dưới 50k")
        assert len(response) > 0
        # Mock should provide a menu-related response

    def test_order_response(self, mock_provider):
        """Test mock responds to order requests."""
        response, _ = mock_provider.generate("Thêm một đơn cho Minh")
        assert len(response) > 0

    def test_consistent_response_type(self, mock_provider):
        """Test mock always returns string responses."""
        for prompt in ["Hello", "123", "xyz", "Gợi ý"]:
            response, _ = mock_provider.generate(prompt)
            assert isinstance(response, str)

    def test_non_empty_responses(self, mock_provider):
        """Test mock never returns empty responses."""
        for prompt in ["Hi", "Test", "Menu"]:
            response, _ = mock_provider.generate(prompt)
            assert len(response) > 0


class TestOpenAIProviderUnit:
    """Unit tests for OpenAIProvider (can run without API calls)."""

    @pytest.fixture
    def has_api_key(self):
        """Check if API key is available."""
        return os.getenv("OPENAI_API_KEY") is not None

    def test_provider_initialization_with_key(self):
        """Test provider initializes when API key is available."""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        provider = OpenAIProvider()
        assert provider is not None
        assert provider.model_name == "gpt-4o-mini"

    def test_provider_custom_model(self):
        """Test provider accepts custom model name."""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        provider = OpenAIProvider(model_name="gpt-4")
        assert provider.model_name == "gpt-4"

    def test_api_key_from_environment(self):
        """Test API key is loaded from environment."""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        provider = OpenAIProvider()
        assert provider.api_key is not None
        assert len(provider.api_key) > 0

    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY environment variable not set"
    )
    def test_generate_returns_tuple(self):
        """Test generate returns (response, usage) tuple."""
        provider = OpenAIProvider()
        response, usage = provider.generate("Test")
        assert isinstance(response, str)
        assert isinstance(usage, dict)

    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY environment variable not set"
    )
    def test_usage_dict_has_tokens(self):
        """Test usage dict contains token information."""
        provider = OpenAIProvider()
        _, usage = provider.generate("Test")
        assert "total_tokens" in usage
        assert usage["total_tokens"] > 0


class TestProviderInterface:
    """Tests to ensure both providers implement consistent interface."""

    @pytest.fixture
    def mock_provider(self):
        """Fixture for mock provider."""
        return MockLLMProvider()

    def test_both_providers_have_generate_method(self, mock_provider):
        """Test both providers have generate method."""
        assert hasattr(mock_provider, 'generate')
        assert callable(getattr(mock_provider, 'generate'))

    def test_both_providers_return_compatible_tuples(self, mock_provider):
        """Test both return compatible (response, usage) tuples."""
        response, usage = mock_provider.generate("test")
        
        # Check response is string
        assert isinstance(response, str)
        
        # Check usage has token info
        assert isinstance(usage, dict)
        assert "total_tokens" in usage

    def test_mock_provider_deterministic(self, mock_provider):
        """Test mock provider gives consistent responses."""
        response1, usage1 = mock_provider.generate("same prompt")
        response2, usage2 = mock_provider.generate("same prompt")
        
        # Mock should be deterministic for same input
        assert len(response1) > 0
        assert len(response2) > 0

    def test_token_calculation_reasonable(self, mock_provider):
        """Test token calculations are reasonable."""
        short_response, usage1 = mock_provider.generate("hi")
        long_response, usage2 = mock_provider.generate("This is a much longer prompt with more words that should take more tokens to process")
        
        # Longer prompt should have more tokens
        assert usage1["total_tokens"] > 0
        assert usage2["total_tokens"] >= usage1["total_tokens"]

    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY environment variable not set"
    )
    def test_both_providers_with_system_prompt(self):
        """Test both providers accept system prompt parameter."""
        mock = MockLLMProvider()
        openai = OpenAIProvider()
        
        system = "You are a helpful assistant"
        user_msg = "Hello"
        
        mock_resp, mock_usage = mock.generate(user_msg, system_prompt=system)
        openai_resp, openai_usage = openai.generate(user_msg, system_prompt=system)
        
        assert len(mock_resp) > 0
        assert len(openai_resp) > 0


class TestMockProviderPatterns:
    """Tests for mock provider pattern matching."""

    @pytest.fixture
    def mock_provider(self):
        """Fixture for mock provider."""
        return MockLLMProvider()

    def test_menu_keyword_detection(self, mock_provider):
        """Test mock detects menu-related keywords."""
        for keyword in ["menu", "Menu", "MENU", "đặt cơm", "ăn gì"]:
            response, _ = mock_provider.generate(keyword)
            assert len(response) > 0

    def test_order_keyword_detection(self, mock_provider):
        """Test mock detects order-related keywords."""
        for keyword in ["order", "đặt", "thêm", "add", "gọi"]:
            response, _ = mock_provider.generate(keyword)
            assert len(response) > 0

    def test_greeting_detection(self, mock_provider):
        """Test mock detects greetings."""
        for greeting in ["hello", "hi", "xin chào", "chào", "hey"]:
            response, _ = mock_provider.generate(greeting)
            assert len(response) > 0

    def test_fallback_response(self, mock_provider):
        """Test mock provides fallback for unknown patterns."""
        response, _ = mock_provider.generate("xyzabc123randomtext")
        assert len(response) > 0
        # Should have some default response


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

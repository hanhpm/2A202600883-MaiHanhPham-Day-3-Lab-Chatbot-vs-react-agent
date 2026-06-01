from typing import Optional
from src.core.llm_provider import LLMProvider


class BaselineChatbot:
    """
    Baseline chatbot that responds directly based on LLM without using tools.
    """

    def __init__(self, llm: LLMProvider):
        self.llm = llm
        self.conversation_history = []

    def chat(self, user_input: str) -> str:
        """
        Simple chatbot response: send input to LLM, get response.
        No tool calling, just conversational.
        """
        system_prompt = """Bạn là một chatbot hỗ trợ đặt cơm trưa cho nhóm.
Trả lời các câu hỏi về menu, gợi ý món ăn, hoặc hướng dẫn cách đặt cơm.
Không gọi bất kỳ tool nào. Chỉ trả lời dựa trên kiến thức cơ bản."""

        # Build context from conversation history
        context = "\n".join(self.conversation_history[-5:])  # Last 5 messages
        full_prompt = f"{context}\nUser: {user_input}"

        # Get response from LLM
        response, usage = self.llm.generate(full_prompt, system_prompt=system_prompt)

        # Extract just the final answer (if it has that pattern)
        if "Final Answer:" in response:
            answer = response.split("Final Answer:")[-1].strip()
        else:
            answer = response

        # Store in history
        self.conversation_history.append(f"User: {user_input}")
        self.conversation_history.append(f"Assistant: {answer}")

        return answer

    def get_history(self) -> list[str]:
        """Get conversation history."""
        return self.conversation_history

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []

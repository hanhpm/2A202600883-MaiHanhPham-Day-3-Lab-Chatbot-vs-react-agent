from typing import Optional
from datetime import datetime


class MockLLMProvider:
    """Mock LLM Provider for offline testing without API keys."""

    def __init__(self, model_name: str = "mock-model"):
        self.model_name = model_name
        self.token_usage = {"prompt_tokens": 0, "completion_tokens": 0}
        self.latency_ms = 100  # simulated latency

    def generate(self, prompt: str, system_prompt: str = "") -> tuple[str, dict]:
        """
        Generate a mock response based on input prompt.
        Returns (response, usage_dict)
        """
        # Simulate thinking time
        import time
        start = time.time()

        response = self._get_mock_response(prompt, system_prompt)

        latency = (time.time() - start) * 1000
        usage = {
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": len(response.split()),
            "total_tokens": len(prompt.split()) + len(response.split()),
        }

        self.token_usage = usage
        return response, usage

    def _get_mock_response(self, prompt: str, system_prompt: str) -> str:
        """
        Return appropriate mock response based on prompt keywords.
        """
        prompt_lower = prompt.lower()

        # Pattern: user searching for menu
        if "search_menu" in prompt or "gợi ý món" in prompt or "dưới" in prompt:
            return """Thought: Người dùng cần tìm món ăn phù hợp. Tôi sẽ gọi search_menu tool.
Action: {"tool": "search_menu", "args": {"max_price": 50000, "spicy": false}}
Observation: [{"item_id": "M01", "name": "Cơm gà", "price": 45000, "spicy": false}, {"item_id": "M02", "name": "Bún thịt nướng", "price": 50000, "spicy": false}]

Thought: Có 2 món phù hợp. Tôi sẽ gợi ý cho người dùng.
Final Answer: Bạn có thể chọn cơm gà 45k hoặc bún thịt nướng 50k. Cái nào bạn thích?"""

        # Pattern: add order
        elif "chọn" in prompt or "cơm gà" in prompt or "thêm" in prompt:
            return """Thought: Người dùng muốn đặt một món ăn. Tôi sẽ gọi add_order.
Action: {"tool": "add_order", "args": {"user": "Minh", "item_id": "M01", "note": "ít cơm"}}
Observation: {"status": "success", "message": "Order added for Minh"}

Final Answer: Đã lưu đơn cho Minh: Cơm gà, ít cơm."""

        # Pattern: summarize orders
        elif "tổng" in prompt or "summary" in prompt or "đơn" in prompt:
            return """Thought: Người dùng muốn xem tổng hợp đơn hàng. Tôi gọi summarize_orders.
Action: {"tool": "summarize_orders", "args": {}}
Observation: {"orders": [{"user": "Minh", "item": "Cơm gà", "price": 45000}, {"user": "Hạnh", "item": "Bún thịt nướng", "price": 50000}], "total": 95000}

Final Answer: Đơn hàng hiện tại:
- Minh: Cơm gà 45k
- Hạnh: Bún thịt nướng 50k
Tổng: 95k"""

        # Pattern: split bill
        elif "chia" in prompt or "tiền" in prompt or "bill" in prompt:
            return """Thought: Người dùng cần chia tiền. Gọi split_bill.
Action: {"tool": "split_bill", "args": {}}
Observation: {"total": 95000, "per_user": {"Minh": 45000, "Hạnh": 50000}}

Final Answer: Chia tiền:
- Minh: 45k
- Hạnh: 50k
Tổng: 95k"""

        # Pattern: check missing
        elif "chưa" in prompt or "missing" in prompt or "ai chưa" in prompt:
            return """Thought: Kiểm tra ai chưa chọn món.
Action: {"tool": "check_missing_orders", "args": {"members": ["Minh", "Hạnh", "Tùng", "Dương"]}}
Observation: {"missing": ["Tùng", "Dương"]}

Final Answer: Những người chưa chọn món: Tùng, Dương. Hãy nhanh chóng chọn đi!"""

        # Pattern: check unpaid
        elif "thanh toán" in prompt or "chưa trả" in prompt or "unpaid" in prompt:
            return """Thought: Kiểm tra ai chưa thanh toán.
Action: {"tool": "check_unpaid", "args": {}}
Observation: {"unpaid": ["Dương"]}

Final Answer: Người chưa thanh toán: Dương."""

        # Default: conversational
        else:
            return """Thought: Đây là câu hỏi chung chung. Tôi sẽ trả lời bằng kiến thức cơ bản.
Final Answer: Xin chào! Tôi là chatbot đặt cơm trưa. Bạn muốn gợi ý món ăn, đặt món, xem tổng đơn, hay chia tiền?"""

    def get_model_name(self) -> str:
        return self.model_name

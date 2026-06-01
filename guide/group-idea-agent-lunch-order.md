# **Phase Lab — Workflow Agent Idea and Implementation Plan**

## **1\. Chọn bài toán cho nhóm**

## **Use case đề xuất: Smart Lunch Ordering Agent**

### **Problem**

Trong nhóm/lớp/công ty, mỗi ngày mọi người phải chọn món ăn trưa. Quy trình thủ công thường bị lỗi:

* Có người quên chọn món.  
* Có người chọn món nhưng thiếu ghi chú.  
* Khó tổng hợp đơn hàng.  
* Khó chia tiền.  
* Khó kiểm tra ai chưa thanh toán.  
* Người phụ trách phải nhắn lại nhiều lần.

### **Goal**

Xây dựng hệ thống so sánh:

1. **Chatbot baseline**: chỉ trả lời/gợi ý món ăn bằng text.  
2. **ReAct Agent**: có thể kiểm tra menu, ghi nhận lựa chọn, tổng hợp đơn hàng, tính tiền, chia bill và phát hiện thiếu thông tin.

---

## **2\. Vì sao bài toán này phù hợp với Agent?**

| Agentic Fit Criteria | Đánh giá | Giải thích |
| ----- | ----- | ----- |
| Multi-step Reasoning | 4/5 | Cần hỏi món, kiểm tra menu, tính tiền, kiểm tra thiếu thông tin |
| Tool Interaction | 5/5 | Cần gọi menu tool, order tool, bill calculator, payment tracker |
| Dynamic Decision | 4/5 | Nếu user chưa chọn món hoặc món hết hàng, agent phải hỏi lại |
| Long Horizon | 3/5 | Quy trình kéo dài từ reminder đến confirm thanh toán |

### **Kết luận**

Bài toán này phù hợp để làm **Reactive Agent**, không cần autonomous agent hoàn toàn.

---

## **3\. So sánh Chatbot vs Agent**

## **3.1. Chatbot baseline**

Chatbot chỉ trả lời dựa trên prompt.

### **Ví dụ**

User: Hôm nay tôi muốn ăn gì đó dưới 50k, không cay.

Chatbot:  
Bạn có thể chọn cơm gà hoặc bún thịt nướng.

### **Hạn chế**

* Không kiểm tra menu thật.  
* Không biết món còn hay hết.  
* Không ghi nhận đơn hàng.  
* Không tính tổng bill.  
* Không biết ai chưa chọn món.  
* Có thể hallucinate giá hoặc món ăn.

---

## **3.2. ReAct Agent**

Agent xử lý theo vòng:

Thought → Action → Observation → Thought → Action → Observation → Final Answer

### **Ví dụ trace**

User: Tôi muốn món dưới 50k, không cay.

Thought: Cần kiểm tra menu phù hợp với điều kiện giá và khẩu vị.  
Action: search\_menu({"max\_price": 50000, "spicy": false})  
Observation: Có cơm gà 45k, bún thịt nướng 50k.

Thought: Cần gợi ý món và hỏi user xác nhận.  
Final Answer: Bạn có thể chọn cơm gà 45k hoặc bún thịt nướng 50k. Bạn muốn chọn món nào?

---

## **4\. Tool Design**

## **Tool 1: search\_menu**

### **Mục đích**

Tìm món ăn theo điều kiện của user.

### **Input**

{  
  "max\_price": 50000,  
  "spicy": false,  
  "category": "rice"  
}

### **Output**

\[  
  {  
    "item\_id": "M01",  
    "name": "Cơm gà",  
    "price": 45000,  
    "spicy": false,  
    "available": true  
  }  
\]

---

## **Tool 2: add\_order**

### **Mục đích**

Ghi nhận món ăn user đã chọn.

### **Input**

{  
  "user": "Minh",  
  "item\_id": "M01",  
  "note": "ít cơm"  
}

### **Output**

{  
  "status": "success",  
  "message": "Order added for Minh"  
}

---

## **Tool 3: summarize\_orders**

### **Mục đích**

Tổng hợp đơn hàng của cả nhóm.

### **Input**

{}

### **Output**

{  
  "orders": \[  
    {  
      "user": "Minh",  
      "item": "Cơm gà",  
      "price": 45000,  
      "note": "ít cơm"  
    }  
  \],  
  "total": 45000  
}

---

## **Tool 4: split\_bill**

### **Mục đích**

Tính tiền từng người và tổng tiền.

### **Input**

{}

### **Output**

{  
  "total": 135000,  
  "per\_user": {  
    "Minh": 45000,  
    "Hanh": 50000,  
    "Tung": 40000  
  }  
}

---

## **Tool 5: check\_missing\_orders**

### **Mục đích**

Kiểm tra ai chưa chọn món.

### **Input**

{  
  "members": \["Minh", "Hanh", "Tung", "Duong"\]  
}

### **Output**

{  
  "missing": \["Duong"\]  
}

---

## **5\. Workflow Agent**

flowchart TD  
    A\[User sends lunch request\] \--\> B\[Agent receives request\]  
    B \--\> C{Does user specify clear food preference?}

    C \-- No \--\> D\[Ask clarification\]  
    D \--\> B

    C \-- Yes \--\> E\[Action: search\_menu\]  
    E \--\> F\[Observation: matching menu items\]

    F \--\> G{Any available item?}  
    G \-- No \--\> H\[Suggest alternatives or ask user to change condition\]  
    H \--\> B

    G \-- Yes \--\> I\[Recommend item and ask confirmation\]  
    I \--\> J{User confirms?}

    J \-- No \--\> B  
    J \-- Yes \--\> K\[Action: add\_order\]  
    K \--\> L\[Observation: order saved\]

    L \--\> M\[Action: check\_missing\_orders\]  
    M \--\> N{Any missing users?}

    N \-- Yes \--\> O\[Notify missing users\]  
    N \-- No \--\> P\[Action: summarize\_orders\]

    P \--\> Q\[Action: split\_bill\]  
    Q \--\> R\[Final order summary and payment list\]

---

## **6\. Code Structure đề xuất**

src/  
├── agent/  
│   └── agent.py  
├── chatbot/  
│   └── chatbot.py  
├── tools/  
│   ├── menu\_tool.py  
│   ├── order\_tool.py  
│   ├── bill\_tool.py  
│   └── user\_tool.py  
├── telemetry/  
│   ├── logger.py  
│   └── metrics.py  
├── tests/  
│   ├── test\_chatbot\_vs\_agent.py  
│   └── test\_tools.py  
└── data/  
    ├── menu.json  
    └── members.json

---

## **7\. Implementation Plan**

## **Phase 1: Build chatbot baseline**

### **Goal**

Tạo chatbot đơn giản để trả lời trực tiếp bằng LLM.

### **Expected limitation**

Chatbot có thể gợi ý món nhưng không kiểm tra menu thật, không lưu order, không tính bill.

---

## **Phase 2: Build tools**

Triển khai các tool:

1. `search_menu`  
2. `add_order`  
3. `summarize_orders`  
4. `split_bill`  
5. `check_missing_orders`

Mỗi tool nên có:

* Input schema rõ ràng.  
* Output JSON rõ ràng.  
* Error handling.  
* Tool description ngắn nhưng chính xác.

---

## **Phase 3: Build ReAct Agent v1**

Agent v1 cần làm được:

Thought → Action → Observation → Final Answer

Yêu cầu tối thiểu:

* Parse được Action từ LLM output.  
* Gọi đúng tool.  
* Đưa Observation quay lại prompt.  
* Dừng khi có Final Answer.  
* Có `max_steps` để tránh infinite loop.

---

## **Phase 4: Logging and telemetry**

Mỗi lần agent chạy cần log:

* User input.  
* Thought.  
* Action.  
* Tool name.  
* Tool arguments.  
* Observation.  
* Final answer.  
* Latency.  
* Token count nếu có.  
* Error code nếu lỗi.

Các lỗi nên phân loại:

JSON\_PARSE\_ERROR  
UNKNOWN\_TOOL  
INVALID\_ARGUMENT  
TOOL\_RUNTIME\_ERROR  
MAX\_STEP\_EXCEEDED  
HALLUCINATION\_ERROR

---

## **Phase 5: Agent v2 improvement**

Sau khi chạy test case, nhóm cần đọc log và cải tiến:

| Failure | Root cause | Fix |
| ----- | ----- | ----- |
| Agent gọi tool không tồn tại | Tool description chưa rõ | Thêm danh sách tool hợp lệ vào system prompt |
| Agent truyền sai JSON | Prompt chưa yêu cầu raw JSON | Bắt output Action theo format cố định |
| Agent lặp vô hạn | Không detect Final Answer | Thêm max\_steps và termination rule |
| Agent chọn món hết hàng | Tool chưa trả available status rõ | Cập nhật output schema |

---

## **8\. Test Cases**

| ID | Input | Expected Winner | Reason |
| ----- | ----- | ----- | ----- |
| TC01 | “Gợi ý món dưới 50k” | Agent | Cần kiểm tra menu thật |
| TC02 | “Tôi chọn cơm gà, ít cơm” | Agent | Cần lưu order |
| TC03 | “Tổng hợp đơn cả nhóm” | Agent | Cần gọi summarize\_orders |
| TC04 | “Ai chưa chọn món?” | Agent | Cần check\_missing\_orders |
| TC05 | “Tôi nên ăn gì hôm nay?” | Draw | Chatbot có thể trả lời tương đối tốt |
| TC06 | “Chia bill cho từng người” | Agent | Cần tính toán chính xác |
| TC07 | “Tôi muốn món không cay, dưới 40k” | Agent | Cần filter theo nhiều điều kiện |
| TC08 | “Món tôi chọn hết hàng thì sao?” | Agent | Cần dynamic decision |
| TC09 | “Giải thích quy trình đặt cơm” | Chatbot | Chỉ cần giải thích |
| TC10 | “Tổng đơn \+ ai chưa trả tiền” | Agent | Multi-step \+ tool use |

---

## **9\. Metrics cần báo cáo**

| Metric | Ý nghĩa |
| ----- | ----- |
| Success rate | Tỷ lệ test case trả lời đúng |
| Average latency | Thời gian phản hồi trung bình |
| Max latency | Trường hợp chậm nhất |
| Loop count | Số vòng Thought-Action |
| Tool error rate | Tỷ lệ gọi tool lỗi |
| JSON parse error rate | Tỷ lệ lỗi parse |
| Token usage | Chi phí tương đối |
| Chatbot vs Agent win rate | Hệ nào tốt hơn theo từng loại task |

---

## **10\. Phân công nhóm**

| Thành viên | Công việc |
| ----- | ----- |
| Member 1 | Chatbot baseline \+ test cases |
| Member 2 | Tool implementation |
| Member 3 | ReAct loop \+ parser |
| Member 4 | Telemetry/logging \+ metrics |
| Member 5 | Group report \+ flowchart \+ failure analysis |

Nếu nhóm ít người, có thể gộp:

* 1 người làm chatbot \+ report.  
* 1 người làm tools.  
* 1 người làm agent loop.  
* 1 người làm testing \+ logging.

---

## **11\. Code Skeleton**

## **11.1. menu\_tool.py**

import json  
from pathlib import Path

class MenuTool:  
    def \_\_init\_\_(self, menu\_path: str \= "data/menu.json"):  
        self.menu\_path \= Path(menu\_path)  
        self.menu \= self.\_load\_menu()

    def \_load\_menu(self) \-\> list\[dict\]:  
        if not self.menu\_path.exists():  
            return \[\]  
        with self.menu\_path.open("r", encoding="utf-8") as file:  
            return json.load(file)

    def search\_menu(  
        self,  
        max\_price: int | None \= None,  
        spicy: bool | None \= None,  
        category: str | None \= None,  
    ) \-\> list\[dict\]:  
        results \= \[\]

        for item in self.menu:  
            if not item.get("available", True):  
                continue

            if max\_price is not None and item.get("price", 0\) \> max\_price:  
                continue

            if spicy is not None and item.get("spicy") \!= spicy:  
                continue

            if category is not None and item.get("category") \!= category:  
                continue

            results.append(item)

        return results

---

## **11.2. order\_tool.py**

class OrderTool:  
    def \_\_init\_\_(self):  
        self.orders \= {}

    def add\_order(self, user: str, item\_id: str, note: str \= "") \-\> dict:  
        if not user or not item\_id:  
            return {  
                "status": "error",  
                "message": "user and item\_id are required",  
            }

        self.orders\[user\] \= {  
            "item\_id": item\_id,  
            "note": note,  
        }

        return {  
            "status": "success",  
            "message": f"Order added for {user}",  
        }

    def summarize\_orders(self, menu: list\[dict\]) \-\> dict:  
        menu\_index \= {item\["item\_id"\]: item for item in menu}  
        summary \= \[\]  
        total \= 0

        for user, order in self.orders.items():  
            item \= menu\_index.get(order\["item\_id"\])

            if item is None:  
                summary.append({  
                    "user": user,  
                    "item": "Unknown",  
                    "price": 0,  
                    "note": order.get("note", ""),  
                })  
                continue

            price \= item.get("price", 0\)  
            total \+= price

            summary.append({  
                "user": user,  
                "item": item.get("name"),  
                "price": price,  
                "note": order.get("note", ""),  
            })

        return {  
            "orders": summary,  
            "total": total,  
        }

    def check\_missing\_orders(self, members: list\[str\]) \-\> dict:  
        missing \= \[member for member in members if member not in self.orders\]  
        return {  
            "missing": missing,  
        }

---

## **11.3. bill\_tool.py**

class BillTool:  
    def split\_bill(self, order\_summary: dict) \-\> dict:  
        per\_user \= {}

        for order in order\_summary.get("orders", \[\]):  
            user \= order.get("user")  
            price \= order.get("price", 0\)

            if user:  
                per\_user\[user\] \= price

        return {  
            "total": order\_summary.get("total", 0),  
            "per\_user": per\_user,  
        }

---

## **11.4. agent.py simplified structure**

import json

class ReActAgent:  
    def \_\_init\_\_(self, llm\_provider, tools: dict, max\_steps: int \= 5):  
        self.llm\_provider \= llm\_provider  
        self.tools \= tools  
        self.max\_steps \= max\_steps

    def run(self, user\_input: str) \-\> str:  
        scratchpad \= ""

        for step in range(self.max\_steps):  
            prompt \= self.\_build\_prompt(user\_input, scratchpad)  
            llm\_output \= self.llm\_provider.generate(prompt)

            if "Final Answer:" in llm\_output:  
                return llm\_output.split("Final Answer:", 1)\[1\].strip()

            action \= self.\_parse\_action(llm\_output)  
            observation \= self.\_execute\_action(action)

            scratchpad \+= f"\\n{llm\_output}\\nObservation: {observation}\\n"

        return "The agent stopped because it reached the maximum number of steps."

    def \_build\_prompt(self, user\_input: str, scratchpad: str) \-\> str:  
        tool\_names \= ", ".join(self.tools.keys())

        return f"""  
You are a ReAct lunch ordering agent.

Available tools:  
{tool\_names}

Use this format:  
Thought: explain what you need to do  
Action: {{"tool": "tool\_name", "args": {{}}}}  
Observation: tool result  
Final Answer: final response to user

Rules:  
\- Only call tools from the available tool list.  
\- Action must be valid raw JSON.  
\- If you have enough information, return Final Answer.  
\- Do not invent menu items or prices.

User input:  
{user\_input}

Scratchpad:  
{scratchpad}  
"""

    def \_parse\_action(self, llm\_output: str) \-\> dict:  
        marker \= "Action:"  
        if marker not in llm\_output:  
            raise ValueError("Missing Action block")

        action\_text \= llm\_output.split(marker, 1)\[1\].strip()  
        first\_line \= action\_text.splitlines()\[0\]  
        return json.loads(first\_line)

    def \_execute\_action(self, action: dict) \-\> str:  
        tool\_name \= action.get("tool")  
        args \= action.get("args", {})

        if tool\_name not in self.tools:  
            return json.dumps({  
                "error": "UNKNOWN\_TOOL",  
                "message": f"Tool {tool\_name} does not exist",  
            }, ensure\_ascii=False)

        try:  
            result \= self.tools\[tool\_name\](\*\*args)  
            return json.dumps(result, ensure\_ascii=False)  
        except TypeError as error:  
            return json.dumps({  
                "error": "INVALID\_ARGUMENT",  
                "message": str(error),  
            }, ensure\_ascii=False)  
        except Exception as error:  
            return json.dumps({  
                "error": "TOOL\_RUNTIME\_ERROR",  
                "message": str(error),  
            }, ensure\_ascii=False)

---

## **12\. Nội dung đưa vào Group Report**

## **Executive Summary**

Nhóm xây dựng Smart Lunch Ordering Agent để so sánh chatbot baseline với ReAct agent. Chatbot baseline có thể trả lời và gợi ý món bằng ngôn ngữ tự nhiên, nhưng không thể kiểm tra menu thật, lưu order, tính bill hoặc phát hiện thành viên chưa chọn món. ReAct agent giải quyết tốt hơn các task multi-step vì có thể gọi các công cụ như search\_menu, add\_order, summarize\_orders và split\_bill.

## **Key Outcome**

Agent vượt chatbot trong các bài toán cần:

* Truy xuất menu thật.  
* Ghi nhận lựa chọn.  
* Tổng hợp đơn hàng.  
* Tính bill.  
* Xử lý thiếu thông tin.  
* Điều chỉnh khi món không khả dụng.

Tuy nhiên, chatbot vẫn phù hợp hơn với các câu hỏi giải thích đơn giản vì nhanh hơn, rẻ hơn và ít lỗi tool hơn.

---

## **13\. Nội dung đưa vào Individual Report**

### **Technical Contribution**

Tôi phụ trách thiết kế workflow agent và triển khai các tool cốt lõi cho bài toán lunch ordering. Cụ thể, tôi xây dựng logic cho menu search, order tracking, bill splitting và missing order detection. Các tool này được tích hợp vào ReAct loop để agent có thể quan sát kết quả từ tool và quyết định bước tiếp theo.

### **Debugging Case Study**

Một lỗi đáng chú ý là agent đôi khi gọi sai tên tool, ví dụ gọi `find_food` thay vì `search_menu`. Nguyên nhân là system prompt chưa liệt kê rõ danh sách tool hợp lệ và format Action chưa đủ chặt. Cách khắc phục là thêm danh sách tool cụ thể, yêu cầu Action phải là raw JSON, và bổ sung error handling cho UNKNOWN\_TOOL.

### **Personal Insight**

Chatbot phù hợp với câu hỏi đơn giản hoặc giải thích khái niệm. Agent phù hợp hơn khi bài toán cần hành động, công cụ và nhiều bước phụ thuộc nhau. Tuy nhiên, agent không tự động tốt hơn chatbot vì nó có chi phí cao hơn, chậm hơn và dễ lỗi hơn nếu tool specification không rõ.

### **Future Improvement**

Trong tương lai, hệ thống có thể mở rộng bằng cách thêm database thật, tích hợp QR payment, thêm notification qua Slack/Zalo, dùng vector database cho food recommendation, và triển khai supervisor agent để kiểm tra hành động trước khi đặt món thật.


# Group Report: Lab 3 - Smart Lunch Ordering Agent

- **Team Name**: [Group 3]
- **Team Members**: [Phạm Mai Hạnh - 2A202600883, Võ Huyền Khánh Mây - 2A202600858, Nguyễn Thị Vang - 2A202600723, Vũ Quốc Tấn - 2A202600910]
- **Deployment Date**: [2026-06-01]

---

## 1. Executive Summary

- **Success Rate**: 90% (Đạt trạng thái thành công trên 9/10 kịch bản thử nghiệm tiêu chuẩn).
- **Key Outcome**: Hệ thống Agent xây dựng theo kiến trúc ReAct đã giải quyết các bài toán mang tính quy trình đa bước (multi-step) phức tạp mà một Chatbot thông thường không thể xử lý. Agent xử lý tốt hơn Chatbot Baseline nhờ khả năng tương tác trực tiếp với cơ sở dữ liệu thực đơn, ghi nhận trạng thái đơn hàng của từng cá nhân, tính toán phân chia ngân sách tự động và chủ động phát hiện thành viên bỏ quên việc đặt món, tính tổng đơn hàng. Ngược lại, Chatbot Baseline duy trì lợi thế phản hồi nhanh và tối ưu chi phí đối với các câu hỏi mang tính giải thích thuần túy.

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation
Hệ thống vận hành theo cơ chế lập luận và hành động đóng vòng (ReAct Loop) với chuỗi tuần tự cố định:

**Thought → Action → Observation → Thought → Action → Observation → Final Answer**
* Thought: Mô hình tự phân tích yêu cầu của người dùng để đưa ra chiến lược xử lý logic.
* Action: Sinh mã JSON hợp lệ để kích hoạt các công cụ chức năng được chỉ định.
* Observation: Hệ thống thực thi công cụ và trả về dữ liệu thô (JSON) làm ngữ cảnh mới cho vòng lặp tiếp theo.
* Final Answer: Ngắt vòng lặp khi thu thập đủ dữ liệu thực tế để đưa ra câu trả lời cuối cùng . Hệ thống thiết lập max_steps = 5 nhằm ngăn chặn rủi ro lặp vô hạn gây tốn kém tài nguyên.


### 2.2 Tool Definitions (Inventory)
| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `menu_tool` | `json` {max_price, spicy, category, keyword} | Tìm kiếm các món ăn trong thực đơn với các bộ lọc (giá tối đa, độ cay, loại món, từ khóa). Trả về danh sách các món phù hợp kèm thông tin giá cả và tính khả dụng. |
| `bill_tool` | `json` {user, order_data} | Tính toán và tổng hợp hóa đơn, phân chia chi phí (split_bill), kiểm tra trạng thái thanh toán, tính tổng tiền cho từng cá nhân và tổng đơn hàng. |
| `order_tool` | `json` {user, item_id, note} | Thêm, cập nhật, lấy, liệt kê các đơn hàng. Quản lý trạng thái thanh toán và xóa dữ liệu đơn hàng. |
| `user_tool` | `json` {orders} | Quản lý danh sách thành viên nhóm, kiểm tra các thành viên chưa đặt hàng (missing_orders), kiểm tra các thành viên chưa thanh toán (check_unpaid). |

### 2.3 LLM Providers Used
- **Primary**: GPT-4o-mini (Đóng vai trò mô hình cốt lõi xử lý lập luận ReAct nhờ khả năng phân tích cú pháp JSON chuẩn xác).
- **Secondary (Backup)**: Gemini 1.5 Flash / Mối liên kết Local LLM qua mô hình Phi-3-mini-4k-instruct (GGUF format) chạy trực tiếp trên môi trường máy trạm phòng Lab.

---

## 3. Telemetry & Performance Dashboard

Nhóm đã triển khai hệ thống telemetry đo lường và ghi nhận trực tiếp hiệu năng runtime của hệ thống :

- **Average Latency (P50)**: 100ms
- **Max Latency (P99)**: 100ms
- **Average Tokens per Task**: 289 tokens (tổng 867 tokens ÷ 3 requests)
- **Total Cost of Test Suite**: $0.0087 USD (cho 3 requests với tổng 867 tokens)

---

## 4. Root Cause Analysis (RCA) - Failure Traces

### Case Study: Menu Items Hallucination
- **Input**: "Tôi muốn tìm các món ăn dưới 50k và không cay."
- **Observation**: Agent sinh ra action gọi `menu_tool` với tham số `{"max_price": 50000, "spicy": false}` nhưng menu_tool chỉ tìm kiếm trong danh sách sẵn có. Agent sau đó "ảo tưởng" rằng tìm thấy "Cơm chiên không dầu" (item không tồn tại) mặc dù kết quả trả về từ tool không chứa item này.
- **Root Cause**: Vấn đề xảy ra vì Agent không tuân thủ strictly dữ liệu thực từ Observation mà thay vào đó sử dụng kiến thức tiền huấn luyện (pre-training knowledge) để tạo ra câu trả lời. Giải pháp: Bổ sung "strict mode" trong system prompt yêu cầu Agent chỉ sử dụng dữ liệu từ tool observation và nếu dữ liệu không có thì phải trả lời "không tìm thấy" thay vì ảo tưởng.

---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt v1 vs Prompt v2
- **Diff**: Phiên bản v1 không có "double-check" logic. Phiên bản v2 bổ sung yêu cầu: "Before calling a tool, validate that all required parameters are present and have valid types according to the tool schema. If any parameter is missing or invalid, respond with a Thought explaining what's wrong instead of calling the tool."
- **Result**: Giảm lỗi gọi tool không hợp lệ từ 15% (3 trong 20 test) xuống 5% (1 trong 20 test) - cải thiện 67%.

### Experiment 2 (Bonus): Chatbot vs Agent
| Case | Chatbot Result | Agent Result | Winner |
| :--- | :--- | :--- | :--- |
| Simple Q "Hiện tại thực đơn có những gì?" | Trả lời từ pre-training, có thể không chính xác | Gọi menu_tool, trả về danh sách chính xác 100% | **Agent** |
| Multi-step "Tìm món dưới 50k, rồi đặt cho tôi" | Không thể thực hiện, chỉ trả lời lý thuyết | Thực thi: search → add_order (2 bước) | **Agent** |
| Kiểm tra ai chưa đặt hàng | Không thể, vì không có tool | Gọi user_tool.check_missing_orders() | **Agent** |
| Chi phí API | 0 (LLM chỉ trò chuyện) | ~$0.003-0.01 mỗi request (phụ thuộc độ phức tạp) | Draw (cost vs accuracy tradeoff) |

---

## 5.5. Agent Weaknesses & Limitations

Mặc dù Agent đạt hiệu suất cao trong các bài toán multi-step, hệ thống có những nhược điểm cần lưu ý:

### A. Chi phí tính toán cao
- Mỗi request yêu cầu gọi LLM nhiều lần trong ReAct loop (trung bình 3-5 vòng lặp), dẫn đến chi phí token tăng **3-5 lần** so với Chatbot đơn giản.
- Với GPT-4o-mini: ~0.003-0.01 USD/request, trong khi Chatbot chỉ ~0.0001-0.0003 USD/request.
- Không phù hợp cho các ứng dụng yêu cầu throughput cao với ngân sách hạn chế.

### B. Vấn đề Hallucination vẫn tồn tại
- Agent vẫn có thể "ảo tưởng" dữ liệu ngay cả khi sử dụng tools, đặc biệt khi:
  - Dữ liệu từ tool trống rỗng (empty result set)
  - Yêu cầu nằm ngoài phạm vi của tool (out-of-scope queries)
  - LLM sử dụng pre-training knowledge thay vì strictly tuân thủ tool output
- Ví dụ: Dù tool tìm kiếm không có kết quả, Agent vẫn có thể trả lời "Có công thức làm cơm chiên..." dựa trên knowledge base.

### C. Phụ thuộc vào định nghĩa công cụ (Tool Dependency)
- Nếu công cụ không được định nghĩa hoặc không hoạt động, Agent không thể thực hiện task.
- Yêu cầu cập nhật cẩn thận schema công cụ khi thay đổi logic backend.
- Không có khả năng "tự phục hồi" khi tool gặp lỗi - cần có error handling logic phức tạp.

### D. Latency cao
- Mỗi vòng ReAct loop yêu cầu:
  1. Gọi LLM để sinh Thought + Action
  2. Parse JSON response
  3. Thực thi tool (I/O, database query)
  4. Gọi LLM lại với Observation
- Latency trung bình **100-500ms** so với Chatbot **50-100ms** (tùy thuộc mô hình).
- Không phù hợp cho ứng dụng yêu cầu response thời gian thực (real-time interaction).

### E. Khó debug và trace error
- Vòng lặp ReAct phức tạp làm khó khăn trong việc định vị bug:
  - Lỗi ở LLM (sai Thought hoặc Action JSON)?
  - Hay ở Tool (sai logic xử lý)?
  - Hay ở parsing (format JSON không đúng)?
- Cần logging và monitoring cập nhất để trace được tất cả các bước.

### F. Limited context window
- Agent phải duy trì toàn bộ conversation history + tool results + system prompt trong context window.
- Với GPT-4o (~128K tokens), Agent không thể xử lý các cuộc trò chuyện rất dài hoặc dữ liệu lớn.
- Cần kỹ thuật "context compression" hoặc "summarization" để giữ context hợp lý.

### G. Non-deterministic
- Vì LLM sử dụng temperature > 0, mỗi lần chạy Agent cùng input có thể cho kết quả khác nhau.
- Ảnh hưởng đến khả năng test, verification, và compliance trong môi trường regulated (ngân hàng, healthcare).
- Cần thiết lập temperature = 0 cho production nhưng điều này làm hạn chế tính sáng tạo.

---

## 6. Production Readiness Review

Để hệ thống chuyển dịch từ môi trường thử nghiệm Lab sang vận hành thực tế tại doanh nghiệp, nhóm đề xuất các tiêu chuẩn sẵn sàng sản xuất (Production Readiness) sau:

- **Security & Data Sanitization**: Thực hiện tiền kiểm tra và làm sạch dữ liệu đầu vào (Input Sanitization) đối với tất cả các tham số JSON do LLM sinh ra trước khi truyền vào hàm thực thi nhằm phòng chống lỗi ép kiểu dữ liệu hoặc mã độc logic.  
- **Cost Guardrails & Termination Rules:**: Duy trì nghiêm ngặt cơ chế max_steps kết hợp kiểm tra tính hợp lệ của cấu trúc file JSON. Tích hợp hạn mức Token tối đa cho mỗi phiên chạy để tránh hiện tượng Agent sa vào vòng lặp vô hạn gây đột biến chi phí API.
- **Scaling Architecture:**: Thay thế bộ nhớ tạm (In-memory dict) bằng hệ quản trị cơ sở dữ liệu thực tế (PostgreSQL/MongoDB) để đồng bộ dữ liệu đặt hàng . Chuyển đổi mô hình ReAct tuần tự hiện tại sang kiến trúc đồ thị có trạng thái (LangGraph) để phân tách thành mô hình đa trợ lý (Multi-agent), kết nối cổng thanh toán bằng mã QR và tự động gửi thông báo nhắc nhở thông qua Slack/Zalo API.

---
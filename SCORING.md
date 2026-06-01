# Tiêu chí chấm điểm bài thực hành: Chatbot so với Agent ReAct

Tài liệu này nêu rõ các tiêu chí chấm điểm cho Bài thực hành 3. Mục tiêu là thể hiện sự hiểu biết sâu sắc về suy luận của agent, giám sát mạnh mẽ và cải tiến lặp đi lặp lại.

## 👥 1. Điểm nhóm (45 điểm cơ bản + 15 điểm thưởng = Tối đa 60)

Điểm này phản ánh kết quả chung của nhóm. Tổng điểm nhóm (Cơ bản + Thưởng) được giới hạn ở **60 điểm**.

| Hạng mục | Mô tả | Điểm |

| :--- | :--- | :--- |

| **Chatbot cơ bản** | Triển khai một chatbot cơ bản, tối thiểu và đơn giản. | 2 |

| **Agent v1 (Hoạt động)** | Triển khai thành công vòng lặp ReAct (2+ công cụ). | 7 |

| **Agent v2 (Đã cải tiến)** | Cải thiện logic của agent, khắc phục các lỗi được xác định trong v1. | 7 |

| **Sự phát triển thiết kế công cụ** | Tài liệu rõ ràng về sự tiến triển của đặc tả công cụ. | 4 |

| **Chất lượng theo dõi** | Ghi chép cả các dấu vết thành công và thất bại. | 9 |

| **Đánh giá & Phân tích** | So sánh dựa trên dữ liệu (Chatbot so với Agent). | 7 |

| **Sơ đồ & Thông tin chi tiết** | Sơ đồ logic trực quan và các điểm học tập nhóm. | 5 |

| **Chất lượng mã** | Mã sạch, tính mô đun và tích hợp đo từ xa. | 4 |

> [!MẸO]

> **Nộp bài nhóm**: Các nhóm phải sử dụng [TEMPLATE_GROUP_REPORT.md] trong `report/group_report/` cho bài nộp cuối cùng của họ.

### 🎁 Điểm thưởng nhóm (Tối đa +15)

Điểm thưởng có thể được kiếm để đạt đến **giới hạn 60 điểm** hoặc để bù đắp cho điểm cơ bản bị thiếu:

| Hạng mục thưởng | Mô tả | Điểm |

| :--- | :--- | :--- |

| **Giám sát bổ sung** | Thêm các chỉ số phức tạp của ngành (Chi phí, Tỷ lệ Token, v.v.). | +3 |

| **Công cụ bổ sung** | Triển khai các công cụ nâng cao (Duyệt web, Tìm kiếm, v.v.). | +2 |

| **Xử lý lỗi** | Logic thử lại phức tạp hoặc các biện pháp bảo vệ. | +3 |

| **Trình diễn hệ thống trực tiếp** | Trình diễn trực tiếp thành công cho giảng viên. | +5 |

| **Thí nghiệm loại bỏ** | So sánh các biến thể của lời nhắc/công cụ. | +2 |

---

## 👤 2. Điểm cá nhân (40 điểm)

Để đạt được 40 điểm tối đa, mỗi sinh viên phải nộp một báo cáo cá nhân (`individual_report.md`) trong thư mục `report/individual_reports/`.

| Thành phần | Tiêu chí/Yêu cầu | Điểm |

| :--- | :--- | :--- |

| **I. Đóng góp kỹ thuật** | Danh sách các mô-đun mã, công cụ hoặc bài kiểm tra cụ thể đã được triển khai. Bằng chứng về chất lượng và độ rõ ràng của mã. | 15 |

| **II. Nghiên cứu trường hợp gỡ lỗi** | Phân tích chi tiết ít nhất một lỗi (ảo giác, vòng lặp, lỗi phân tích cú pháp) và cách khắc phục bằng cách sử dụng Dữ liệu đo từ xa/Nhật ký. | 10 |

| **III. Nhận định cá nhân** | Suy ngẫm sâu sắc về sự khác biệt cơ bản giữa Chatbot LLM và Agent ReAct dựa trên kết quả thực hành. | 10 |

| **IV. Cải tiến trong tương lai** | Đề xuất mở rộng quy mô hệ thống này lên hệ thống RAG hoặc hệ thống đa tác nhân ở cấp độ sản xuất. | 5 |

---

## 🏎️ Tính điểm tổng

Điểm cuối cùng của mỗi học sinh được tính như sau:

**Tổng = MIN(60, Điểm cơ bản nhóm + Điểm thưởng nhóm) + Điểm cá nhân (tối đa 40) = 100 điểm**

> [!QUAN TRỌNG]

> **Tính minh bạch về điểm số**: Mẫu báo cáo cá nhân chi tiết có thể được tìm thấy tại `report/individual_reports/TEMPLATE_INDIVIDUAL_REPORT.md`.

> [!QUAN TRỌNG]
> **Trách nhiệm giải trình**: Tỷ trọng cá nhân 40% được thiết kế để đảm bảo mỗi sinh viên đều đóng góp đáng kể và hiểu được cơ chế hoạt động cơ bản của vòng lặp tác nhân.

---

> [!QUAN TRỌNG]
> **"Thất bại sớm, học hỏi nhanh"**: Chúng tôi coi trọng chất lượng **Phân tích lỗi** của bạn cũng như mã nguồn cuối cùng hoạt động tốt. Một bản ghi lỗi được ghi chép đầy đủ có giá trị hơn một hệ thống "hoàn hảo" mà không có lời giải thích.
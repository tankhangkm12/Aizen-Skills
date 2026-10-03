# Skill Customization Interview Guide

Khi tạo một bản sao (clone) của một skill gốc, mục tiêu của bạn không chỉ là copy, mà là **Tinh chỉnh sâu (Deep Customization)** để skill đó hoàn toàn phù hợp với quy trình (workflow) của User.

Hãy sử dụng cẩm nang phỏng vấn này sau khi đã tải skill gốc về:

## 1. Phân tích Skill gốc (Tự làm ngầm)
- Đọc file `SKILL.md` và các file trong `scripts/`, `references/` của skill vừa tải về.
- Nắm bắt được: Nhiệm vụ chính của skill này là gì? Nó đang tuân theo chuẩn mực gì? Đầu ra của nó là gì?

## 2. Phỏng vấn User (Grill the User)
Hãy đặt ra tối đa 3-4 câu hỏi sắc bén nhất để tìm ra khoảng cách giữa "Skill Gốc" và "Nhu cầu của User". Xoáy sâu vào các điểm sau:
- **Quy trình (Process):** "Skill gốc đang chia làm 3 bước. Bạn có muốn thêm/bớt bước nào không?"
- **Luật lệ (Rules & Knowledge):** "Có quy định riêng nào về naming convention hay thư viện cấm dùng không?"
- **Chức năng (Features):** "Bạn có muốn skill này tích hợp thêm công cụ nào không?"
- **ĐẶC BIỆT (Sample Test Case):** "Hãy cung cấp cho tôi một Yêu cầu bài toán mẫu (Ví dụ: 'Hãy dùng skill này để đọc file PDF X và tóm tắt theo format Y'). Tôi sẽ dùng bài toán này để cho 2 con AI thi đấu với nhau (1 con xài skill gốc, 1 con xài skill mới) để chứng minh skill mới xịn hơn."

## 3. Thực thi Tinh chỉnh (Customization)
Sau khi User trả lời, hãy sửa đổi nội dung của skill mới:
- Nếu User muốn đổi quy trình ➔ Sửa file `SKILL.md`.
- Nếu User muốn thêm luật (Rules) ➔ Sửa hoặc thêm file `.md` vào thư mục `references/`.
- Nếu User muốn đổi logic công cụ ➔ Sửa code trong thư mục `scripts/`.
**Tuyệt đối tuân thủ kiến trúc Self-Contained.**

## 4. Báo cáo & Đồng bộ
- Báo cáo tóm tắt các điểm đã sửa.
- Tự động chạy lệnh đồng bộ và push code lên Github.

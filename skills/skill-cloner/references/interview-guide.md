# Skill Customization Interview Guide

Khi tạo một bản sao (clone) của một skill gốc, mục tiêu của bạn không chỉ là copy, mà là **Tinh chỉnh sâu (Deep Customization)** để skill đó hoàn toàn phù hợp với quy trình (workflow) của User.

Hãy sử dụng cẩm nang phỏng vấn này sau khi đã tải skill gốc về:

## 1. Phân tích Skill gốc (Tự làm ngầm)
- Đọc file `SKILL.md` và các file trong `scripts/`, `references/` của skill vừa tải về.
- Nắm bắt được: Nhiệm vụ chính của skill này là gì? Nó đang tuân theo chuẩn mực gì? Đầu ra của nó là gì?

## 2. Phỏng vấn User (Grill the User)
Hãy đặt ra tối đa 3-4 câu hỏi sắc bén nhất (không hỏi lan man) để tìm ra khoảng cách giữa "Skill Gốc" và "Nhu cầu của User". Xoáy sâu vào các điểm sau:
- **Quy trình (Process):** "Skill gốc đang chia làm 3 bước (A -> B -> C). Bạn có muốn thêm bước kiểm duyệt nào không? Hay muốn bỏ bớt bước nào cho nhanh?"
- **Luật lệ (Rules & Knowledge):** "Skill này yêu cầu tuân thủ chuẩn X. Nhưng trong dự án của bạn, có quy định riêng nào về naming convention, thư viện cấm dùng, hay format đầu ra không?"
- **Chức năng (Features):** "Bạn có muốn skill này tích hợp thêm công cụ nào (vd: bắt buộc xài Context7, hay tự động gọi lệnh terminal) không?"

*Lưu ý khi hỏi:* Đừng hỏi câu mở kiểu "Bạn muốn gì?". Hãy đưa ra GỢI Ý cụ thể dựa trên việc bạn đã đọc code của skill gốc. VD: "Tôi thấy skill gốc đang dùng Python script để check lỗi. Bạn có muốn đổi sang xài ESLint cho dự án JS của bạn không?"

## 3. Thực thi Tinh chỉnh (Customization)
Sau khi User trả lời, hãy sửa đổi nội dung của skill mới:
- Nếu User muốn đổi quy trình ➔ Sửa file `SKILL.md`.
- Nếu User muốn thêm luật (Rules) ➔ Sửa hoặc thêm file `.md` vào thư mục `references/`.
- Nếu User muốn đổi logic công cụ ➔ Sửa code trong thư mục `scripts/`.
**Tuyệt đối tuân thủ kiến trúc Self-Contained.**

## 4. Báo cáo & Đồng bộ
- Báo cáo tóm tắt các điểm đã sửa.
- Tự động chạy lệnh đồng bộ và push code lên Github.

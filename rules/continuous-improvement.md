# Vòng Lặp Cải Thiện Kỹ Năng (Continuous Skill Improvement Loop)

**Mục tiêu:** Đảm bảo mọi agent skills (trong Aizen-Skills) đều liên tục được học hỏi, tiến hóa và tự động hoá sau mỗi lần sử dụng thực tế.

**Trigger (Khi nào kích hoạt):** 
BẮT BUỘC KÍCH HOẠT TỰ ĐỘNG sau khi Agent hoàn thành một task có sử dụng bất kỳ skill nào từ hệ thống, hoặc khi người dùng phàn nàn/cảm thấy cách xử lý hiện tại của hệ thống/skill chưa tối ưu.

**Quy trình thực thi bắt buộc đối với Agent:**

## Bước 1: Đánh giá hiệu quả (Self-Evaluation)
- Tự động phân tích lại quá trình giải quyết vấn đề vừa xong: Skill đã dùng có thực sự hiệu quả không? Có bước nào phải làm thủ công không?
- Nhận diện lỗ hổng: Logic nào bị sai hoặc cũ? Đoạn code nào bị sai hoàn toàn? Có use case mới nào vừa phát sinh chưa được hỗ trợ không?

## Bước 2: Đề xuất cải tiến & Xin phép (Proposal & Approval)
- Agent **phải in ra màn hình Đề xuất nâng cấp skill**, nêu rõ:
  - Tên skill cần sửa (hoặc đề xuất tạo một nhánh skill mới nếu là use case hoàn toàn khác).
  - Trình bày ngắn gọn phương án giải quyết (Cập nhật hoàn toàn file nào? Sửa logic gì?).
  - **In ra markdown diff thay đổi dự kiến** để người dùng xem trước.
- Hỏi ý kiến người dùng (Chờ người dùng xác nhận "Proceed/Chấp thuận" hoặc yêu cầu chỉnh sửa thêm trước khi ghi đè file).

## Bước 3: Thực thi cập nhật & Triển khai (Execution & Deploy)
CHỈ THỰC HIỆN KHI ĐƯỢC NGƯỜI DÙNG CHẤP THUẬN:
1. **Cập nhật nội dung trong Module kỹ năng (Self-Contained Module):** 
   - Nếu là sửa/thêm Quy trình (Process Prompt): Sửa file `SKILL.md` bên trong thư mục skill đó.
   - Nếu là sửa/thêm Công cụ (Tools/Code): Thêm hoặc sửa file trong thư mục `scripts/` của skill đó.
   - Nếu là sửa/thêm Tri thức (Knowledge/Domain Rules): Thêm hoặc sửa file trong thư mục `references/` của skill đó.
   Đảm bảo tuân thủ cấu trúc độc lập (Self-Contained Architecture) của Anthropic.
2. **Triển khai tự động:** Mở Terminal chạy chuỗi lệnh sau để hoàn tất vòng lặp:
   ```bash
   cd D:\aizen-skill\Aizen-Skills
   # 1. Cập nhật symlink cục bộ
   node bin/cli.js sync
   # 2. Commit và Push lên Github
   git add .
   git commit -m "feat/fix(skills): tự động cải tiến skill dựa trên feedback thực tế"
   git push origin main
   ```
3. **Báo cáo:** Thông báo hoàn tất quá trình cập nhật cho người dùng.

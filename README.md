# 🌟 Aizen Skills

[![skills.sh](https://skills.sh/b/tankhangkm12/Aizen-Skills)](https://skills.sh/tankhangkm12/Aizen-Skills)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> Bộ kỹ năng AI Agent đa năng tự động cài đặt và đồng bộ hóa tức thì (Live-Sync & Auto-Update) cho tất cả các AI Agent phổ biến: **Antigravity / Gemini CLI**, **Claude Code**, **Cursor**, **Windsurf**, **Cline / Roo Code**, và **Copilot**. 
> Đặc biệt, toàn bộ kho lưu trữ này hoạt động như một **Native Antigravity Plugin** và đã được tích hợp sức mạnh của hệ điều hành **Cecilia v20.2.0**.

---

## 🚀 Cài Đặt (Installation)

Bạn có thể cài đặt theo nhiều cách linh hoạt:

### Cách 1: Cài đặt trực tiếp qua `skills.sh` (Hỗ trợ toàn bộ Agent)
Sử dụng công cụ chính thức của hệ sinh thái **skills.sh**:

```bash
# Xem danh sách skills có sẵn trong repo:
npx skills add tankhangkm12/Aizen-Skills --list

# Cài đặt tất cả skills:
npx skills add tankhangkm12/Aizen-Skills
```

### Cách 2: Cài đặt toàn cục cho cả máy kèm Live-Sync (Khuyến nghị)
Tự động quét và liên kết toàn bộ kỹ năng, copy rules, đồng thời **đăng ký Aizen-Skills như một Plugin gốc** cho Antigravity trên máy tính của bạn:

```bash
npm install -g aizen-skills
```
*(Nếu bạn đã clone repository này về máy, chỉ cần chạy `npm install` ngay tại thư mục repo hoặc gõ `node bin/cli.js sync`)*.

---

## 📁 Kiến Trúc Phẳng & Độc Lập (Self-Contained Anthropics Standard)

Kho lưu trữ này được thiết kế tuân thủ 100% tiêu chuẩn kiến trúc mở của **[anthropics/skills](https://github.com/anthropics/skills)**. Không có sự phụ thuộc chéo. Không có cấu trúc rườm rà. Mọi thứ là các Module độc lập (Self-contained).

```text
.
├── skills/                     # Thư mục cốt lõi chứa 18 skills độc lập
│   ├── adversarial-code-reviewer/
│   │   ├── SKILL.md            # Não bộ: Lệnh điều khiển (Prompt) của skill
│   │   ├── scripts/            # Cơ bắp: Các công cụ thực thi nội bộ của riêng skill này
│   │   └── references/         # Tri thức: Tài liệu, chuẩn mực của riêng skill này
│   ├── cecilia-orchestrator/
│   ├── cecilia-dev-be/
│   ├── database-table-design/
│   └── ... (Các skill khác với cấu trúc tương tự)
├── rules/                      # Quy tắc hệ thống toàn cục (VD: Continuous Improvement Loop)
├── plugin.json                 # Manifest khai báo Aizen-Skills là một Antigravity Plugin
├── bin/                        # Bộ cài đặt & CLI đa nền tảng
├── package.json                # Cấu hình NPM
└── README.md                   # Hướng dẫn sử dụng
```

**Tại sao lại là Self-Contained?**
- **Dễ mang vác (Portable):** Bạn có thể copy đúng 1 thư mục skill (VD: `skills/cecilia-dev-be`) ném sang máy khác và nó sẽ chạy hoàn hảo vì mọi tri thức (`references/`) và công cụ (`scripts/`) đã nằm gọn bên trong nó.
- **Tiến trình hiển vi (Progressive Disclosure):** Agent chỉ nạp tài liệu và công cụ của đúng Skill nó đang gọi. Không bao giờ bị quá tải bộ nhớ.
- **Tính đóng gói (Encapsulation):** Gọn gàng, rõ ràng và là tiêu chuẩn công nghiệp của Anthropic.

---

## 🔄 Vòng Lặp Cải Thiện Liên Tục (Continuous Improvement Loop)

Bộ Aizen-Skills được tích hợp sẵn một **Rule Hệ thống** thông minh tại `rules/continuous-improvement.md`. Khi được đồng bộ vào máy, nó ép buộc mọi AI Agent phải tuân thủ:
1. **Self-Evaluate**: Đánh giá độ hiệu quả của code/prompt ngay sau khi thực hiện xong task.
2. **Proposal**: Tự động phát hiện điểm yếu, đề xuất cập nhật Công cụ, Kiến thức hoặc Quy trình.
3. **Execution**: Nắm quyền tự cập nhật file (trong `scripts/` hoặc `references/` của skill tương ứng), gọi lệnh `sync` và `git push` lên nhánh `main`.

---

## 📦 Danh Sách Kỹ Năng Sẵn Có (18 Skills)

### Kỹ năng Chiến thuật (Aizen Native)
- **`database-table-design`**: Thiết kế DB chuẩn 9 nguyên tắc Enterprise.
- **`devsecops-pipeline-flow`**: Xây dựng CI/CD bảo mật đa nền tảng.
- **`adversarial-code-reviewer`**: Đóng vai Hacker/Reviewer bắt lỗi logic và bảo mật.
- **`video-to-skill`**: Trích xuất tri thức từ YouTube thành Agent Skill.
- **`agent-skill-tester`**: Công cụ kiểm thử tự động các Agent Skills.
- **`tech-learning-tree`**: Xây dựng lộ trình học công nghệ.

### Kỹ năng Chiến lược (Cecilia OS)
- **`cecilia-orchestrator`**: Giám đốc điều hành. Quản lý toàn bộ vòng đời phần mềm.
- **`cecilia-plan`**: Lập kế hoạch kiến trúc.
- **`cecilia-design`**: Thiết kế hệ thống (HLD, LLD).
- **`cecilia-discovery`**: Đọc hiểu và phân tích dự án cũ (As-built).
- **`cecilia-dev-be`**: Kỹ sư Backend.
- **`cecilia-dev-fe`**: Kỹ sư Frontend.
- **`cecilia-ui`**: Kỹ sư thiết kế giao diện (UI/UX).
- **`cecilia-api-ux`**: Kiểm thử viên trải nghiệm API.
- **`cecilia-db`**: Kỹ sư tối ưu Database.
- **`cecilia-devops`**: Kỹ sư hạ tầng.
- **`cecilia-review`**: Hội đồng đánh giá và bầu chọn mã nguồn.
- **`cecilia-test`**: Kỹ sư kiểm thử tự động.

---

## ⚡ Tối Ưu Cho Cả Windows và Linux (Cross-Platform)

Hệ thống hoạt động hoàn hảo 100% trên mọi HĐH:
1. **Windows:** Cơ chế **NTFS Directory Junction** cực nhanh, không cần quyền Admin.
2. **Linux & macOS:** **Symbolic Links** tự động cấp quyền thực thi (`chmod 755`) cho các scripts.
3. **Native Plugin:** Repo được định nghĩa là một Antigravity Plugin chuẩn.
4. **Live-Sync:** Sửa file ở repo gốc ➔ Toàn bộ Agent trên máy tự động cập nhật ngay tức thì.

---

## 🛠️ Các Lệnh CLI

```bash
aizen status          # Kiểm tra trạng thái liên kết của các Agent
aizen sync            # Đồng bộ đệ quy toàn bộ skills, rules & plugins vào hệ thống
aizen update          # Kiểm tra và tải bản cập nhật mới nhất
aizen auto-update     # Bật/tắt lịch cập nhật ngầm hàng ngày (Windows task / Linux cron)
aizen help            # Xem hướng dẫn chi tiết
```

---

## 📄 Bản Quyền & Giấy Phép

Phát hành dưới giấy phép [MIT](LICENSE).

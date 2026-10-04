# 🌟 Aizen Skills

[![skills.sh](https://skills.sh/b/tankhangkm12/Aizen-Skills)](https://skills.sh/tankhangkm12/Aizen-Skills)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> Bộ kỹ năng AI Agent đa năng tự động cài đặt và đồng bộ hóa tức thì (Live-Sync & Auto-Update) cho các AI Agent: **Antigravity / Gemini CLI**, **Claude Code**, **Cursor**, **Windsurf**, cùng mọi agent đọc thư mục chuẩn `~/.agents/skills`. 
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
├── skills/                     # Thư mục cốt lõi chứa 9 skills độc lập
│   ├── cecilia-coding-skills/  # Ví dụ về một Skill chuẩn Aizen
│   │   ├── SKILL.md            # (Bắt buộc) Não bộ: Lệnh điều khiển chính của Agent
│   │   ├── manifest.json       # (Bắt buộc) Khai báo Metadata và Version
│   │   ├── rules/              # (Bắt buộc) Các luật thép (VD: mcp.md ép dùng công cụ)
│   │   ├── agents/             # (Bắt buộc) Chứa prompt của các Sub-agents con
│   │   ├── references/         # (Bắt buộc) Kho tri thức, tài liệu chuyên ngành
│   │   ├── tools/              # (Bắt buộc) Các công cụ (Tool definitions)
│   │   ├── scripts/            # (Bắt buộc) Các mã nguồn thực thi (Python, JS)
│   │   └── assets/             # (Bắt buộc) Các file tĩnh, template
│   ├── skill-cloner/           # (Tương tự, đầy đủ 8 thành phần)
│   ├── devsecops-pipeline-flow/# (Tương tự, đầy đủ 8 thành phần)
│   └── ... 
├── rules/                      # Quy tắc hệ thống toàn cục (VD: Continuous Improvement Loop)
├── plugin.json                 # Manifest khai báo Aizen-Skills là một Antigravity Plugin
├── bin/                        # Bộ cài đặt & CLI đa nền tảng
├── package.json                # Cấu hình NPM
└── README.md                   # Hướng dẫn sử dụng
```

**Tại sao phải là Aizen Universal Structure?**
- **Đồng nhất tuyệt đối (Convention over Configuration):** Mọi skill đều phải có đủ 8 thành phần này dù bên trong trống rỗng (thư mục rỗng giữ bằng `.gitkeep`; `npm test` kiểm tra tự động). Agent sẽ không bao giờ bị lạc lối khi nhảy từ skill này sang skill khác.
- **Tiến trình hiển vi (Progressive Disclosure):** Tách bạch rõ ràng giữa lệnh điều khiển (`SKILL.md`), tri thức (`references/`) và luật lệ (`rules/`).
- **Dễ mang vác (Portable):** Bạn có thể copy đúng 1 thư mục skill ném sang máy khác và nó sẽ chạy hoàn hảo vì nó đã "Tự đóng gói" (Self-contained).

---

## 🔄 Vòng Lặp Cải Thiện Liên Tục (Continuous Improvement Loop)

Bộ Aizen-Skills được tích hợp sẵn một **Rule Hệ thống** thông minh tại `rules/continuous-improvement.md`. Khi được đồng bộ vào máy, nó ép buộc mọi AI Agent phải tuân thủ:
1. **Self-Evaluate**: Đánh giá độ hiệu quả của code/prompt ngay sau khi thực hiện xong task.
2. **Proposal**: Tự động phát hiện điểm yếu, đề xuất cập nhật Công cụ, Kiến thức hoặc Quy trình.
3. **Execution**: Sau khi người dùng duyệt, cập nhật file của skill tương ứng, chạy `npm test` + `sync`, commit; chỉ `git push` khi người dùng đồng ý.

---

## 📦 Danh Sách Kỹ Năng Sẵn Có (9 Skills)

### Kỹ năng Chiến thuật (Aizen Native)
- **`database-table-design`**: Thiết kế DB chuẩn 9 nguyên tắc Enterprise.
- **`devsecops-pipeline-flow`**: Xây dựng CI/CD bảo mật đa nền tảng.
- **`adversarial-code-reviewer`**: Đóng vai Hacker/Reviewer bắt lỗi logic và bảo mật.
- **`video-to-skill`**: Trích xuất tri thức từ YouTube thành Agent Skill.
- **`agent-skill-tester`**: Công cụ kiểm thử tự động các Agent Skills.
- **`tech-learning-tree`**: Xây dựng lộ trình học công nghệ.
- **`skill-cloner`**: Nhân bản, tinh chỉnh và test một skill từ Github vào workspace.
- **`skill-creator`**: Tạo và cải thiện skill mới với chuẩn cấu trúc Aizen, test A/B qua Artifacts.

### Kỹ năng Chiến lược (Master Skill)
- **`cecilia-coding-skills`**: Một Siêu kỹ năng (Super-Agent) tự động điều phối toàn bộ vòng đời phần mềm. Nó được trang bị sẵn 11 Sub-agents bên trong thư mục `agents/` của nó, chạy ở portable mode khi máy không có CLI `cecilia` (xem SKILL.md). Các sub-agent gồm:
  - Lập kế hoạch & Thiết kế (`cecilia-plan`, `cecilia-design`)
  - Lập trình (`cecilia-dev-be`, `cecilia-dev-fe`, `cecilia-ui`, `cecilia-db`)
  - Kiểm thử & Triển khai (`cecilia-test`, `cecilia-api-ux`, `cecilia-devops`)
  - Hội đồng duyệt (`cecilia-review`, `cecilia-discovery`)

---

## ⚡ Tối Ưu Cho Cả Windows và Linux (Cross-Platform)

Hệ thống hoạt động hoàn hảo 100% trên mọi HĐH:
1. **Windows:** Cơ chế **NTFS Directory Junction** cực nhanh, không cần quyền Admin.
2. **Linux & macOS:** **Symbolic Links** tự động cấp quyền thực thi (`chmod 755`) cho các scripts.
3. **Native Plugin:** Repo được định nghĩa là một Antigravity Plugin chuẩn.
4. **Live-Sync:** Sửa file ở repo gốc ➔ Toàn bộ Agent trên máy tự động cập nhật ngay tức thì.
5. **An toàn:** Installer không bao giờ ghi đè thư mục thật trùng tên (skill bạn tự viết) mà chỉ cảnh báo; link tới skill đã xóa/đổi tên được dọn tự động khi `sync`.

---

## 🛠️ Các Lệnh CLI

```bash
aizen status          # Kiểm tra trạng thái liên kết của các Agent
aizen sync            # Đồng bộ đệ quy toàn bộ skills, rules & plugins vào hệ thống
aizen check           # Chỉ kiểm tra có bản mới hay không
aizen update          # Kiểm tra và tải bản cập nhật mới nhất
aizen auto-update     # Bật/tắt lịch cập nhật ngầm hàng ngày (Windows task / Linux cron)
aizen help            # Xem hướng dẫn chi tiết
```

---

## 📄 Bản Quyền & Giấy Phép

Phát hành dưới giấy phép [MIT](LICENSE). Riêng `skills/skill-creator` dựa trên skill của Anthropic và giữ giấy phép Apache 2.0 trong `skills/skill-creator/LICENSE.txt`.

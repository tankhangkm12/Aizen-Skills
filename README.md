# 🌟 Aizen Skills

[![skills.sh](https://skills.sh/b/tankhangkm12/Aizen-Skills)](https://skills.sh/tankhangkm12/Aizen-Skills)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> Bộ kỹ năng AI Agent đa năng tự động cài đặt và đồng bộ hóa tức thì (Live-Sync & Auto-Update) cho tất cả các AI Agent phổ biến: **Antigravity / Gemini CLI**, **Claude Code**, **Cursor**, **Windsurf**, **Cline / Roo Code**, và **Copilot**.

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

# Hoặc chỉ cài đặt một skill cụ thể (ví dụ database-table-design):
npx skills add tankhangkm12/Aizen-Skills --skill database-table-design
```

### Cách 2: Cài đặt toàn cục cho cả máy kèm Live-Sync (Khuyến nghị)
Tự động quét và liên kết toàn bộ kỹ năng vào tất cả AI Agent trên máy tính của bạn:

```bash
npm install -g aizen-skills
```
*(Nếu bạn đã clone repository này về máy, chỉ cần chạy `npm install` ngay tại thư mục repo)*.

### Cách 3: Cài đặt cho một dự án cụ thể (Project-level)
Tạo thư mục `.agents/skills/`, `.cursor/rules/`, và cập nhật file `AGENTS.md` cho dự án:

```bash
npm install --save-dev aizen-skills
# Hoặc chạy lệnh:
npx aizen-skills install --project
```

### Cách 4: Chạy trực tiếp qua NPX (Không cần cài đặt trước)

```bash
npx aizen-skills sync
```

---

## 📁 Cấu Trúc Kho Lưu Trữ (Clean Architecture)

Thư mục gốc được tối giản gọn gàng, toàn bộ kỹ năng được gom riêng vào thư mục `skills/`:

```text
.
├── skills/                     # Thư mục chứa toàn bộ các AI Agent skills
│   ├── adversarial-code-reviewer
│   ├── agent-skill-tester
│   ├── database-table-design
│   ├── tech-learning-tree
│   └── video-to-skill
├── bin/                        # Bộ cài đặt & CLI đa nền tảng (Windows / Linux / macOS)
│   ├── cli.js
│   ├── install.js
│   ├── updater.js
│   └── agents-config.js
├── tests/                      # Bộ kiểm thử tự động (Unit & Integration tests)
├── package.json                # Cấu hình NPM với hook postinstall tự động
└── README.md                   # Hướng dẫn sử dụng
```

---

## ⚡ Tối Ưu Cho Cả Windows và Linux (Cross-Platform)

Hệ thống được thiết kế để hoạt động hoàn hảo 100% trên cả **Windows** và **Linux / macOS**:

1. **Trên Windows:**
   - Sử dụng cơ chế **NTFS Directory Junction** (`mklink /J` qua `fs.symlinkSync(..., 'junction')`).
   - **Ưu điểm vượt trội:** Hoạt động ngay lập tức, **hoàn toàn không cần quyền Administrator**, không yêu cầu bật Windows Developer Mode.
   - Tự động nhận diện và sửa chữa các broken/dangling junctions.

2. **Trên Linux & macOS:**
   - Sử dụng **Symbolic Links** (`ln -s` qua `fs.symlinkSync(..., 'dir')`).
   - Tự động thiết lập quyền thực thi (`chmod 755`) cho các file scripts (.sh, .py, .js) để tránh lỗi `Permission Denied` khi Agent gọi công cụ.
   - Hỗ trợ tự động cấu hình **crontab** với `process.execPath` cho lịch cập nhật tự động.

3. **Cơ Chế Live-Sync:**
   - Các Agent đọc trực tiếp từ thư mục nguồn. Khi bạn chạy `git pull` hoặc `npm update`, toàn bộ AI Agent trên máy **lập tức nhận được cập nhật mới nhất ngay tức thì** mà không cần sao chép thủ công.

---

## 🤖 Các AI Agent Được Hỗ Trợ

| AI Agent | Vị trí cài đặt Toàn cục (Global) | Vị trí cài đặt Dự án (Project) |
| :--- | :--- | :--- |
| **Google Antigravity / Gemini CLI** | `~/.gemini/config/skills/<skill-name>` | `.agents/skills/<skill-name>` |
| **Claude Code** | `~/.claude/skills/<skill-name>` | `.claude/skills/<skill-name>` |
| **Cursor** | `~/.cursor/skills/<skill-name>` | `.cursor/rules/<skill-name>.mdc` |
| **Windsurf** | `~/.codeium/windsurf/memories/` | `.windsurfrules` |
| **Cline / Roo Code** | Custom Instructions | `.clinerules` |
| **Universal Agents** | Standard Agent Path | `AGENTS.md` (Skills Index) |

---

## 📦 Danh Sách Kỹ Năng Sẵn Có trong `skills/`

| Kỹ năng | Mô tả |
| :--- | :--- |
| **`database-table-design`** | Áp dụng 9 nguyên tắc cốt lõi và best practices khi thiết kế bảng MySQL/RDBMS, tối ưu hóa index, phân vùng dọc, và audit columns. |
| **`video-to-skill`** | Trích xuất tri thức từ video YouTube hoặc file video/audio local thành một Agent Skill tái sử dụng theo chuẩn. |
| **`adversarial-code-reviewer`** | Đóng vai reviewer phản biện độc lập, rà soát lỗ hổng logic, bảo mật và hiệu năng. |
| **`agent-skill-tester`** | Bộ công cụ tự động kiểm thử và đánh giá độ chính xác, an toàn của các Agent Skills. |
| **`tech-learning-tree`** | Xây dựng lộ trình học tập công nghệ dạng cây phân cấp (Learning Tree) có cấu trúc cho lập trình viên. |

---

## 🛠️ Các Lệnh CLI

```bash
aizen status          # Kiểm tra trạng thái liên kết của các Agent
aizen sync            # Đồng bộ lại toàn bộ skills vào các Agent
aizen update          # Kiểm tra và tải bản cập nhật mới nhất
aizen auto-update     # Bật/tắt lịch cập nhật ngầm hàng ngày (Windows task / Linux cron)
aizen help            # Xem hướng dẫn chi tiết
```

---

## 📄 Bản Quyền & Giấy Phép

Phát hành dưới giấy phép [MIT](LICENSE).

# Aizen Multi-Plugin Suite (v3.0)

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

Hệ sinh thái Đa Plugin chuẩn mực cho AI coding agents: **Antigravity (Gemini CLI)** và **Claude Code**. 

Khác với các bộ rules/skills truyền thống, Aizen v3.0 chuyển đổi thành một **Hệ sinh thái Đa Plugin (Multi-Plugin Suite)** tự chứa (self-contained), chuyên biệt hóa 100% cho cấp độ **Dự án (Project-level isolated)**, tuân thủ chặt chẽ nguyên tắc **SOLID (Đơn trách nhiệm SRP và Đóng/Mở OCP)**:
* **Không làm ô nhiễm máy (Zero Global Pollution):** Toàn bộ tệp cấu hình, MCP và skills nằm trọn trong thư mục dự án (`.agents/` và `.claude/`).
* **Hỗ trợ Slash Commands:** Gọi nhanh bất kỳ kỹ năng hay plugin nào bằng lệnh `/aizen-skills:<tên>`.
* **Trực quan hóa Canvas:** Tích hợp trực tiếp **Penpot MCP** (vẽ giao diện Canvas theo chuẩn `taste-skills`) và **Archify** (kết xuất sơ đồ kiến trúc HLD/LLD sang HTML/SVG).
* **Kiểm thử Thực tế:** Tích hợp **Playwright MCP** cho phép Agent tự khởi chạy trình duyệt headless, click/test DOM thực tế và chụp ảnh nghiệm thu visual regression.
* **Micro-modular Execution:** Bắt buộc Agent chia nhỏ kế hoạch thành các lát cắt nguyên tử (1–3 files/module) để code nhanh, test dễ và chạy song song an toàn.

---

## Mục lục

- [Danh mục 4 Bộ Plugins](#danh-mục-4-bộ-plugins)
- [Cài đặt vào Dự án](#cài-đặt-vào-dự-án)
- [Cách Sử dụng Slash Commands](#cách-sử-dụng-slash-commands)
- [Tích hợp MCP Servers](#tích-hợp-mcp-servers)
- [Cơ chế Mở rộng: Tạo Plugin Mới (OCP / SRP)](#cơ-chế-mở-rộng-tạo-plugin-mới-ocp--srp)
- [Tài liệu Kiến trúc & Thiết kế](docs/architecture/README.md)
- [Quy chuẩn Plugin](docs/aizen-plugin-standard.md)
- [CLI](#cli)
- [Giấy phép](#giấy-phép)

---

## Danh mục 4 Bộ Plugins

| Plugin | Tên gọi | Danh sách Skills | Chuyên gia đảm nhận (`agents/`) |
| :--- | :--- | :--- | :--- |
| **Thiết kế** | `aizen-design` | `aizen-design`, `aizen-taste-uiux`, `aizen-database`, `aizen-prompt-architect`, `archify` | `system-architect` (HLD/LLD), `uiux-designer` (Penpot Canvas), `database-architect` (3NF/DDL), `api-ux-designer` |
| **Lập trình & QA** | `aizen-code` | `aizen-build`, `aizen-backend`, `aizen-frontend`, `aizen-quality`, `aizen-infra` | `task-planner` (1-3 files/module), `backend-engineer` (Go Clean Arch), `frontend-engineer` (React/Playwright), `qa-tester`, `adversarial-reviewer`, `devops-engineer` |
| **Học tập & R&D** | `aizen-learn` | `aizen-tech-learning`, `aizen-video-to-skill`, `aizen-skill-importer`, `aizen-skill-creator`, `aizen-skill-eval` | `tech-researcher` (Tech tree), `video-synthesizer` (YouTube to markdown), `skill-synthesizer`, `benchmark-evaluator` |
| **Toàn trình Studio** | `aizen-full` | Tích hợp trọn vẹn cả 3 plugin trên vào một pipeline khép kín từ Idea -> Design -> Code -> Deploy | `full-coordinator` điều phối toàn bộ vòng đời dự án |

---

## Cài đặt vào Dự án

Yêu cầu: **Node.js >= 18** và **[uv](https://docs.astral.sh/uv/)**.

Chạy lệnh cài đặt trực tiếp trong thư mục dự án của bạn:

```bash
# 1. Dự án chỉ làm Thiết kế Kiến trúc & UI Canvas:
node /path/to/Aizen-Skills/bin/cli.js install --plugin design

# 2. Dự án chỉ làm Lập trình, Micro-modular & QA Playwright:
node /path/to/Aizen-Skills/bin/cli.js install --plugin code

# 3. Dự án chỉ làm Học tập, Nghiên cứu & Bóc tách Video:
node /path/to/Aizen-Skills/bin/cli.js install --plugin learn

# 4. Dự án Toàn trình từ A-Z (Mặc định):
node /path/to/Aizen-Skills/bin/cli.js install --plugin full
```

Sau khi cài đặt, dự án tự động có:
* `./.agents/skills/` (cho Antigravity / Gemini CLI)
* `./.claude/skills/` và `./.claude/commands/` (cho Claude Code)
* `./.mcp.json` (cấu hình MCP Servers tương ứng)
* `./.git/hooks/pre-push` (chốt chặn kiểm định trước khi push)

---

## Cách Sử dụng Slash Commands

Trong giao diện chat của **Claude Code** hoặc **Antigravity**, bạn và AI có thể gõ trực tiếp các lệnh nhanh:

* `/aizen-skills:design`: Kích hoạt quy trình thiết kế SRS, kiến trúc Archify và Canvas Penpot.
* `/aizen-skills:code`: Kích hoạt quy trình bẻ nhỏ micro-modules và lập trình có kiểm định.
* `/aizen-skills:penpot`: Mở hướng dẫn và công cụ vẽ layout, shapes trực tiếp trên Penpot Canvas.
* `/aizen-skills:playwright`: Kích hoạt kịch bản mở trình duyệt headless kiểm thử UI và chụp ảnh màn hình.
* `/aizen-skills:archify`: Kết xuất toàn bộ sơ đồ HLD/LLD sang HTML tương tác.

---

## Tích hợp MCP Servers

Aizen tự động quản lý file `.mcp.json` tại gốc dự án theo từng plugin:
* **`sequentialthinking`**: Bắt buộc cho mọi bài toán phức tạp, phân tích blast radius và giải thuật.
* **`context7`**: Tra cứu tài liệu và thư viện mới nhất.
* **`playwright`**: Tự động hóa kiểm thử trình duyệt, chụp ảnh màn hình, kiểm tra DOM và console log.
* **`penpot`**: Thao tác và sinh component trực tiếp trên Canvas Penpot qua API.

---

## Cơ chế Mở rộng: Tạo Plugin Mới (OCP / SRP)

Aizen mở cho việc mở rộng nhưng đóng với việc sửa core engine. Khi bạn hoặc AI Agent muốn tạo một plugin mới:

```bash
# 1. Tạo bộ khung plugin mới chuẩn hóa:
node bin/cli.js plugin create aizen-security --domain security

# 2. Kiểm tra tính hợp lệ của Plugin theo chuẩn Aizen:
node bin/cli.js plugin validate plugins/aizen-security
```

Bộ linter tự động kiểm tra tính tuân thủ:
* Đầy đủ `plugin.json`, `workflow.md`, `agents/`, `mcp.template.json`.
* Mỗi agent trong `agents/` có phân quyền A1-A4 rõ ràng.
* Plugin mới tự động xuất hiện trong danh sách `aizen plugin list` và cài đặt được ngay qua `aizen install --plugin security`.

---

## Kiểm thử & Phát triển

```bash
npm test    # Chạy toàn bộ 5 bài test: check-skills, check-scripts, test-installer, test-external, test-plugins
```

## Giấy phép
Dự án được phát hành theo giấy phép [MIT](LICENSE).

# Quy Chuẩn Kiến Trúc Aizen Plugin (Aizen Plugin Specification Standard v3.0)

Tài liệu này định nghĩa quy chuẩn thiết kế, cấu trúc thư mục, giao diện trừu tượng và các nguyên tắc công nghệ bắt buộc áp dụng khi phát triển hoặc để AI Agent tự động khởi tạo một **Aizen Plugin** mới.

---

## 1. Các Nguyên Tắc Thiết Kế Bắt Buộc (Core Principles)

### 1.1. Nguyên tắc Đóng/Mở (Open/Closed Principle - OCP)
* **Mở để mở rộng (Open for extension):** Bất kỳ lập trình viên hoặc AI Agent nào cũng có thể bổ sung plugin mới vào thư mục `plugins/<plugin-id>/` mà không làm thay đổi hệ sinh thái sẵn có.
* **Đóng với việc sửa đổi (Closed for modification):** Core engine (`bin/cli.js`, `bin/install.js`) hoàn toàn không hardcode danh sách plugin. Hệ thống phát hiện tự động (Auto-discovery) thông qua file `plugin.json` tuân thủ bản hợp đồng này.

### 1.2. Nguyên tắc Đơn Trách Nhiệm (Single Responsibility Principle - SRP)
* **Phạm vi Plugin:** Mỗi plugin chỉ giải quyết đúng một miền nghiệp vụ duy nhất (Ví dụ: `aizen-design` chỉ lo phân tích và thiết kế; `aizen-code` chỉ lo lập trình và kiểm thử; `aizen-learn` chỉ lo nghiên cứu và tổng hợp tri thức).
* **Phạm vi Agent:** Mỗi tệp trong thư mục `agents/` chỉ đặc tả một vai trò chuyên gia duy nhất với ranh giới quyền hạn (Authority Levels A1-A4) và công cụ rõ ràng.

### 1.3. Tính Trừu Tượng Hóa & Hợp Đồng Dữ Liệu (Abstraction & Contracts)
* Mọi plugin là một thể hiện cụ thể (concrete implementation) kế thừa từ giao diện chuẩn:
  1. Manifest hợp lệ: `plugin.json`
  2. Chu trình làm việc riêng: `workflow.md`
  3. Đội ngũ chuyên gia: `agents/*.md`
  4. Bộ kỹ năng chuyên ngành: `skills/`
  5. Cấu hình Model Context Protocol: `mcp.template.json`

---

## 2. Cấu Trúc Thư Mục Chuẩn Của Một Plugin

Khi tạo một plugin mới (`plugins/<plugin-id>/`), cấu trúc bắt buộc phải tuân theo:

```
plugins/<plugin-id>/
├── plugin.json                 # Manifest khai báo metadata, capabilities, mcp, agents
├── workflow.md                 # Chu trình làm việc đặc thù của miền nghiệp vụ đó
├── agents/                     # Danh sách các vai trò chuyên gia (mỗi file 1 vai trò - SRP)
│   ├── <role-1>.md
│   └── <role-2>.md
├── skills/                     # Danh sách kỹ năng hoặc tham chiếu tới skills/
├── mcp.template.json           # Khai báo cấu hình MCP Server cho plugin
└── README.md                   # Hướng dẫn chi tiết phạm vi và cách dùng
```

---

## 3. Đặc Tả Schema `plugin.json`

Mỗi file `plugin.json` phải chứa đầy đủ các trường sau:

```json
{
  "id": "aizen-domain-name",
  "name": "Tên Hiển Thị Của Plugin",
  "version": "1.0.0",
  "description": "Mô tả mục tiêu duy nhất của plugin theo chuẩn SRP (không quá 500 ký tự).",
  "domain": "design | code | learn | data | custom",
  "workflow": "./workflow.md",
  "skills": [
    "aizen-skill-id-1",
    "aizen-skill-id-2"
  ],
  "agents": [
    {
      "id": "chuyen-gia-1",
      "name": "Tên Chuyên Gia 1",
      "responsibility": "Mô tả trách nhiệm duy nhất của vai trò này",
      "file": "./agents/chuyen-gia-1.md",
      "tools": ["mcp:tool-name"]
    }
  ],
  "mcp": {
    "required": ["sequentialthinking", "context7"],
    "optional": ["playwright", "penpot", "archify"]
  }
}
```

---

## 4. Quy Chuẩn Các Thành Phần Bắt Buộc

### 4.1. Quy chuẩn Workflow (`workflow.md`)
* Không dùng chung một workflow cho tất cả các bài toán. Mỗi plugin phải có chu trình làm việc riêng:
  * **Design Workflow:** Khảo sát (SRS) -> Kiến trúc (Archify) -> UI/UX Canvas (Penpot / taste-skills) -> CSDL & API Contracts.
  * **Coding Workflow:** Micro-modular breakdown (1-3 files/module) -> Đóng băng Acceptance -> Atomic Code -> Test tự động (Playwright cho Frontend) -> Adversarial Review -> Pre-push Guard.
  * **Learning Workflow:** Deep-dive tài liệu -> Phân tích video -> Dựng cây tri thức (Tech Tree) -> Xuất Notion -> Đóng gói & Eval Skill.

### 4.2. Quy chuẩn MCP Server
* **Bắt buộc chung:** Mọi plugin đều phải tích hợp `sequentialthinking` (tư duy tuần tự từng bước) và `context7` (tra cứu docs chính xác).
* **Frontend / UI Testing:** Bắt buộc tích hợp `playwright` để khởi chạy trình duyệt headless, kiểm tra trực tiếp DOM, visual regression và console logs.
* **Canvas Design:** Bắt buộc tích hợp `penpot` (hoặc Figma/Google Stitch) để vẽ và tương tác trực tiếp trên canvas thông qua API.
* **Architecture:** Bắt buộc tích hợp `archify` để trực quan hóa sơ đồ HLD, LLD, Sequence, DFD.

### 4.3. Quy chuẩn Đội ngũ Chuyên gia (`agents/*.md`)
* Mỗi file trong `agents/` phải có cấu trúc:
  1. `# Role: <Tên Vai Trò>`
  2. `## Trách nhiệm cốt lõi (Single Responsibility)`
  3. `## Bảng phân quyền (Authority Levels: Free, A3, Never)`
  4. `## Quy trình thực hiện (Step-by-step Instructions)`
  5. `## Tiêu chuẩn đầu ra (Acceptance Artifacts)`

---

## 5. Hướng Dẫn Tự Động Hóa Dành Cho AI Agent

Khi được yêu cầu: *"Hãy tạo một plugin mới cho Aizen về [Chủ đề X]"*, AI Agent phải tuân theo 4 bước sau:

1. **Khởi tạo bộ khung chuẩn:**
   Chạy lệnh CLI:
   ```bash
   node bin/cli.js plugin create <tên-plugin> --domain <domain>
   ```
2. **Điền nội dung chuyên môn:**
   * Soạn thảo `workflow.md` mô tả các bước thực hiện tinh gọn nhưng kiểm soát chặt chẽ.
   * Viết các file vai trò chuyên gia độc lập trong thư mục `agents/`.
   * Khai báo các MCP Server cần thiết trong `mcp.template.json`.
3. **Kiểm tra hợp đồng linter (Validation):**
   Chạy lệnh xác thực:
   ```bash
   node bin/cli.js plugin validate plugins/<tên-plugin>
   ```
   Nếu linter phát hiện thiếu trường, vi phạm cấu trúc hoặc thiếu tệp vai trò, Agent phải tự sửa chữa cho đến khi đạt 100%.
4. **Đăng ký vào hệ sinh thái:**
   Plugin mới sẽ tự động được nhận diện bởi `bin/install.js` và cho phép cài đặt qua lệnh:
   ```bash
   node bin/cli.js install --plugin <tên-plugin>
   ```

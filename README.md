# 🌟 Aizen Skills

[![skills.sh](https://skills.sh/b/tankhangkm12/Aizen-Skills)](https://skills.sh/tankhangkm12/Aizen-Skills)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> Bộ kỹ năng AI Agent đa năng tự động cài đặt và đồng bộ hóa tức thì (Live-Sync & Auto-Update) cho tất cả các AI Agent phổ biến: **Antigravity / Gemini CLI**, **Claude Code**, **Cursor**, **Windsurf**, **Cline / Roo Code**, và **Copilot**. 
> Đặc biệt, toàn bộ kho lưu trữ này hoạt động như một **Native Antigravity Plugin** và đã được tích hợp sức mạnh siêu phân tách của hệ điều hành **Cecilia v20.2.0**.

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
Tự động quét đệ quy và liên kết toàn bộ kỹ năng, copy rules, đồng thời **đăng ký Aizen-Skills như một Plugin gốc** cho Antigravity trên máy tính của bạn:

```bash
npm install -g aizen-skills
```
*(Nếu bạn đã clone repository này về máy, chỉ cần chạy `npm install` ngay tại thư mục repo hoặc gõ `node bin/cli.js sync`)*.

---

## 📁 Kiến Trúc Phân Tách Siêu Rời (Decoupled Architecture)

Thư mục gốc được thiết kế theo cấu trúc cây chuyên biệt. Chúng tôi đã tách biệt hoàn toàn **Quy trình (Skills)**, **Công cụ (Tools)**, và **Tri thức (Knowledge)** để tối đa hóa khả năng mở rộng và giảm tải Context Window cho Agent:

```text
.
├── skills/                     # Quy trình làm việc (Chỉ chứa file cấu trúc các bước thực thi)
│   ├── programming/            # Lập trình & Kỹ thuật
│   ├── workflow/               # Quy trình & Điều phối 
│   ├── education/              # Học tập & Đào tạo
│   └── tools/                  # Kiểm thử (Testing & Builders)
├── tools/                      # Các script thực thi (Python/JS) dùng chung cho Agent
├── knowledge/                  # Cơ sở Tri thức (Kiến thức Domain, Code Standards, DB Rules)
├── rules/                      # Quy tắc hệ thống toàn cục (VD: Continuous Improvement Loop)
├── plugin.json                 # Manifest khai báo Aizen-Skills là một Antigravity Plugin
├── bin/                        # Bộ cài đặt & CLI đa nền tảng
├── package.json                # Cấu hình NPM
└── README.md                   # Hướng dẫn sử dụng
```

---

## 🔄 Vòng Lặp Cải Thiện Liên Tục (Continuous Improvement Loop)

Bộ Aizen-Skills được tích hợp sẵn một **Rule Hệ thống** thông minh tại `rules/continuous-improvement.md`. Khi được đồng bộ vào máy, nó ép buộc mọi AI Agent phải tuân thủ:
1. **Self-Evaluate**: Đánh giá độ hiệu quả của code/prompt ngay sau khi thực hiện xong task.
2. **Proposal**: Tự động phát hiện điểm yếu, đề xuất cập nhật Công cụ, Kiến thức hoặc Quy trình.
3. **Execution**: Nắm quyền tự cập nhật file, gọi script `sync` và `git push` lên nhánh `main` khi được bạn phê duyệt.

---

## 📦 Danh Sách Kỹ Năng Sẵn Có (18 Skills)

Các skills được phân loại khoa học vào từng nhóm chuyên môn:

### 💻 1. Lập Trình & Kỹ Thuật (`programming/`)
| Kỹ năng | Mô tả |
| :--- | :--- |
| **`cecilia-dev-be`** | Lập trình viên Backend (Cecilia). Code logic, API, kết nối DB đảm bảo tính toàn vẹn và sạch sẽ. |
| **`cecilia-dev-fe`** | Lập trình viên Frontend (Cecilia). Xây dựng UI Component và màn hình chính xác theo thiết kế. |
| **`cecilia-ui`** | Designer UI (Cecilia). Phác thảo giao diện, hệ thống màu sắc và layout trước khi code. |
| **`cecilia-api-ux`** | Chuyên gia review trải nghiệm API (Consumer role). Đánh giá tính thân thiện và bảo mật của API. |
| **`cecilia-db`** | Chuyên gia CSDL (Cecilia). Tối ưu schema, index, và truy vấn chậm. |
| **`database-table-design`** | Thiết kế bảng MySQL/RDBMS theo 9 nguyên tắc cốt lõi (tối ưu index, audit, partition). |
| **`cecilia-devops`** | Kỹ sư DevOps (Cecilia). Viết CI/CD, Dockerfiles, compose, và giám sát hạ tầng. |
| **`devsecops-pipeline-flow`** | Tự động lập kế hoạch và triển khai DevSecOps pipeline bảo mật đa nền tảng, 5 cổng kiểm soát. |
| **`cecilia-review`** | Reviewer độc lập (Cecilia). Phân tích mã nguồn không thiên vị, bầu chọn duyệt code. |
| **`adversarial-code-reviewer`** | Đóng vai reviewer phản biện độc lập, rà soát lỗ hổng logic, bảo mật và hiệu năng. |

### 🔄 2. Quy Trình & Kiến Trúc (`workflow/`)
| Kỹ năng | Mô tả |
| :--- | :--- |
| **`cecilia-orchestrator`** | Trái tim điều phối của Cecilia. Phân chia task, gọi agent phụ, quản lý quy trình. |
| **`cecilia-plan`** | Kỹ sư quy hoạch (Planning). Cạnh tranh chéo giữa 3 agent để đưa ra kế hoạch code tối ưu nhất. |
| **`cecilia-discovery`** | Kỹ sư khảo sát dự án (Discovery). Dựng bản đồ dự án hiện tại (as-built) làm cơ sở dữ liệu. |
| **`cecilia-design`** | Kỹ sư thiết kế kiến trúc (Design). Chuyển hóa yêu cầu thành HLD, LLD, sequence diagrams. |

### 🛠️ 3. Công Cụ & Kiểm Thử (`tools/`)
| Kỹ năng | Mô tả |
| :--- | :--- |
| **`cecilia-test`** | Kỹ sư kiểm thử độc lập (Cecilia). Chạy test functional, integration, API dựa trên tiêu chuẩn. |
| **`agent-skill-tester`** | Bộ công cụ kiểm thử độ chính xác, an toàn, và bảo mật của các AI Agent Skills. |
| **`video-to-skill`** | Trích xuất tri thức từ YouTube/video thành một Agent Skill theo format chuẩn. |

### 🎓 4. Học Tập (`education/`)
| Kỹ năng | Mô tả |
| :--- | :--- |
| **`tech-learning-tree`** | Xây dựng lộ trình học tập công nghệ dạng cây phân cấp (Learning Tree) có cấu trúc. |

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

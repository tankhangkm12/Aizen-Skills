# Aizen Skills

[![skills.sh](https://skills.sh/b/tankhangkm12/Aizen-Skills)](https://skills.sh/tankhangkm12/Aizen-Skills)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Bộ skill cho AI coding agent: **Claude Code**, **Antigravity / Gemini CLI**, **Cursor**, **Windsurf** và mọi agent đọc
thư mục chuẩn `~/.agents/skills`. Mỗi skill là một thư mục tự chứa (`SKILL.md` + tài nguyên), cài bằng liên kết
(junction/symlink) nên sửa trong repo là agent thấy ngay.

## Mục lục

- [Cài đặt](#cài-đặt)
- [Danh sách skill](#danh-sách-skill)
- [Cecilia — trợ lý production coding](#cecilia--trợ-lý-production-coding)
- [Cấu trúc repo](#cấu-trúc-repo)
- [CLI](#cli)
- [Phát triển skill](#phát-triển-skill)
- [Gỡ cài đặt](#gỡ-cài-đặt)
- [Giấy phép](#giấy-phép)

## Cài đặt

Yêu cầu: Node.js ≥ 18, Git. Một số skill dùng thêm Python 3 (scripts) — không bắt buộc để cài.

### Cách 1 — Clone và liên kết (khuyến nghị)

```bash
git clone https://github.com/tankhangkm12/Aizen-Skills.git
cd Aizen-Skills
npm install          # postinstall tự chạy bộ cài (global)
# hoặc chạy tay:
node bin/cli.js sync
```

Bộ cài liên kết từng thư mục trong `skills/` vào:

| Agent | Thư mục |
|---|---|
| Universal (`.agents`) | `~/.agents/skills` |
| Claude Code | `~/.claude/skills` |
| Antigravity CLI | `~/.gemini/antigravity-cli/skills` |
| Gemini CLI | `~/.gemini/skills` |
| Antigravity config | `~/.gemini/config/skills` |
| Cursor | `~/.cursor/skills` |
| Windsurf | `~/.codeium/windsurf/skills` |

Ngoài ra nó chép `rules/*.md` vào `~/.gemini/config/rules/` và đăng ký cả repo làm plugin Antigravity tại
`~/.gemini/config/plugins/aizen-skills`.

- **Windows** dùng NTFS junction (không cần quyền Admin); **Linux/macOS** dùng symlink và `chmod 755` cho scripts.
- Thư mục thật trùng tên (skill bạn tự viết) **không bị ghi đè** — bộ cài chỉ cảnh báo.
- Liên kết trỏ tới skill đã xóa/đổi tên được dọn khi chạy `sync`.

Cài cho riêng một project (`./.agents/skills`, `./.claude/skills`, `./.cursor/rules/*.mdc`):

```bash
node /path/to/Aizen-Skills/bin/cli.js sync --project
```

### Cách 2 — Qua skills.sh

```bash
npx skills add tankhangkm12/Aizen-Skills --list   # xem danh sách
npx skills add tankhangkm12/Aizen-Skills          # cài tất cả
```

Cách này chép skill (không live-sync, không cài rules/plugin).

Sau khi cài, khởi động lại agent (hoặc mở session mới) để nó nạp danh sách skill.

## Danh sách skill

| Skill | Dùng khi |
|---|---|
| [`cecilia-coding-skills`](skills/cecilia-coding-skills) | Làm tính năng/bug fix production: lập kế hoạch, code song song, test, review, PR. Xem [bên dưới](#cecilia--trợ-lý-production-coding). |
| `cecilia-*` (6 knowledge pack) | Kiến thức theo chủ đề cho các role của Cecilia — không gọi trực tiếp, Cecilia tự nạp. |
| [`adversarial-code-reviewer`](skills/adversarial-code-reviewer) | Review PR/diff/code do AI viết theo góc nhìn đối kháng: blast radius, lỗi logic, bảo mật. |
| [`database-table-design`](skills/database-table-design) | Thiết kế schema quan hệ / bảng MySQL theo 9 nguyên tắc, viết DDL, review kiến trúc DB. |
| [`devsecops-pipeline-flow`](skills/devsecops-pipeline-flow) | Dựng CI/CD bảo mật (GitHub Actions, GitLab CI, Jenkins, ArgoCD), quét Gitleaks/Trivy/Semgrep, có các bước xác nhận. |
| [`agent-skill-tester`](skills/agent-skill-tester) | Đánh giá một skill so với baseline (Outcome, Process, Style, Efficiency), LLM-as-a-judge. |
| [`skill-creator`](skills/skill-creator) | Tạo/cải thiện skill theo cấu trúc Aizen, chạy eval. |
| [`skill-cloner`](skills/skill-cloner) | Chép skill từ GitHub/đường dẫn local, phỏng vấn để tùy biến rồi đồng bộ. |
| [`tech-learning-tree`](skills/tech-learning-tree) | Nghiên cứu công nghệ mới và ghi lại thành cây kiến thức trên Notion. |
| [`video-to-skill`](skills/video-to-skill) | Biến video YouTube/file local thành skill (phụ đề → hoặc ffmpeg + speech-to-text). |

Agent tự chọn skill theo `description` trong `SKILL.md`; bạn cũng có thể gọi trực tiếp (Claude Code: `/<tên-skill>`).

## Cecilia — trợ lý production coding

`cecilia-coding-skills` (v22) điều phối một task code từ yêu cầu đến PR, **chỉ làm local** — agent không bao giờ
`git push`; cuối task bạn nhận khối lệnh push/PR để tự chạy.

**Chế độ**

| Mode | Khi nào | Luồng | Số sub-agent |
|---|---|---|---|
| FAST | sửa nhỏ, rõ ràng | main session tự sửa và chạy test | 0 |
| STANDARD | mặc định | planner → 1 decision card → `dev` song song (mỗi unit một worktree) → tích hợp `int/<TASK>` → tester → reviewer → fix ≤ 2 vòng | ~4–6 (+3 mỗi vòng fix) |
| CONTROLLED | auth, tiền, migration, concurrency, contract public, infra, prod | như STANDARD + duyệt plan rõ ràng + reviewer thứ hai (`LENS=redteam`) + `devops` khi đụng hạ tầng | ~6–8 (+3 mỗi vòng fix) |

**5 role** (`agents/`)

| Role | Việc | Ghi code? |
|---|---|---|
| `planner` | khảo sát codebase, yêu cầu/thiết kế khi cần, kế hoạch chia unit + 2–3 phương án | không (chỉ docs/plan) |
| `dev` | thực thi một unit; `KIND=be\|fe\|db\|ui` quyết định nạp kiến thức nào | có, trong worktree riêng |
| `tester` | viết/chạy test theo lens, báo bug có bằng chứng | test |
| `reviewer` | review độc lập trên SHA đã tích hợp, read-only | không |
| `devops` | CI/CD, Docker, IaC, deploy/rollback, sự cố | file hạ tầng |

**Kiến thức chia theo chủ đề** thành skill chính + 6 knowledge pack cài cạnh nhau; mỗi chủ đề có `method.md` làm
điểm vào, agent chỉ nạp file cần cho việc đang làm. Brief của mỗi role in bảng đường dẫn tuyệt đối tới các pack.

| Skill | `references/` |
|---|---|
| `cecilia-coding-skills` | `flow`, `plan`, `dev`, `common` + toàn bộ `agents/`, `rules/`, `assets/`, `scripts/` |
| `cecilia-discover-design` | `discover`, `design` |
| `cecilia-backend` | `backend`, `api-ux` |
| `cecilia-frontend` | `frontend`, `ui` |
| `cecilia-db` | `db` |
| `cecilia-quality` | `test`, `review` |
| `cecilia-infra` | `infra` |

**Quy tắc chính** (`rules/core.md`): mức quyền A0–A4 (việc rủi ro phải hỏi), không tự quyết thay người dùng, mọi kết
luận gắn nhãn `[verified]/[inferred]/[unverified]/[projected]`, kiểm diff/test/SHA thay vì tin báo cáo "DONE".

**Scripts** (`scripts/`, Python 3, chạy từ thư mục project bằng đường dẫn tuyệt đối tới skill):

```bash
S=~/.claude/skills/cecilia-coding-skills/scripts
python $S/state.py init --task T-12 --goal "..." --mode standard   # trạng thái task để resume
python $S/check.py --task T-12 --unit api  # lint, typecheck, build, test, secrets, deps → evidence-api.json
python $S/capacity.py --help               # ước lượng tải/dung lượng
```

`check.py` chỉ báo PASS khi có bước thật sự chạy và đạt; thiếu test hoặc không quét được secrets → `UNVERIFIED`
(exit 3), không bao giờ là PASS.

Trạng thái và báo cáo ghi vào `tensura/` ở gốc project (local-only, nên thêm vào `.git/info/exclude`).

Hỗ trợ Claude Code (Agent tool, worktree) và Antigravity (`define_subagent`/`invoke_subagent`) — chi tiết trong
`references/flow/platform-*.md`.

## Cấu trúc repo

```text
.
├── skills/<skill>/            # mỗi skill tự chứa, đủ 8 phần:
│   ├── SKILL.md               #   điểm vào: front-matter name/description + hướng dẫn
│   ├── manifest.json          #   metadata, version
│   ├── rules/                 #   luật bắt buộc
│   ├── agents/                #   prompt sub-agent
│   ├── references/            #   kiến thức nạp theo nhu cầu
│   ├── tools/                 #   định nghĩa tool
│   ├── scripts/               #   mã chạy được (Python/JS)
│   └── assets/                #   template, file tĩnh
├── rules/                     # rule toàn cục (continuous-improvement.md)
├── bin/                       # cli.js, install.js, updater.js, agents-config.js
├── tests/                     # check-skills.js (lint cấu trúc), check-scripts.js (smoke test Python), test-installer.js
├── plugin.json                # manifest plugin Antigravity
└── package.json
```

Thư mục rỗng giữ bằng `.gitkeep`. Knowledge pack (`manifest.json` có `partOf`) chỉ cần `SKILL.md`, `manifest.json`,
`references/`. `tests/check-skills.js` kiểm: đủ thành phần, tên khớp thư mục, `description` ≤ 1024 ký tự, mọi
đường dẫn `` `references|assets|scripts|agents|rules/…` `` và link markdown tương đối tồn tại (xuyên pack), `(vNN)`
khớp `manifest.version`, không còn tên role cũ.

## CLI

Chạy bằng `node bin/cli.js <lệnh>` (hoặc `aizen <lệnh>` nếu đã `npm link`):

| Lệnh | Việc |
|---|---|
| `status` | liệt kê skill và số liên kết ở từng agent |
| `sync` / `install` | liên kết skills, chép rules, đăng ký plugin; `--project` để cài vào project hiện tại |
| `check` | kiểm tra có bản mới không |
| `update` | kéo bản mới (git) rồi sync |
| `auto-update enable\|disable` | bật/tắt cập nhật ngầm hằng ngày (Task Scheduler / cron) |
| `help` | trợ giúp |

## Phát triển skill

1. Tạo skill mới bằng `skill-creator` hoặc chép một skill có sẵn, giữ đủ 8 phần.
2. `description` trong `SKILL.md` quyết định khi nào agent chọn skill — viết rõ "dùng khi…".
3. Giữ `SKILL.md` ngắn; kiến thức dài đưa vào `references/` và chỉ dẫn khi nào đọc.
4. Kiểm tra rồi đồng bộ:

```bash
npm test               # check-skills.js + check-scripts.js + test-installer.js
node bin/cli.js sync
```

Rule `rules/continuous-improvement.md` yêu cầu agent sau mỗi lần dùng skill tự đánh giá, đề xuất cải tiến, và chỉ
sửa skill khi bạn đồng ý.

## Gỡ cài đặt

Xóa các liên kết (không xóa repo): các mục trùng tên skill trong những thư mục ở bảng [Cài đặt](#cài-đặt),
`~/.gemini/config/plugins/aizen-skills` và `~/.gemini/config/rules/continuous-improvement.md`. Trên Windows dùng
`rmdir <link>` (xóa junction, không đụng thư mục gốc). Tắt cập nhật ngầm: `node bin/cli.js auto-update disable`.

## Giấy phép

[MIT](LICENSE). Riêng `skills/skill-creator` dựa trên skill của Anthropic, giữ giấy phép Apache 2.0 trong
`skills/skill-creator/LICENSE.txt`.

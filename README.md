# Aizen Skills

[![skills.sh](https://skills.sh/b/tankhangkm12/Aizen-Skills)](https://skills.sh/tankhangkm12/Aizen-Skills)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Bộ skill cho AI coding agent: **Claude Code**, **Antigravity / Gemini CLI**, **Cursor**, **Windsurf** và mọi agent đọc
thư mục chuẩn `~/.agents/skills`. Mỗi skill là một thư mục (`SKILL.md` + tài nguyên) cài cạnh nhau bằng liên kết
(junction/symlink) nên sửa trong repo là agent thấy ngay. Luật chung nằm một chỗ ở `aizen-core`; vì vậy hãy cài cả
bộ (hoặc ít nhất skill cần dùng cùng các skill trong `requires` của `manifest.json`).

## Mục lục

- [Cài đặt](#cài-đặt)
- [Hướng dẫn sử dụng và prompt mẫu](docs/huong-dan-su-dung.md)
- [Danh sách skill](#danh-sách-skill)
- [Nguyên tắc làm việc của agent](#nguyên-tắc-làm-việc-của-agent)
- [Kiến trúc bộ skill (SOLID)](#kiến-trúc-bộ-skill-solid)
- [aizen-build — điều phối production](#aizen-build--điều-phối-production)
- [Nâng cấp từ bản trước](#nâng-cấp-từ-bản-trước-đổi-tên)
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

Ngoài ra nó chép `rules/*.md` vào `~/.gemini/config/rules/` (Antigravity) và `~/.claude/rules/` (Claude Code), và đăng ký cả repo làm plugin Antigravity tại
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

**Dùng thế nào cho hiệu quả:** đọc [docs/huong-dan-su-dung.md](docs/huong-dan-su-dung.md) và copy prompt từ
[docs/prompt-mau.md](docs/prompt-mau.md) — prompt đủ 6 phần (mục tiêu, tiêu chí xong, phạm vi, ràng buộc, tài liệu,
quyền cho trước) giúp agent không phải đoán và không hỏi lại.

## Danh sách skill

Bộ skill chia làm hai loại (theo `kind` trong `manifest.json`):

- **entry** — skill bạn gọi (agent tự chọn theo `description`, hoặc `/<tên>`).
- **pack** — kho kiến thức theo topic; không gọi trực tiếp, các entry tự nạp đúng file cần.

| Skill | Dùng khi |
|---|---|
| [`aizen-build`](skills/aizen-build) | Mọi việc kỹ thuật trên dự án đang có: tính năng, sửa bug, refactor, từ ý tưởng tới PR; **review** PR/diff; **chỉ thiết kế** (schema, API, kiến trúc); **chỉ dựng** CI/CD, Docker, Kubernetes. Xem [bên dưới](#aizen-build--điều-phối-production). |
| [`aizen-init`](skills/aizen-init) | Khởi tạo dự án backend cho team từ repo + tài liệu theo 11 bước có checkpoint: Git Flow, plan trong `.aizen/init/`, khung code + health check, Docker/compose kèm infra, config tập trung, kết nối infra fail-fast, adapter, AOP + request-id + auth, README, rà lại bằng graphify. |
| [`aizen-skill-creator`](skills/aizen-skill-creator) | Tạo skill mới hoặc cải thiện skill có sẵn theo chuẩn Aizen, đặt đúng chỗ (entry hay topic của pack), viết docs, đánh giá, `npm test`, commit. |
| [`aizen-skill-importer`](skills/aizen-skill-importer) | Đưa tri thức bên ngoài vào Aizen: chép cả skill (ghi nguồn/giấy phép, tuỳ biến, A/B test) hoặc **vendor** best practice của upstream vào một pack, ghim commit. |
| [`aizen-skill-eval`](skills/aizen-skill-eval) | Đánh giá một skill so với baseline: bộ eval (gồm negative control), chạy độc lập, chấm điểm, A/B, tổng hợp benchmark. |
| [`aizen-tech-learning`](skills/aizen-tech-learning) | Nghiên cứu sâu một công nghệ theo một workload: từ tầng ứng dụng xuống runtime, kernel, network; sơ đồ Mermaid; so sánh bằng kiến trúc; đăng lên Notion. |
| [`aizen-video-to-skill`](skills/aizen-video-to-skill) | Biến video YouTube/file local thành skill (phụ đề → hoặc ffmpeg + speech-to-text). |

| Pack | Topic | Nội dung |
|---|---|---|
| `aizen-core` | `core` | Luật chung cho mọi skill: quyền A0–A4, evidence, quyết định, git local-only, code-quality (4 nguyên tắc Karpathy, thang tái sử dụng, `ponytail:`), code-style; `check.py`, `graph.py`, `capacity.py` |
| `aizen-design` | `discover`, `design` | phạm vi, onboard code cũ, SRS, HLD/LLD, API contract, threat model |
| `aizen-backend` | `backend`, `api-ux` | nguyên tắc backend, kiến trúc, messaging (Kafka, RabbitMQ), S3, microservices, stack Spring Boot / FastAPI / NestJS |
| `aizen-frontend` | `frontend`, `ui` | nguyên tắc frontend, React/Next (luật của Vercel), accessibility, kiểm tra bằng trình duyệt, UI design |
| `aizen-database` | `db` | schema, migration, concurrency, hiệu năng, HA/DR; PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch |
| `aizen-quality` | `test`, `review` | chiến lược test, lens, review độc lập (blast radius, gating), verify báo cáo |
| `aizen-infra` | `infra` | pipeline + security gate, deploy/rollback, secrets, observability, sự cố; Docker, Podman, Kubernetes/Helm, Terraform, Cloudflare |

Agent tự chọn skill theo `description` trong `SKILL.md`; bạn cũng có thể gọi trực tiếp (Claude Code: `/<tên-skill>`).

## Nguyên tắc làm việc của agent

Bốn nguyên tắc của [andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) áp cho mọi việc
code, ở hai mức:

- **Mọi session agent trên máy** — `rules/working-principles.md` được `sync` cài vào `~/.claude/rules/`,
  `~/.gemini/config/rules/` (và `.mdc` cho Cursor khi `sync --project`).
- **Trong các skill Aizen** — mỗi nguyên tắc có chỗ thực thi và chỗ kiểm (bảng trong `skills/aizen-core/SKILL.md`):

| Nguyên tắc | Aizen thực thi bằng |
|---|---|
| Nghĩ trước khi code | câu hỏi chỉ ở pha plan, có phương án + mặc định; dòng "Simpler option"; `approve` chặn module chưa xác nhận |
| Đơn giản trước | thang tái sử dụng, không trừu tượng cho code dùng một lần, không phòng thủ trạng thái không thể xảy ra, câu hỏi "200 → 50" |
| Sửa như phẫu thuật | mọi dòng đổi phải truy về yêu cầu; chỉ dọn rác của chính mình, code chết có sẵn thì ghi vào `## Proposals` |
| Thực thi theo mục tiêu | Done của module thành check chạy được trước khi code, test fail trước, `step → verify` |

## Kiến trúc bộ skill (SOLID)

| Nguyên tắc | Áp vào Aizen |
|---|---|
| **S** — một lý do để thay đổi | mỗi pack sở hữu đúng các topic của nó: `references/<topic>/`, `assets/<topic>/`, `scripts/<topic>/` nằm cùng nhau. Luật chung chỉ có một bản ở `aizen-core` (trước đây 10 bản `rules/mcp.md`). |
| **O** — mở để mở rộng, đóng để sửa | thêm pack/topic mới chỉ cần khai báo `topics` trong `manifest.json`; `state.py` và lint đọc manifest, không sửa code. Stack/engine/platform mới: một file trong `stacks/`, `engines/`, `platforms/`. |
| **L** — thay thế được | mọi pack theo cùng một hợp đồng: `SKILL.md` + `manifest.json` (`kind`, `topics`, `requires`) + `method.md` làm điểm vào. |
| **I** — interface nhỏ | role chỉ nạp topic nó cần; mỗi `method.md` có bảng "Guides" để nạp từng dòng. Review, thiết kế, pipeline là các *route* ngắn của cùng một luồng thay vì skill riêng tranh trigger. |
| **D** — phụ thuộc vào trừu tượng | đường dẫn trỏ tới **topic**, không tới thư mục cụ thể; brief in bảng topic → thư mục tuyệt đối từ manifest. |

### Đứng trên vai người khổng lồ — kiến thức vendored

Best practice của chính đội làm ra công cụ được chép nguyên văn vào pack, **ghim commit**, kèm `UPSTREAM.md` và
`LICENSE`. Danh sách nằm trong [`vendor.lock.json`](vendor.lock.json):

| Nguồn | Vào pack | Giấy phép |
|---|---|---|
| andrej-karpathy-skills — 4 nguyên tắc làm việc + ví dụ (bảng ánh xạ trong `aizen-core`) | `aizen-core` | MIT |
| Vercel — React & Next.js best practices (52/70 luật tác động cao nhất) | `aizen-frontend` | MIT |
| Supabase — Postgres best practices | `aizen-database` | MIT |
| PlanetScale — MySQL; Postgres MVCC/VACUUM, index audit | `aizen-database` | MIT |
| Redis Inc. — core, connections, clustering, security, observability | `aizen-database` | MIT |
| Elastic — index design, query optimization, reindex | `aizen-database` | Apache-2.0 |
| Confluent — Kafka client Java/Python | `aizen-backend` | Apache-2.0 |
| FastAPI (skill chính thức trong repo FastAPI) | `aizen-backend` | MIT |
| Julien Dubois (JHipster) — Spring Boot 4 | `aizen-backend` | Apache-2.0 |
| Docker Inc. — build, compose, destructive guardrails | `aizen-infra` | Apache-2.0 |
| KubeShark — Kubernetes failure modes | `aizen-infra` | MIT |

Thứ tự ưu tiên khi mâu thuẫn: **luật core > hướng dẫn của pack > kiến thức vendored** — upstream dạy *làm đúng thế
nào trong công cụ đó*, core quyết định *làm bao nhiêu và ai quyết*. RabbitMQ, S3, Podman, NestJS chưa có nguồn chính
thức đủ tốt (hoặc không có giấy phép) nên Aizen tự viết guide, dẫn docs chính thức.

```bash
node bin/vendor.js list            # nguồn, commit, giấy phép
node bin/vendor.js sync            # chép lại đúng các commit đã ghim
node bin/vendor.js update redis    # kéo bản mới của một nguồn — xem git diff trước khi commit
```

### Skill cộng đồng dùng trực tiếp — không chép, luôn theo bản mới

Có những skill nên dùng **nguyên bản từ cộng đồng** thay vì chép về: chúng có công cụ chạy được, có cơ chế cập nhật
riêng, và giá trị nằm ở việc theo kịp upstream. Aizen khai báo chúng trong [`externals.json`](externals.json),
pack nào dùng thì ghi trong `manifest.json` → `optional`, và luôn có đường lui khi chưa cài.

| Skill | Dùng ở | Để làm gì | Khi chưa cài |
|---|---|---|---|
| [archify](https://github.com/tt-a1i/archify) (MIT) | `aizen-design`, route design của `aizen-build` | render sơ đồ architecture / workflow / sequence / dataflow / lifecycle thành HTML tương tác, có kiểm tra tự động | sơ đồ ASCII trong tài liệu (vẫn là bản gốc) |

```bash
node bin/cli.js external list               # đã cài chưa, đang ở commit nào
node bin/cli.js external install archify    # clone vào ~/.aizen/external/archify, chạy setup khai báo (npm ci)
node bin/cli.js sync                        # liên kết nó vào thư mục skill của các agent, cạnh skill Aizen
node bin/cli.js external update archify     # liệt kê commit mới của upstream rồi cập nhật
```

Không lệnh nào tự chạy khi `npm install`, `sync` hay auto-update: cài hoặc cập nhật code bên thứ ba luôn là việc
bạn chủ động gõ. Nếu đã cài archify bằng `npx skills add tt-a1i/archify -g`, Aizen dùng luôn bản đó.

## aizen-build — điều phối production

`aizen-build` (v24) điều phối một task từ yêu cầu đến PR, **chỉ làm local** — agent không bao giờ `git push`; cuối
task bạn nhận khối lệnh push/PR để tự chạy. Hướng dẫn dùng và prompt mẫu:
[docs/huong-dan-su-dung.md](docs/huong-dan-su-dung.md) · [docs/prompt-mau.md](docs/prompt-mau.md).

**Route** — chọn ở bước đầu:

| Bạn cần | Route |
|---|---|
| tính năng, bug, refactor, ý tưởng → PR | **build** — đủ hai pha bên dưới |
| review PR / diff / branch | **review** — reviewer (+ redteam nếu chạm vùng rủi ro) ở SHA đã ghim |
| chỉ thiết kế (schema, API, kiến trúc) | **design** — planner `STAGE=design`, bạn duyệt từng phần |
| CI/CD, Docker, Kubernetes, Terraform | **build** với module `infra` cho `devops`, có security gate |

**Hai pha của route build**

| Pha | Làm gì | Bạn |
|---|---|---|
| **Thống nhất** | planner khảo sát + thiết kế, viết plan chia theo module (chốt sẵn tên, interface, dữ liệu, file, test) → bạn xác nhận **từng phần**: phạm vi → từng module → cách triển khai (các việc A3 duyệt trước) → `approve` (script **từ chối** nếu còn module chưa xác nhận) | được hỏi chi tiết từng phần |
| **Thực thi** | `dev` song song (mỗi module một worktree, code tối thiểu) → tích hợp `int/<TASK>` → tester → reviewer (+ `redteam` nếu có module rủi ro) → fix ≤ 2 vòng → tổng kết + lệnh push/PR | **không bị hỏi thêm**; chỉ khi `BLOCKED` (việc A3 chưa duyệt, A4, mất dữ liệu, plan không làm được) |

**5 role** (`agents/`)

| Role | Việc | Ghi code? |
|---|---|---|
| `planner` | khảo sát codebase, yêu cầu/thiết kế khi cần, plan chia module kèm phương án + câu hỏi từng module | không (chỉ docs/plan) |
| `dev` | làm đúng một module đã duyệt bằng code tối thiểu; `KIND=be\|fe\|db\|ui` quyết định nạp kiến thức nào | có, trong worktree riêng |
| `tester` | viết/chạy test theo lens, báo bug có bằng chứng | test |
| `reviewer` | review độc lập trên SHA đã tích hợp, read-only | không |
| `devops` | CI/CD, Docker, IaC, deploy/rollback, sự cố | file hạ tầng |

**Quy tắc chính** (`aizen-core/references/core/rules.md`): mức quyền A0–A4 (việc A3 duyệt sẵn trong plan, A4 chỉ
bạn làm), chỉ hỏi ở pha thống nhất, không tự quyết thay bạn, mọi kết luận gắn nhãn
`[verified]/[inferred]/[unverified]/[projected]`, kiểm diff/test/SHA thay vì tin báo cáo "DONE". Code: thang tái sử
dụng (YAGNI → có sẵn trong repo → stdlib → tính năng native → dependency đã có → mới viết), đánh dấu đường tắt bằng
`ponytail: <đơn giản hoá gì> — nâng cấp khi <ngưỡng đo được>`, không bao giờ cắt validation, xử lý lỗi, bảo mật, a11y.

**Scripts** (Python 3, chạy từ thư mục project bằng đường dẫn tuyệt đối):

```bash
B=~/.claude/skills/aizen-build/scripts/flow; C=~/.claude/skills/aizen-core/scripts/core
python $B/state.py init --task T-12 --goal "..."     # trạng thái task để resume; tự thêm .aizen/ vào .git/info/exclude
python $B/state.py answer --task T-12 --module api --text "B"   # ghi xác nhận từng phần
python $B/state.py approve --task T-12                # chốt plan → agent làm không hỏi thêm
python $C/check.py --task T-12 --unit api             # lint, typecheck, build, test, secrets, deps → evidence-api.json
python $C/graph.py --project .                        # code map graphify (AST, offline) → graphify-out/
python $C/capacity.py --help                          # dự phóng tải/dung lượng
```

`check.py` chỉ báo PASS khi có bước thật sự chạy và đạt; thiếu test hoặc không quét được secrets → `UNVERIFIED`
(exit 3), không bao giờ là PASS. Trạng thái và báo cáo ghi vào `.aizen/` ở gốc project (local-only).

Hỗ trợ Claude Code (Agent tool, worktree) và Antigravity (`define_subagent`/`invoke_subagent`) — chi tiết trong
`skills/aizen-build/references/flow/platform-*.md`.

### Guard — ép agent làm đủ, không làm thừa

Luật trong SKILL.md agent có thể "quên" hoặc tự cho là không cần (Claude hay bỏ bước, Antigravity hay dừng sớm).
`guard.py` chuyển quyền nói "xong" từ agent sang hook do Claude Code / Antigravity chạy — agent không bỏ qua được.
Cài **theo từng dự án**: `node bin/cli.js sync --project` (hoặc `aizen guard install`) trong thư mục dự án.

| Hook | Việc |
|---|---|
| PreToolUse | chặn sửa code khi plan chưa `approve`; chặn ghi ngoài write set của module trong `.worktrees/<unit>/`; chặn sửa file của guard (run.json, ledger, waivers, evidence) |
| PostToolUse | chấm công: ghi mọi lần ghi file / lệnh shell vào `.aizen/tasks/<TASK>/ledger.jsonl` |
| Stop | chạy checklist (`checklist` trong `aizen-build/manifest.json`); còn thiếu → agent phải làm tiếp, kèm đúng danh sách thiếu |
| git pre-push | cùng checklist cho nhánh `int/<TASK>` và `feature/<TASK>-*` |

Checklist chỉ đòi **đủ những gì plan đã chốt**: plan đã duyệt · evidence `check.py` PASS ở đúng tip của từng module
· báo cáo test · review **PASS** ghi đúng SHA hiện tại · không file nào đổi ngoài write set đã duyệt (chống
over-engineering) · `pr-body.md` khi xong. Bước thật sự không áp dụng → `aizen guard waive --task <ID> --step <id>
--reason "..."` (ghi lại, phải liệt kê trong `pr-body.md`); `plan` và `review` không miễn được. Ba lần định dừng
liền mà không làm gì thêm (hoặc 10 lần tổng) → task chuyển `blocked`, agent được dừng, bạn quyết định.

Giới hạn: hook lỗi thì cho qua (không làm kẹt agent); `--dangerously-skip-permissions` hoặc hook không chạy (đã có
báo cáo với Antigravity trên Windows) thì chỉ còn pre-push chặn. `.aizen/` là local-only nên CI không chạy được
checklist — pre-push là chốt cuối. Bật chế độ chặt (`{"require_task": true}` trong `.aizen/guard.json`) để cấm sửa
code khi chưa có task được duyệt.

## Cấu trúc repo

```text
.
├── docs/                      # hướng dẫn sử dụng, prompt mẫu, chuẩn viết skill
├── skills/<skill>/            # chỉ SKILL.md + manifest.json là bắt buộc; thư mục khác có khi có nội dung
│   ├── SKILL.md               #   điểm vào: front-matter name/description + hướng dẫn
│   ├── manifest.json          #   name, version, kind (entry|pack), topics, requires
│   ├── rules/ agents/         #   luật riêng, prompt sub-agent (entry)
│   ├── references/<topic>/    #   kiến thức nạp theo nhu cầu; vendor/<nguồn>/ = kiến thức upstream ghim commit
│   ├── assets/<topic>/        #   template
│   └── scripts/<topic>/       #   mã chạy được (Python stdlib)
├── rules/                     # rule toàn cục cho mọi session agent (working-principles.md, continuous-improvement.md)
├── bin/                       # cli.js, install.js, updater.js, agents-config.js, vendor.js
├── tests/                     # check-skills.js (lint + sổ topic), check-scripts.js (smoke test Python), test-installer.js
├── vendor.lock.json           # nguồn, commit, giấy phép của kiến thức vendored (chép, ghim commit)
├── externals.json             # skill cộng đồng dùng trực tiếp (không chép, theo bản mới)
├── plugin.json                # manifest plugin Antigravity
└── package.json
```

`tests/check-skills.js` kiểm: manifest (`kind`, `topics` không trùng, `requires` tồn tại), tên khớp thư mục,
`description` ≤ 1024 ký tự và có "Not for:" (entry), mọi đường dẫn `` `references|assets|scripts/<topic>/…` `` resolve
qua sổ topic, link markdown tương đối tồn tại, `(vNN)` khớp `manifest.version`, mỗi `vendor/<nguồn>/` có
`UPSTREAM.md` + `LICENSE`, không còn tên cũ.

## Nâng cấp từ bản trước (đổi tên)

| Cũ | Mới |
|---|---|
| `cecilia-coding-skills` | `aizen-build` |
| `cecilia-discover-design` / `-backend` / `-frontend` / `-db` / `-quality` / `-infra` | `aizen-design` / `aizen-backend` / `aizen-frontend` / `aizen-database` / `aizen-quality` / `aizen-infra` |
| `adversarial-code-reviewer` | route **review** của `aizen-build` (+ `aizen-quality` §0 blast radius) |
| `database-table-design` | `aizen-database` (`schema-design.md` — quy ước team chọn một lần) |
| `devsecops-pipeline-flow` | `aizen-infra` (security gates, Cloudflare, Docker Hub, `pipeline_scaffold.py`) |
| `thanhtan-backend-coding-init` | `aizen-init` |
| `skill-creator` / `skill-cloner` / `agent-skill-tester` | `aizen-skill-creator` / `aizen-skill-importer` / `aizen-skill-eval` |
| `tech-learning-tree` / `video-to-skill` | `aizen-tech-learning` / `aizen-video-to-skill` |
| workspace `tensura/`, `.thanhtan/` | `.aizen/`, `.aizen/init/` |

`git pull && node bin/cli.js sync` dọn link tên cũ và tạo link tên mới. Task đang dở trong `tensura/`: đổi tên thư
mục thành `.aizen/` rồi `state.py status --task <TASK>`.

## CLI

Chạy bằng `node bin/cli.js <lệnh>` (hoặc `aizen <lệnh>` nếu đã `npm link`):

| Lệnh | Việc |
|---|---|
| `status` | liệt kê skill và số liên kết ở từng agent |
| `sync` / `install` | liên kết skills, chép rules, đăng ký plugin; `--project` để cài vào project hiện tại |
| `check` | kiểm tra có bản mới không |
| `update` | kéo bản mới (git) rồi sync |
| `auto-update enable\|disable` | bật/tắt cập nhật ngầm hằng ngày (Task Scheduler / cron) — chỉ repo Aizen, không đụng skill cộng đồng |
| `external list\|install\|update\|remove <tên>` | skill cộng đồng trong `externals.json` |
| `guard install\|check\|waive` | hook ép quy trình aizen-build cho dự án hiện tại ([Guard](#guard--ép-agent-làm-đủ-không-làm-thừa)) |
| `help` | trợ giúp |

## Phát triển skill

Chuẩn đầy đủ: [docs/aizen-skill-standard.md](docs/aizen-skill-standard.md) (entry/pack, topic, `description`,
`manifest.json`, vendored knowledge, scripts, tài liệu bắt buộc, git).

1. Tạo skill mới: `/aizen-skill-creator` · đưa skill hoặc kiến thức bên ngoài vào: `/aizen-skill-importer` (prompt
   mẫu trong [docs/prompt-mau.md](docs/prompt-mau.md)). Trước khi tạo skill mới, hỏi: đây là **entry** mới hay chỉ là
   một **topic** cho pack đã có?
2. Mỗi entry phải có: một dòng trong bảng [Danh sách skill](#danh-sách-skill), dòng trong `docs/huong-dan-su-dung.md`
   (§2, §4) và một prompt `/<tên>` trong `docs/prompt-mau.md` — `npm test` kiểm.
3. `description` quyết định khi nào agent chọn skill: làm gì · "Use when …" · "Not for: …".
4. Thư mục tạm (baseline, kết quả eval) ở `.aizen-work/` — không bao giờ trong `skills/`.
5. Kiểm tra rồi đồng bộ:

```bash
npm test               # check-skills.js + check-scripts.js + test-installer.js
node bin/cli.js sync
```

**Skill tự cải thiện** (`rules/continuous-improvement.md`): khi một skill làm chưa tốt (bạn phàn nàn, script lỗi,
hướng dẫn sai, phải làm tay), agent ghi một dòng vào sổ `.aizen-work/feedback/<skill>.jsonl` bằng
`aizen-skill-creator/scripts/authoring/feedback.py` — không hỏi, không chen task. Chỉ khi bạn phàn nàn trực tiếp, vấn
đề lặp ≥ 2 lần, hoặc skill ra kết quả sai, agent mới đề xuất sửa; sửa đi qua quy trình improve của
`aizen-skill-creator` (baseline, eval case mới, bump version, `npm test`, commit). Xem sổ:
`python skills/aizen-skill-creator/scripts/authoring/feedback.py list --open`.
Cursor (`sync --project`) nhận rule dưới dạng `.mdc` `alwaysApply`; Windsurf/Gemini CLI chưa được cài rule tự động.

## Gỡ cài đặt

Xóa các liên kết (không xóa repo): các mục trùng tên skill trong những thư mục ở bảng [Cài đặt](#cài-đặt),
`~/.gemini/config/plugins/aizen-skills`, các file `working-principles.md`, `continuous-improvement.md` trong `~/.gemini/config/rules/` và `~/.claude/rules/`. Trên Windows dùng
`rmdir <link>` (xóa junction, không đụng thư mục gốc). Tắt cập nhật ngầm: `node bin/cli.js auto-update disable`.

## Giấy phép

[MIT](LICENSE). Riêng `skills/aizen-skill-creator` và phần grader/benchmark của `skills/aizen-skill-eval` dựa trên
skill của Anthropic, giữ giấy phép Apache 2.0 (`LICENSE.txt` trong mỗi thư mục). Kiến thức vendored giữ giấy phép
gốc trong `LICENSE` của từng thư mục `vendor/<nguồn>/` (xem `vendor.lock.json`).

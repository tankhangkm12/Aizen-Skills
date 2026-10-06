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
- [Hợp đồng chung và bản đồ dự án](#hợp-đồng-chung--agent-làm-đủ-không-làm-thừa-có-bằng-chứng)
- [Nâng cấp dự án đang chạy](#nâng-cấp-dự-án-đang-chạy)
- [Nâng cấp từ bản trước](#nâng-cấp-từ-bản-trước-đổi-tên)
- [Cấu trúc repo](#cấu-trúc-repo)
- [CLI](#cli)
- [Phát triển skill](#phát-triển-skill)
- [Gỡ cài đặt](#gỡ-cài-đặt)
- [Giấy phép](#giấy-phép)

## Cài đặt

Yêu cầu: **Node.js ≥ 18** (cho `npx`) và **[uv](https://docs.astral.sh/uv/)**. Không cần cài Python: mọi script của
Aizen có header [PEP 723](https://peps.python.org/pep-0723/) và chạy bằng `uv run`, uv tự tải Python phù hợp.

```bash
winget install astral-sh.uv                        # Windows
curl -LsSf https://astral.sh/uv/install.sh | sh    # macOS / Linux
```

Cài xong uv, mở terminal mới (và khởi động lại Antigravity / Claude Code) để PATH có `uv`.

### Cách 1 — Dùng: cài cho một dự án qua skills.sh (khuyến nghị)

Chạy trong thư mục gốc của dự án (đã `git init`):

```bash
npx skills add tankhangkm12/Aizen-Skills -a antigravity -s '*' -y      # chép 15 skill vào ./.agents/skills
uv run .agents/skills/aizen-core/scripts/core/guard.py install         # hook, git pre-push, session rules, .aizen/
```

- `-a antigravity` → `./.agents/skills/`; thêm agent khác bằng `-a antigravity claude-code` (Claude Code →
  `./.claude/skills/`). Không có `-g` nên **chỉ dự án này** thấy Aizen.
- **Chỉ cài cho Claude Code** (`-a claude-code`): skill nằm ở `.claude/skills/`, nên bước setup là
  `uv run .claude/skills/aizen-core/scripts/core/guard.py install`.
- Bước `guard.py install` ghi hook dạng `uv run --script "<dự án>/.agents/skills/aizen-core/…/guard.py" hook …` vào
  `.agents/hooks.json` (Antigravity), `.claude/settings.local.json` (Claude Code) và `.git/hooks/pre-push`; chép luật
  phiên làm việc vào `.agents/rules/` (front-matter `trigger: always_on`) và `.claude/rules/`. Quên bước này cũng
  không sao: skill entry tự chạy nó ở bước đầu (`aizen-core/references/core/rules.md` → Setup).
- Cập nhật: `npx skills update` rồi chạy lại `guard.py install`. Chuyển thư mục dự án đi chỗ khác → chạy lại
  `guard.py install` (hook dùng đường dẫn tuyệt đối tới bản trong dự án).
- Skill cộng đồng dùng kèm, ví dụ archify: `npx skills add tt-a1i/archify -a antigravity -y`.

### Cách 2 — Phát triển Aizen: clone và liên kết (live-sync)

Dùng khi bạn sửa chính bộ skill: dự án liên kết (junction/symlink) vào repo nên sửa trong repo là agent thấy ngay.

```bash
git clone https://github.com/tankhangkm12/Aizen-Skills.git
cd Aizen-Skills
npm install                                        # chỉ tải; không tự liên kết vào agent nào
cd /path/to/du-an && node /path/to/Aizen-Skills/bin/cli.js sync --project
```

`sync --project` (mặc định của `sync`) liên kết vào `./.agents/skills`, `./.claude/skills`, tạo `./.cursor/rules/*.mdc`,
cập nhật `AGENTS.md`, rồi chạy `guard.py install` như Cách 1.

Muốn cài cho **mọi dự án trên máy** thì phải gõ rõ `node bin/cli.js sync --global`. Lệnh này liên kết vào:

| Agent | Thư mục |
|---|---|
| Universal (`.agents`) | `~/.agents/skills` |
| Claude Code | `~/.claude/skills` |
| Antigravity CLI | `~/.gemini/antigravity-cli/skills` |
| Gemini CLI | `~/.gemini/skills` |
| Antigravity config | `~/.gemini/config/skills` |
| Cursor | `~/.cursor/skills` |
| Windsurf | `~/.codeium/windsurf/skills` |

và chép luật phiên làm việc (`skills/aizen-core/rules/*.md`) vào `~/.gemini/config/rules/` (có front-matter
`trigger: always_on`, thiếu nó Antigravity bỏ qua file) và `~/.claude/rules/`, đăng ký repo làm plugin Antigravity tại
`~/.gemini/config/plugins/aizen-skills`.

- **Windows** dùng NTFS junction (không cần quyền Admin); **Linux/macOS** dùng symlink và `chmod 755` cho scripts.
- Thư mục thật trùng tên (skill bạn tự viết) **không bị ghi đè** — bộ cài chỉ cảnh báo.
- Liên kết trỏ tới skill đã xóa/đổi tên được dọn khi chạy `sync`.

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
| [`aizen-init`](skills/aizen-init) | Khởi tạo dự án backend cho team từ repo + tài liệu theo 11 bước có checkpoint: Git Flow, plan trong `.aizen/runs/init/`, khung code + health check, Docker/compose kèm infra, config tập trung, kết nối infra fail-fast, adapter, AOP + request-id + auth, README, rà lại bằng graphify. |
| [`aizen-prompt-architect`](skills/aizen-prompt-architect) | Phỏng vấn bạn vài câu rồi viết prompt Aizen đủ trường (task, tên nghiệp vụ, mục tiêu, tiêu chí xong, phạm vi, quyền, điểm dừng, gợi ý case kiểm thử). Có bản một file [`docs/aizen-web-kit.md`](docs/aizen-web-kit.md) để dán vào ChatGPT, Gemini, Claude chat, DeepSeek. |
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

- **Mọi session agent trong dự án** — `skills/aizen-core/rules/working-principles.md` được `guard.py install` chép vào
  `.agents/rules/` (Antigravity) và `.claude/rules/` (Claude Code) của dự án; `sync --global` chép cho cả máy; `.mdc` cho Cursor khi `sync --project`.
- **Trong các skill Aizen** — mỗi nguyên tắc có chỗ thực thi và chỗ kiểm (bảng trong `skills/aizen-core/SKILL.md`):

| Nguyên tắc | Aizen thực thi bằng |
|---|---|
| Nghĩ trước khi code | câu hỏi chỉ ở pha plan, có phương án + mặc định; dòng "Simpler option"; `approve` chặn module chưa xác nhận |
| Đơn giản trước | thang tái sử dụng, không trừu tượng cho code dùng một lần, không phòng thủ trạng thái không thể xảy ra, câu hỏi "200 → 50" |
| Sửa như phẫu thuật | mọi dòng đổi phải truy về yêu cầu; chỉ dọn rác của chính mình, code chết có sẵn thì ghi vào `## Proposals` |
| Thực thi theo mục tiêu | Done của module thành check chạy được trước khi code, test fail trước, `step → verify` |

**Cách suy luận** — `skills/aizen-core/rules/reasoning.md` cũng được cài như session rule (cả Antigravity lẫn Claude
Code): nêu lại vấn đề, tách sự thật khỏi phỏng đoán, ≥ 2 phương án cho quyết định khó đảo ngược, hỏi "hỏng thế
nào?", bước nhỏ nhất rồi kiểm, ghi quyết định vào nhật ký. Bản đầy đủ kèm playbook (bug, thiết kế, công cụ lạ, hiệu
năng, dữ liệu/tiền/đồng thời, bị kẹt): `skills/aizen-core/references/core/reasoning.md`.

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

`aizen-build` (v26) điều phối một task từ yêu cầu đến PR, **chỉ làm local** — agent không bao giờ `git push`; cuối
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
| **Thống nhất** | planner khảo sát + thiết kế, viết plan chia theo module (chốt sẵn tên, interface, dữ liệu, file, test) và bộ test case nghiệm thu `acceptance.md` → bạn xác nhận **từng phần**: phạm vi → test case → từng module → cách triển khai (các việc A3 duyệt trước) → `approve` (script **từ chối** nếu còn module chưa xác nhận) | được hỏi chi tiết từng phần |
| **Thực thi** | `dev` song song (mỗi module một worktree, code tối thiểu) → tích hợp vào nhánh PR `<type>/<slug>` → tester → reviewer (+ `redteam` nếu có module rủi ro) → fix ≤ 2 vòng → tổng kết + lệnh push/PR | **không bị hỏi thêm**; chỉ khi `BLOCKED` (việc A3 chưa duyệt, A4, mất dữ liệu, plan không làm được) |

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

**Scripts** (chạy bằng `uv run`, từ thư mục project, đường dẫn tuyệt đối):

```bash
B=~/.claude/skills/aizen-build/scripts/flow; C=~/.claude/skills/aizen-core/scripts/core
uv run $B/state.py init --task T-12 --goal "..." --slug giu-ghe   # slug = tên nghiệp vụ của nhánh
uv run $B/state.py branch --task T-12 [--unit api]   # feature/giu-ghe[-api] — không bao giờ là mã run
uv run $C/journal.py note --run T-12 --kind think --text "Tôi đang nghĩ …" --as planner   # một dòng ở điểm quyết định
uv run $C/journal.py report                           # → .aizen/out/latest.md
uv run $B/state.py answer --task T-12 --module api --text "B"   # ghi xác nhận từng phần
uv run $B/state.py approve --task T-12                # chốt plan → agent làm không hỏi thêm
uv run $C/check.py --task T-12 --unit api             # lint, typecheck, build, test, secrets, deps → evidence-api.json
uv run $C/graph.py --project .                        # code map graphify (AST, offline) → graphify-out/
uv run $C/capacity.py --help                          # dự phóng tải/dung lượng
```

`check.py` chỉ báo PASS khi có bước thật sự chạy và đạt; thiếu test hoặc không quét được secrets → `UNVERIFIED`
(exit 3), không bao giờ là PASS. Trạng thái và báo cáo ghi vào `.aizen/` ở gốc project (local-only).

**Theo dõi agent bằng file, không bằng terminal** (v26):

| Bạn muốn | Mở | Ghi bởi |
|---|---|---|
| đọc nhanh / dán cho AI web | `.aizen/out/latest.md` (bản cũ ở `out/history/`) | `journal.py report`, tự chạy khi duyệt plan, sang vòng sửa, bị chặn, xong |
| xem agent nghĩ gì, làm gì, dừng ở đâu | `.aizen/runs/<TASK>/journal.md` — mỗi dòng một câu: 🧠 nghĩ · 🔧 thử · 🔀 chọn · ✍ đã ghi · ▶ đã chạy · ✅ xong · ⛔ dừng | agent (`journal.py note`) ở điểm quyết định; hook tự ghi ✍/▶ |
| test không thiên vị | `.aizen/runs/<TASK>/acceptance.md` — test case `TC-nn` bạn duyệt cùng plan, khoá khi approve | planner viết, tester làm, dev không được đụng |

**GitHub sạch** (v26): file của agent (`.claude/`, `.agents/`, `AGENTS.md`, `CLAUDE.md`, `.aizen/`…) chỉ nằm ở
máy (`.git/info/exclude`); nhánh mang tên nghiệp vụ (`feature/giu-ghe`, không `feature/T-12-api`); commit không
gắn mã run hay dòng đồng tác giả AI — pre-push chặn và in lệnh sửa. Tắt: `"hide_ai_files": false` trong
`.aizen/config/guard.json`. Chi tiết: [docs/huong-dan-su-dung.md](docs/huong-dan-su-dung.md).

**Song song có đo đạc.** `state.py waves --task <TASK>` xếp các module thành đợt từ write set và `after:` của plan:
module chung file thì chạy sau, mỗi đợt tối đa `parallel.max` (mặc định 2 — mỗi unit cần worktree, port, container,
DB riêng trên một máy). Sau run, `journal.py stats --run <TASK>` (và mục "Thời gian" trong `.aizen/out/latest.md`)
cho biết từng sub-agent làm lúc nào và hệ số song song: gần 1.0× là đang chờ nhau → lần sau gộp module; cao hơn rõ
và merge sạch → có thể tăng `"parallel": {"max": 3}` trong `.aizen/config/guard.json`.

Hỗ trợ Claude Code (Agent tool, worktree) và Antigravity (`define_subagent`/`invoke_subagent`) — chi tiết trong
`skills/aizen-build/references/flow/platform-*.md`.

### Tài liệu cho team: `docs/`

Tài liệu thiết kế (SRS, kiến trúc, module, API, dữ liệu, hạ tầng) nằm trong `docs/` theo một bố cục cố định, được
commit và đọc được trên GitHub; việc riêng của agent (plan, run, nhật ký, `decisions.md`, `lessons.md`) vẫn ở
`.aizen/`. Dự án mới mặc định như vậy (`"docs": "docs"` trong `.aizen/config/guard.json`).

```
docs/README.md   mục lục (phần trên viết tay, bảng dưới do docs.py sinh)
docs/product/    ý tưởng, SRS, user story, kế hoạch kiểm thử
docs/architecture/   kiến trúc, luồng, bảo mật · modules/<m>.md · adr/NNNN-<slug>.md
docs/api/        <m>.md + <m>.yaml       docs/data/   ERD, bảng, ddl.sql
docs/ui/         frontend, màn hình      docs/ops/    hạ tầng, biến môi trường, runbook
docs/guides/     onboarding, cách chạy   docs/services/<svc>/   microservice
```

`aizen-core/scripts/core/docs.py`: `where <tên>` (đường dẫn đúng của một tài liệu) · `index` (dựng lại mục lục) ·
`check` (bố cục, tiêu đề, dòng tóm tắt, link hỏng, nhắc tới `.aizen/` hay mã run) · `migrate [--apply]` (dự án cũ:
chuyển `.aizen/knowledge/` và file rời trong `docs/` vào bố cục bằng `git mv`). Quy tắc viết:
`skills/aizen-core/references/core/docs.md`.

## Hợp đồng chung — agent làm đủ, không làm thừa, có bằng chứng

Luật viết trong SKILL.md agent có thể "quên" hoặc tự cho là không cần (Claude hay bỏ bước, Antigravity hay dừng
sớm). Vì vậy **mọi entry skill** khai báo một `contract` trong `manifest.json`, và **một engine chung**
(`skills/aizen-core/scripts/core/guard.py`) thi hành nó qua hook của Claude Code / Antigravity và git pre-push —
agent không bỏ qua được. Thêm skill mới chỉ cần khai báo `contract`; `npm test` từ chối entry skill thiếu nó.

Cài **theo từng dự án**: `node bin/cli.js sync --project` (hoặc `aizen guard install`) trong thư mục dự án. Lần đầu
nó tự chuyển `.aizen/` kiểu cũ sang cấu trúc mới.

| Phần của contract | Agent làm | Ai kiểm |
|---|---|---|
| `steps` → `runs/<RUN>/sheet.md` | tích từng bước kèm bằng chứng: `file:` · `cmd:` · `out:"…"` · `sha:` · `url:` | script: file có thật và mới, lệnh có trong ledger và đạt, dòng output thật sự được in, commit tồn tại, URL được trích trong đầu ra. Tích mà không có bằng chứng → trượt |
| `rules` | — | script tất định: `count` · `per_block` (≤ N node/diagram) · `labels` (claim có số phải gắn `[verified]/[inferred]/[unverified]/[projected]` hoặc nguồn) · `sections` · `regex` · `command` (vd. `check_tree.py`); aizen-build thêm `approved` · `acceptance` · `evidence` · `report` · `scope` · `knowledge`; mọi skill: `journal` (có sửa file thì phải có dòng suy nghĩ) |
| `expectations` + `verifier` | dispatch một verifier **sạch** (`references/core/verifier.md`) | verifier độc lập ghi `verdict.json`; guard kiểm người ghi khác người làm, mỗi mục đạt có `path:line` có thật, tỷ lệ ≥ 80% |

| Hook | Việc |
|---|---|
| PreToolUse | chặn sửa file của guard (run.json, ledger, waivers, evidence, PROJECT.md); chặn ghi đầu ra/code trước khi bạn xác nhận; chặn ghi ngoài write set của module; chặn agent tự duyệt backlog |
| PostToolUse | chấm công: ghi mọi lần ghi file / lệnh shell vào `ledger.jsonl` của run, kèm **ai** làm (sub-agent nào); thêm dòng ✍/▶ dễ đọc vào `journal.md` |
| Stop | chạy contract; còn thiếu → agent làm tiếp với đúng danh sách; đủ → run `done`, vào `archive/`, backlog `done`, `PROJECT.md` cập nhật. Ba lần dừng liền không làm gì thêm, hoặc quá số vòng verifier → `blocked`, bạn quyết |
| git pre-push | chạy lại contract cho nhánh của run (`<type>/<slug>[-<unit>]`); với **mọi** nhánh: chặn file AI trong cây và mã run / dòng đồng tác giả AI trong commit chưa push |

Bước thật sự không áp dụng → `guard.py waive --run <RUN> --step <id> --reason "…" --evidence <file | 1 dòng output>`
(file được băm, sửa sau là mất hiệu lực). Waiver chỉ tính khi verifier (hoặc reviewer) ghi `accepted`.

### `.aizen/` và bản đồ dự án

```
.aizen/
├── PROJECT.md      👁 bản đồ dự án — file duy nhất bạn đọc (máy biên soạn, có mục lục)
├── out/            👁 latest.md — báo cáo mới nhất, dán thẳng cho AI web · history/
├── backlog.md      ✍ việc sắp làm BL-nn (agent đề xuất, chỉ bạn duyệt)
├── config/         guard.json · conventions.md
├── knowledge/      decisions.md · lessons.md (+ system/ · modules/ khi tài liệu thiết kế chưa chuyển ra docs/)
├── runs/<RUN>/     run.json · state.md · plan.md · acceptance.md · journal.md · sheet.md · ledger.jsonl · waivers.json · evidence/ · reports/ · verdict.json · work/
├── worktrees/ · cache/ · backups/ · archive/
```

`PROJECT.md`: 0 Cần bạn ngay · 1 Tổng quan · 2 Kiến trúc · 3 Luồng nghiệp vụ · 4 Module · 5 Dữ liệu · 6 Hạ tầng ·
7 Quy ước · 8 Quyết định · 9 Bài học · 10 Quy trình agent (sơ đồ + contract từng skill) · 11 Việc của agent (đang
làm / sắp làm / đã làm) · 12 Cách điều khiển · 13 Nguồn. Nội dung lấy từ `knowledge/`, `config/`, `backlog.md`,
`runs/` — sửa nguồn, bản đồ tự theo; aizen-build không xong khi code đổi mà `knowledge/` chưa ghi lại.
Chi tiết: `skills/aizen-core/references/core/workspace.md`.

Giới hạn: hook lỗi thì cho qua (không làm kẹt agent); `--dangerously-skip-permissions` hoặc hook không chạy (đã có
báo cáo với Antigravity trên Windows) thì chỉ còn pre-push chặn. `.aizen/` là local-only nên CI không kiểm được run.
Kiểm `path:line` chứng minh dòng có thật, không chứng minh nhận xét đúng.

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
├── bin/                       # cli.js, install.js, updater.js, agents-config.js, vendor.js
├── tools/upgrade/            # aizen-upgrade.bat / .sh — nâng cấp Aizen trong một dự án đang chạy
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

## Nâng cấp dự án đang chạy

Dự án đã cài Aizen bằng skills.sh và muốn lên bản mới, không mất `.aizen/`, không mất task đang dở. Script nằm ở
[`tools/upgrade/`](tools/upgrade): `aizen-upgrade.bat` (Windows cmd / PowerShell) và `aizen-upgrade.sh` (Linux,
macOS, Git Bash, WSL). Đặt script **ngoài** thư mục dự án, chạy từ trong dự án:

```powershell
D:\tools\aizen-upgrade.bat check develop        # chỉ kiểm tra, không đổi gì
D:\tools\aizen-upgrade.bat upgrade develop      # sao lưu → nhánh chore/untrack-agent-files → skills update → guard install
# merge PR chore/untrack-agent-files vào develop trên GitHub, rồi:
D:\tools\aizen-upgrade.bat after-merge develop  # về develop, pull, khôi phục skill vừa cài
```

| Lệnh | Làm gì |
|---|---|
| `check` | nhánh, phiên bản Aizen, cây sạch chưa, file AI nào đang bị git theo dõi, commit chưa push có mã task / dòng đồng tác giả AI, run đang dở |
| `upgrade` | sao lưu `.agents`, `.claude`, `.aizen`, `skills-lock.json` vào `~/aizen-backups/<repo>-<giờ>/before`; gỡ file AI khỏi git trên nhánh `chore/untrack-agent-files` (file vẫn còn trên máy); `npx skills update -p`; `guard.py install`; lưu bản đã cài; hỏi trước khi push / mở PR |
| `finish` | chạy tiếp bước 4–6 nếu `upgrade` dừng sau bước cập nhật skill (không sao lưu lại) |
| `after-merge` | sau khi PR được merge: về nhánh gốc, pull, xoá nhánh chore ở máy, chép lại skill vừa cài |
| `restore` | checkout một nhánh cũ còn theo dõi `.agents`/`.claude` đã ghi đè skill → chép lại bản mới |
| `rollback` | trả skill, rules và `.aizen` về đúng như trước khi nâng cấp |

Không force-push, không viết lại lịch sử: commit cũ trên GitHub vẫn còn file AI. Máy khác cùng clone repo: chạy
`upgrade` (đừng `git pull` trước) — pull commit gỡ file AI sẽ xoá skill đang bị theo dõi khỏi ổ đĩa, `upgrade` sao
lưu trước rồi cài lại.

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
| workspace `tensura/`, `.thanhtan/` | `.aizen/`, `.aizen/runs/init/` |

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
| `guard install\|check\|stop` | hợp đồng chung cho dự án hiện tại ([Hợp đồng chung](#hợp-đồng-chung--agent-làm-đủ-không-làm-thừa-có-bằng-chứng)) |
| `project` | biên soạn lại `.aizen/PROJECT.md` |
| `backlog list\|add\|approve\|drop` | việc sắp làm (chỉ bạn duyệt) |
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
4. Thư mục tạm (baseline, kết quả eval) ở `.aizen/cache/` — không bao giờ trong `skills/`.
5. Kiểm tra rồi đồng bộ:

```bash
npm test               # check-skills.js + check-scripts.js + test-installer.js
node bin/cli.js sync
```

**Skill tự cải thiện** (`skills/aizen-core/rules/continuous-improvement.md`): khi một skill làm chưa tốt (bạn phàn nàn, script lỗi,
hướng dẫn sai, phải làm tay), agent ghi một dòng vào sổ `.aizen/knowledge/feedback/<skill>.jsonl` bằng
`aizen-skill-creator/scripts/authoring/feedback.py` — không hỏi, không chen task. Chỉ khi bạn phàn nàn trực tiếp, vấn
đề lặp ≥ 2 lần, hoặc skill ra kết quả sai, agent mới đề xuất sửa; sửa đi qua quy trình improve của
`aizen-skill-creator` (baseline, eval case mới, bump version, `npm test`, commit). Xem sổ:
`uv run skills/aizen-skill-creator/scripts/authoring/feedback.py list --open`.
Cursor (`sync --project`) nhận rule dưới dạng `.mdc` `alwaysApply`; Windsurf/Gemini CLI chưa được cài rule tự động.

## Gỡ cài đặt

Một dự án cài bằng skills.sh: `npx skills remove` trong dự án, xoá khối `aizen-guard` trong `.agents/hooks.json`,
hook có `guard.py` trong `.claude/settings.local.json`, file `.git/hooks/pre-push` của Aizen và `.agents/rules/aizen-*.md`.

Bản `sync --global`: xóa các liên kết (không xóa repo): các mục trùng tên skill trong những thư mục ở bảng [Cài đặt](#cài-đặt),
`~/.gemini/config/plugins/aizen-skills`, các file `working-principles.md`, `continuous-improvement.md` trong `~/.gemini/config/rules/` và `~/.claude/rules/`. Trên Windows dùng
`rmdir <link>` (xóa junction, không đụng thư mục gốc). Tắt cập nhật ngầm: `node bin/cli.js auto-update disable`.

## Giấy phép

[MIT](LICENSE). Riêng `skills/aizen-skill-creator` và phần grader/benchmark của `skills/aizen-skill-eval` dựa trên
skill của Anthropic, giữ giấy phép Apache 2.0 (`LICENSE.txt` trong mỗi thư mục). Kiến thức vendored giữ giấy phép
gốc trong `LICENSE` của từng thư mục `vendor/<nguồn>/` (xem `vendor.lock.json`).

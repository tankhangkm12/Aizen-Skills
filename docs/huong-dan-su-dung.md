# Hướng dẫn sử dụng Aizen Skills

Tài liệu này hướng dẫn cách dùng bộ skill hiệu quả nhất: agent nhận đủ thông tin ngay từ đầu nên không phải
đoán, không hỏi lại những gì bạn đã biết, và tập trung vào đúng việc. Prompt mẫu để copy: [prompt-mau.md](prompt-mau.md).

## 1. Cài và kiểm tra

Cần Node.js ≥ 18 và [uv](https://docs.astral.sh/uv/) (`winget install astral-sh.uv` trên Windows). Không cần cài
Python: script Aizen chạy bằng `uv run`, uv tự tải Python. Trong thư mục gốc của dự án:

```bash
npx skills add tankhangkm12/Aizen-Skills -a antigravity -s '*' -y   # chỉ dự án này; thêm claude-code nếu dùng
uv run .agents/skills/aizen-core/scripts/core/guard.py install      # hook, pre-push, session rules, .aizen/
```

Chỉ dùng Claude Code: `-a claude-code`, và bước setup dùng `.claude/skills/…/guard.py` thay cho `.agents/skills/…`.

Mở **session mới** của agent. Kiểm tra: gõ `/aizen-build`, hoặc hỏi "liệt kê các skill bạn có", và xem
`.agents/hooks.json` có lệnh `uv run --script …guard.py hook …`. Cập nhật: `npx skills update` rồi chạy lại `guard.py install`.

Skill cộng đồng dùng kèm, ví dụ archify (sơ đồ HTML tương tác, cần Chrome): `npx skills add tt-a1i/archify -a antigravity -y`.

Sửa chính bộ skill (live-sync): clone repo, `npm install` (chỉ tải, không tự liên kết), rồi trong dự án
`node <repo>/bin/cli.js sync --project` — xem README › Cài đặt › Cách 2. Graphify (code map) được đề nghị cài khi
cần (`uv tool install graphifyy`) — bạn duyệt một lần. Cài cả bộ: mọi entry dùng luật chung ở `aizen-core`.

## 2. Gọi skill

- **Tự động**: agent chọn skill theo nội dung prompt. Dùng đúng từ khoá trong bảng dưới cho chắc.
- **Gọi thẳng** (chắc chắn nhất): Claude Code `/<tên-skill> <prompt>`; agent khác: "Dùng skill `<tên>` để …".

| Bạn muốn | Skill | Từ khoá trong prompt |
|---|---|---|
| làm tính năng, sửa bug, refactor tới PR | `aizen-build` (route build) | "làm tính năng", "sửa bug", "từ ý tưởng tới PR" |
| review PR / diff / code AI viết | `aizen-build` (route review) | "review PR", "audit diff" |
| thiết kế bảng, API, kiến trúc (chưa code) | `aizen-build` (route design) | "thiết kế bảng", "thiết kế API", "DDL" |
| CI/CD bảo mật, Docker, Kubernetes, deploy | `aizen-build` (module infra) | "pipeline CI/CD", "DevSecOps", "Dockerfile", "k8s" |
| khởi tạo dự án backend mới cho team (khung, Docker, infra, health check) | `aizen-init` | "khởi tạo dự án backend", "dựng khung backend", "init backend" |
| tạo skill mới / cải thiện skill trong repo | `aizen-skill-creator` | "tạo skill", "cải thiện skill <tên>" |
| chép skill từ GitHub/thư mục khác, hoặc vendor best practice của upstream vào pack | `aizen-skill-importer` | "clone skill" + link, "học theo skill" |
| đánh giá một skill | `aizen-skill-eval` | "test skill", "benchmark skill" |
| hiểu sâu một công nghệ, so sánh kiến trúc → Notion | `aizen-tech-learning` | "nghiên cứu", "vì sao X nhanh", "so sánh kiến trúc X và Y" |
| biến video thành skill | `aizen-video-to-skill` | link YouTube / file video |

`aizen-core`, `aizen-design`, `aizen-backend`, `aizen-frontend`, `aizen-database`, `aizen-quality`, `aizen-infra` là
knowledge pack — **không gọi trực tiếp**, `aizen-build` tự nạp đúng topic cho từng role.

## 3. Làm việc với aizen-build

### Route

| Bạn cần | Route | Bạn được hỏi |
|---|---|---|
| tính năng, bug, refactor | build — đủ hai pha bên dưới | từng phần của plan |
| review PR / diff / branch | review — reviewer (+ redteam) ở SHA đã ghim, chỉ đọc | không, trừ khi thiếu mục tiêu của thay đổi |
| thiết kế schema / API / kiến trúc | design — planner viết tài liệu, dừng ở đó | từng phần của tài liệu |
| CI/CD, Docker, k8s | build với module `infra` cho `devops` | như build; mọi lệnh lên môi trường thật là A3/A4 |

### Luồng build — hai pha

```
Pha THỐNG NHẤT (bạn được hỏi kỹ)              Pha THỰC THI (không hỏi bạn nữa)
S0 tiếp nhận + code map                      S3 dev song song, mỗi module một worktree, code tối thiểu
S1 planner khảo sát, thiết kế, chia module,  S4 tích hợp vào nhánh PR (vd. feature/giu-ghe)
   viết bộ test case nghiệm thu             S5 tester   S6 reviewer (+ redteam nếu rủi ro)
S2 xác nhận từng phần:                       S7 tự sửa ≤ 2 vòng
   phạm vi → test case → module 1 → …
   → triển khai (duyệt trước các việc A3)    S8 tổng kết + khối lệnh push/PR để bạn chạy
   → approve
```

- **Pha thống nhất**: mỗi lượt hỏi chỉ về một phần, có phương án đề xuất đứng đầu. Muốn đổi gì cứ nói — agent
  sửa plan và hỏi lại **đúng phần đó**. Chốt bằng câu "approve plan".
- **Pha thực thi**: plan đã duyệt là hợp đồng. Agent không hỏi nữa; chi tiết nhỏ plan chưa nói thì chọn cách đơn
  giản nhất và liệt kê ở `Deviations:` trong báo cáo. Bạn chỉ bị gọi lại khi `BLOCKED`: cần việc A3 chưa duyệt,
  việc A4 (push, merge, production, secret…), nguy cơ mất dữ liệu, hoặc plan không làm được.
- Agent **không bao giờ push**. Cuối task bạn nhận khối lệnh `git push` + `gh pr create --draft` để tự chạy.

### Test case nghiệm thu — duyệt trước khi có code

Planner viết `.aizen/runs/<TASK>/acceptance.md`: mỗi tiêu chí (AC) có các case `TC-nn` dạng Given / When / Then,
luôn có ít nhất một case **đúng** và một case **sai** (bị từ chối, hết hạn, trùng…), thêm case biên khi đụng giới
hạn, thời gian, tranh chấp, phân quyền, tiền. Bạn duyệt bảng này ở bước "test case" của S2. Khi `approve`:

- file bị **băm và khoá** — agent không sửa được nữa, chỉ bạn sửa (rồi xác nhận lại `acceptance` và approve lại);
- dev **không được viết** test nằm ở `Test location` của file (hook chặn) — chỉ tester viết;
- tester làm đủ mọi `TC-nn` **trước khi đọc báo cáo của dev**, case tự thêm sau đó gắn `[tester-added]`;
- báo cáo test có bảng *Acceptance matrix*; guard không cho run xong nếu thiếu một case nào.

Nhờ vậy test kiểm thứ bạn đã đồng ý, không phải thứ dev tình cờ viết ra.

### Cho agent đủ thông tin ngay từ đầu

Prompt càng đủ, pha thống nhất càng ít vòng. Một prompt tốt có 6 phần (mẫu đầy đủ ở [prompt-mau.md](prompt-mau.md)):

1. **Mục tiêu** — một câu kiểm chứng được ("người dùng nhập mã giảm giá ở checkout và thấy tổng tiền giảm").
2. **Tiêu chí xong** — các trường hợp đúng/sai cụ thể, số liệu (giới hạn, thời gian phản hồi).
3. **Phạm vi** — làm gì, *không* làm gì.
4. **Ràng buộc** — API/schema không được đổi, thư viện được/không được dùng, branch gốc.
5. **Tài liệu và chỗ cần nhìn** — đường dẫn file/thư mục, link thiết kế, ticket, log lỗi.
6. **Quyền cho trước** — việc A3 bạn cho phép sẵn (cài graphify, chạy DB local bằng Docker, tải package…).

Không cần ghi những gì agent tự đo được (version, cấu trúc thư mục, cách code hiện tại chạy) — nó sẽ tự đọc.

### Trả lời câu hỏi xác nhận

- Đồng ý hết phương án đề xuất: "theo đề xuất".
- Đổi một phần: nói rõ phần nào, muốn gì ("module api: dùng 1 endpoint, giữ endpoint cũ 1 tháng").
- Còn băn khoăn: hỏi lại — chưa `approve` thì chưa có dòng code nào được viết.

### Theo dõi và tiếp tục

- **Báo cáo để đọc / dán cho AI web: `.aizen/out/latest.md`** — mục tiêu, trạng thái, câu hỏi chờ bạn, kiểm tra
  còn mở, tóm tắt của agent, nhật ký gần nhất, đường dẫn file chi tiết. Tự cập nhật khi duyệt plan, sang vòng sửa,
  bị chặn, chờ bạn, xong. Bản cũ giữ ở `.aizen/out/history/`. Terminal chỉ in đường dẫn, không in lại báo cáo
  (tốn token hai lần). Tạo lại bất kỳ lúc nào: `uv run <CORE_DIR>/scripts/core/journal.py report`.
- **Nhật ký suy nghĩ: `.aizen/runs/<TASK>/journal.md`** — mỗi dòng một câu:

  ```
  - 14:30 · planner · 🧠 Tôi đang nghĩ cách giữ ghế: khoá Redis hay cột held_until
  - 14:31 · planner · 🔀 Tôi chọn cột held_until vì cần truy vấn ghế đang giữ
  - 14:52 · dev-api · ✍ Đã ghi seat_hold.py, seat_hold_test.py
  - 14:53 · dev-api · ▶ Đã chạy `npm test -- seat` → lỗi
  - 14:55 · dev-api · 🔧 Tôi sẽ thử khoá dòng bằng SELECT … FOR UPDATE
  ```

  Dòng ✍/▶ do hook tự ghi (không quên, không bịa được); dòng 🧠 🔧 🔀 ✅ ❓ ⛔ do agent ghi ở **điểm quyết định**
  bằng `journal.py note`. Run có sửa file mà không có dòng suy nghĩ nào thì guard không cho xong. Lưu ý: dòng
  "nghĩ" là lời agent tự kể, dùng để theo dõi hướng đi — bằng chứng thật vẫn là dòng ✍/▶ và diff.
- Trạng thái máy: `.aizen/runs/<TASK>/state.md` (phần `## Agreed` ghi từng câu bạn đã xác nhận). Plan:
  `plan.md`; báo cáo từng role: `reports/`.
- Tiếp tục task bị ngắt: "/aizen-build tiếp tục task <TASK>" — agent đọc `state.md` và `journal.md`, không hỏi lại phần đã chốt.
- Ngôn ngữ của nhật ký và báo cáo: `"lang": "vi"` (mặc định) hoặc `"en"` trong `.aizen/config/guard.json`.

### GitHub sạch: không file AI, nhánh theo nghiệp vụ

- `guard.py install` thêm vào `.git/info/exclude` (chỉ ở máy bạn, không lộ cả trong `.gitignore`): `.aizen/`,
  `.agents/`, `.claude/`, `.cursor/`, `.gemini/`, `.windsurf/`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.mcp.json`,
  `skills-lock.json`, `graphify-out/`… và tắt dòng `Co-Authored-By` / "Generated with" mà Claude Code tự thêm vào commit/PR.
- Nhánh đặt theo **nghiệp vụ**, không theo mã task của agent: `feature/giu-ghe`, `bugfix/thanh-toan-timeout`
  (nhiều module: `feature/giu-ghe-api`, `feature/giu-ghe-web` gộp vào `feature/giu-ghe`). Agent đặt tên khi
  `state.py init --slug giu-ghe`; xem tên bằng `state.py branch --task <TASK>`.
- Commit: `feat(seat): giữ ghế 5 phút khi đặt vé` — không `[T-12]`. Có ticket Jira/issue thật thì truyền
  `--ticket SHOP-42`, commit thêm dòng `Refs: SHOP-42`.
- `git push` bị chặn nếu nhánh còn chứa file AI, hoặc commit chưa push có mã run / dòng đồng tác giả AI — hook in
  sẵn lệnh sửa. Repo **đã lỡ commit** `CLAUDE.md`, `.claude/`…: exclude không gỡ được file đã theo dõi, bạn chạy
  một lần lệnh `git rm -r --cached …` hook in ra (lịch sử cũ vẫn còn).
- Team cố ý chia sẻ các file này: `"hide_ai_files": false` trong `.aizen/config/guard.json`.

### Điều khiển dự án: `.aizen/PROJECT.md` và backlog

Sau khi cài cho dự án (`guard.py install` hoặc `sync --project`), mở **`.aizen/PROJECT.md`** — file duy nhất cần đọc:
mục 0 "Cần bạn ngay" (run bị chặn, câu hỏi chờ trả lời, việc chờ duyệt, push bị chặn), mục 1–9 để hiểu dự án,
mục 11 việc agent đã / đang / sắp làm. File tự cập nhật; muốn sửa nội dung thì sửa nguồn ở mục 13.

```bash
aizen backlog add --title "rate limit cho API public" --skill aizen-build   # thêm việc (trạng thái proposed)
aizen backlog approve BL-05                                                # chỉ bạn duyệt — hook chặn agent
aizen guard check --run T-12                                               # run còn thiếu gì (exit 0 = đủ)
aizen guard stop --run T-12 --reason "đổi hướng"                            # dừng một run
aizen project                                                              # biên soạn lại bản đồ ngay
```

Mỗi skill chạy thành một run trong `.aizen/runs/<RUN>/`. Agent tích `sheet.md` kèm bằng chứng, guard kiểm từng ô,
chạy các luật tất định, rồi một verifier độc lập chấm (≥ 80%). Chưa đủ thì agent bị đẩy lại làm tiếp với danh
sách cụ thể; đủ thì guard tự đánh dấu `done` và chuyển run vào `archive/`.

- Run chuyển `blocked` → mục 0 của `PROJECT.md` có lý do; chọn: làm tiếp, cho miễn bước, sửa plan, hoặc dừng.
- Miễn bước: agent chạy `guard.py waive … --evidence <file | 1 dòng output>`; chỉ có hiệu lực khi verifier (hoặc
  reviewer) ghi `accepted`.
- Báo cáo test/review và `verdict.json` phải do chính tester/reviewer/verifier viết (hook ghi lại ai viết); mọi kết
  luận đạt phải dẫn `path:line` và guard mở từng dòng để kiểm.
- `git push` nhánh của run bị chặn khi contract chưa đủ — đúng ý đồ; `--no-verify` nếu bạn chủ động bỏ qua.
- Run cũ bỏ dở chặn sửa code: `aizen guard stop --run <ID> --reason "…"`.
- Bắt mọi sửa code phải có run: `"require_task": true` trong `.aizen/config/guard.json`. Chia sẻ `knowledge/` và
  `PROJECT.md` với team: `"share_knowledge": true`, rồi `aizen guard install`.

### Mẹo để agent làm tốt nhất

- Một task = một mục tiêu. Nhiều việc không liên quan → nhiều task.
- Có `CLAUDE.md`/`AGENTS.md` trong project ghi lệnh build/test, quy ước code — mọi role đều đọc.
- Có test chạy được (`npm test`, `pytest`…): `check.py` chỉ báo PASS khi có test thật sự chạy; không có test thì
  kết quả là `UNVERIFIED`, không phải PASS.
- Ghi bài học vào `.aizen/knowledge/lessons.md` (agent tự thêm `L-nn` cuối task) — lần sau agent đọc trước khi sửa code.
- Duyệt cài graphify ở task đầu tiên: các role tìm code và phạm vi ảnh hưởng nhanh hơn nhiều.

## 4. Các skill khác — cần đưa gì

| Skill | Luôn kèm |
|---|---|
| `aizen-build` — review | diff/PR (số PR, branch, hoặc `git diff base...head`), mục tiêu của thay đổi, phần nào là lõi |
| `aizen-build` — design | engine + version, các thực thể và quan hệ, quy mô dữ liệu, truy vấn chính, quy ước team nếu có |
| `aizen-build` — pipeline | repo, nền tảng CI, nơi deploy, registry, branch nào deploy đi đâu, secret đã có (chỉ tên) |
| `aizen-init` | **URL repo GitHub/GitLab** + **tài liệu chi tiết dự án** (bắt buộc, thiếu thì skill dừng hỏi); nếu có: stack, infra, kiểu auth |
| `aizen-skill-creator` | skill làm gì, 3 prompt phải kích hoạt + vài prompt không được kích hoạt, đầu ra mong muốn, việc nào cần hỏi bạn |
| `aizen-skill-importer` | link thư mục skill (`…/tree/<branch>/<path>`) hoặc đường dẫn local, tên skill đích, muốn đổi gì, một task mẫu để A/B test |
| `aizen-skill-eval` | tên skill, tiêu chí đạt, vài prompt nên/không nên kích hoạt |
| `aizen-tech-learning` | tên công nghệ + version, **workload tham chiếu** (vd. cache 100k GET/s, value 1KB), 2–3 công nghệ để so sánh, trang Notion cha |
| `aizen-video-to-skill` | link/file video, skill mới giúp agent làm gì, tên + ngôn ngữ skill |

## 5. Tạo và chép skill

Cả hai skill làm việc ngay trong repo Aizen-Skills và theo [chuẩn skill Aizen](aizen-skill-standard.md).

| | `aizen-skill-creator` | `aizen-skill-importer` |
|---|---|---|
| Đầu vào | ý tưởng skill | link GitHub hoặc thư mục skill có sẵn |
| Bạn được hỏi | 1 lượt phỏng vấn → duyệt bản thiết kế ngắn | 1 lượt phỏng vấn → duyệt bản tóm tắt thay đổi |
| Agent tự làm | quyết định entry hay topic của pack, dựng `SKILL.md` + `manifest.json` (`new_skill.py`), viết skill, thêm README + docs + prompt mẫu, eval bằng `aizen-skill-eval` | tải về, chuẩn hoá + ghi nguồn/giấy phép (`fetch_skill.py`) hoặc vendor vào pack (`bin/vendor.js`), tuỳ biến, A/B test bằng `aizen-skill-eval`, thêm docs |
| Kết thúc | `npm test` xanh → `sync` → commit đúng file | như bên trái |
| Push | chỉ khi bạn đồng ý | chỉ khi bạn đồng ý |

- Cải thiện skill đã có trong repo: dùng `aizen-skill-creator` ("cải thiện skill <tên>: <vấn đề>"); nó lưu bản cũ vào
  `.aizen/cache/import/<tên>/baseline/`, đề xuất thay đổi, rồi so sánh bản mới với bản cũ.
- Skill tự cải thiện: khi skill làm chưa tốt, agent ghi sổ phản hồi (`feedback.py log`) rồi báo bạn một dòng. Vấn
  đề lặp ≥ 2 lần (hoặc bạn phàn nàn) → agent đề xuất sửa qua `aizen-skill-creator`, thêm eval case để lỗi không quay lại.
  Xem sổ: `uv run skills/aizen-skill-creator/scripts/authoring/feedback.py list --open`.
- Không bao giờ ghi đè skill trùng tên; thư mục tạm nằm ở `.aizen/cache/` (đã git-ignore).
- Skill chép về không có giấy phép → agent báo trước khi tuỳ biến; bạn quyết định giữ riêng hay không.


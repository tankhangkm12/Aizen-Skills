# Hướng dẫn sử dụng Aizen Skills

Tài liệu này hướng dẫn cách dùng bộ skill hiệu quả nhất: agent nhận đủ thông tin ngay từ đầu nên không phải
đoán, không hỏi lại những gì bạn đã biết, và tập trung vào đúng việc. Prompt mẫu để copy: [prompt-mau.md](prompt-mau.md).

## 1. Cài và kiểm tra

```bash
git clone https://github.com/tankhangkm12/Aizen-Skills.git && cd Aizen-Skills
node bin/cli.js sync        # liên kết mọi skill vào ~/.claude/skills, ~/.agents/skills, …
npm test                    # (tuỳ chọn) kiểm tra bộ skill
```

Mở **session mới** của agent sau khi sync. Kiểm tra: gõ `/cecilia-coding-skills` trong Claude Code, hoặc hỏi
"liệt kê các skill bạn có". Cập nhật sau này: `git pull && node bin/cli.js sync`.

Python 3 cần cho script của Cecilia (`state.py`, `check.py`, `graph.py`, …). Graphify (code map) được Cecilia đề
nghị cài khi cần — bạn duyệt một lần.

## 2. Gọi skill

- **Tự động**: agent chọn skill theo nội dung prompt. Dùng đúng từ khoá trong bảng dưới cho chắc.
- **Gọi thẳng** (chắc chắn nhất): Claude Code `/<tên-skill> <prompt>`; agent khác: "Dùng skill `<tên>` để …".

| Bạn muốn | Skill | Từ khoá trong prompt |
|---|---|---|
| làm tính năng, sửa bug, refactor tới PR | `cecilia-coding-skills` | "Cecilia", "làm tính năng", "sửa bug", "từ ý tưởng tới PR" |
| review PR / diff / code AI viết | `adversarial-code-reviewer` | "review PR", "audit diff" |
| thiết kế bảng / schema MySQL | `database-table-design` | "thiết kế bảng", "DDL" |
| CI/CD bảo mật, Docker, deploy | `devsecops-pipeline-flow` | "pipeline CI/CD", "DevSecOps" |
| tạo skill mới / cải thiện skill trong repo | `skill-creator` | "tạo skill", "cải thiện skill <tên>" |
| chép skill từ GitHub/thư mục khác rồi tuỳ biến | `skill-cloner` | "clone skill" + link |
| đánh giá một skill | `agent-skill-tester` | "test skill", "benchmark skill" |
| hiểu sâu một công nghệ, so sánh kiến trúc → Notion | `tech-learning-tree` | "nghiên cứu", "vì sao X nhanh", "so sánh kiến trúc X và Y" |
| biến video thành skill | `video-to-skill` | link YouTube / file video |

Các `cecilia-*` còn lại là knowledge pack — **không gọi trực tiếp**, Cecilia tự nạp cho từng role.

## 3. Làm việc với Cecilia

### Luồng — một luồng, hai pha

```
Pha THỐNG NHẤT (bạn được hỏi kỹ)              Pha THỰC THI (không hỏi bạn nữa)
S0 tiếp nhận + code map                      S3 dev song song, mỗi module một worktree, code tối thiểu
S1 planner khảo sát, thiết kế, chia module   S4 tích hợp int/<TASK>
S2 xác nhận từng phần:                       S5 tester   S6 reviewer (+ redteam nếu rủi ro)
   phạm vi → module 1 → module 2 → …         S7 tự sửa ≤ 2 vòng
   → triển khai (duyệt trước các việc A3)    S8 tổng kết + khối lệnh push/PR để bạn chạy
   → approve
```

- **Pha thống nhất**: mỗi lượt hỏi chỉ về một phần, có phương án đề xuất đứng đầu. Muốn đổi gì cứ nói — Cecilia
  sửa plan và hỏi lại **đúng phần đó**. Chốt bằng câu "approve plan".
- **Pha thực thi**: plan đã duyệt là hợp đồng. Agent không hỏi nữa; chi tiết nhỏ plan chưa nói thì chọn cách đơn
  giản nhất và liệt kê ở `Deviations:` trong báo cáo. Bạn chỉ bị gọi lại khi `BLOCKED`: cần việc A3 chưa duyệt,
  việc A4 (push, merge, production, secret…), nguy cơ mất dữ liệu, hoặc plan không làm được.
- Agent **không bao giờ push**. Cuối task bạn nhận khối lệnh `git push` + `gh pr create --draft` để tự chạy.

### Cho Cecilia đủ thông tin ngay từ đầu

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

- Trạng thái task: `tensura/tasks/<TASK>/state.md` (phần `## Agreed` ghi từng câu bạn đã xác nhận).
- Plan: `tensura/plans/<TASK>.md`; báo cáo từng role: `tensura/reports/<TASK>/`.
- Tiếp tục task bị ngắt: "Cecilia, tiếp tục task <TASK>" — agent đọc `state.md`, không hỏi lại phần đã chốt.
- Thêm `tensura/` và `graphify-out/` vào `.git/info/exclude` (Cecilia tự làm với `graphify-out/`).

### Mẹo để agent làm tốt nhất

- Một task = một mục tiêu. Nhiều việc không liên quan → nhiều task.
- Có `CLAUDE.md`/`AGENTS.md` trong project ghi lệnh build/test, quy ước code — mọi role đều đọc.
- Có test chạy được (`npm test`, `pytest`…): `check.py` chỉ báo PASS khi có test thật sự chạy; không có test thì
  kết quả là `UNVERIFIED`, không phải PASS.
- Ghi bài học vào `tensura/lessons.md` (Cecilia tự thêm `L-nn` cuối task) — lần sau agent đọc trước khi sửa code.
- Duyệt cài graphify ở task đầu tiên: các role tìm code và phạm vi ảnh hưởng nhanh hơn nhiều.

## 4. Các skill khác — cần đưa gì

| Skill | Luôn kèm |
|---|---|
| `adversarial-code-reviewer` | diff/PR (số PR, branch, hoặc `git diff base...head`), mục tiêu của thay đổi, phần nào là lõi |
| `database-table-design` | engine + version, các thực thể và quan hệ, quy mô dữ liệu, truy vấn chính |
| `devsecops-pipeline-flow` | repo, nền tảng CI, nơi deploy, registry, branch nào deploy đi đâu, secret đã có (chỉ tên) |
| `skill-creator` | skill làm gì, 3 prompt phải kích hoạt + vài prompt không được kích hoạt, đầu ra mong muốn, việc nào cần hỏi bạn |
| `skill-cloner` | link thư mục skill (`…/tree/<branch>/<path>`) hoặc đường dẫn local, tên skill đích, muốn đổi gì, một task mẫu để A/B test |
| `agent-skill-tester` | tên skill, tiêu chí đạt, vài prompt nên/không nên kích hoạt |
| `tech-learning-tree` | tên công nghệ + version, **workload tham chiếu** (vd. cache 100k GET/s, value 1KB), 2–3 công nghệ để so sánh, trang Notion cha |
| `video-to-skill` | link/file video, skill mới giúp agent làm gì, tên + ngôn ngữ skill |

## 5. Tạo và chép skill

Cả hai skill làm việc ngay trong repo Aizen-Skills và theo [chuẩn skill Aizen](aizen-skill-standard.md).

| | `skill-creator` | `skill-cloner` |
|---|---|---|
| Đầu vào | ý tưởng skill | link GitHub hoặc thư mục skill có sẵn |
| Bạn được hỏi | 1 lượt phỏng vấn → duyệt bản thiết kế ngắn | 1 lượt phỏng vấn → duyệt bản tóm tắt thay đổi |
| Agent tự làm | dựng đủ 8 phần (`new_skill.py`), viết skill, thêm dòng README + docs + prompt mẫu, eval có/không skill | tải về, chuẩn hoá 8 phần + ghi nguồn/giấy phép (`fetch_skill.py`), tuỳ biến, A/B test bản gốc vs bản mới, thêm docs |
| Kết thúc | `npm test` xanh → `sync` → commit đúng file | như bên trái |
| Push | chỉ khi bạn đồng ý | chỉ khi bạn đồng ý |

- Cải thiện skill đã có trong repo: dùng `skill-creator` ("cải thiện skill <tên>: <vấn đề>"); nó lưu bản cũ vào
  `.aizen-work/<tên>/baseline/`, đề xuất thay đổi, rồi so sánh bản mới với bản cũ.
- Skill tự cải thiện: khi skill làm chưa tốt, agent ghi sổ phản hồi (`feedback.py log`) rồi báo bạn một dòng. Vấn
  đề lặp ≥ 2 lần (hoặc bạn phàn nàn) → agent đề xuất sửa qua `skill-creator`, thêm eval case để lỗi không quay lại.
  Xem sổ: `python skills/skill-creator/scripts/feedback.py list --open`.
- Không bao giờ ghi đè skill trùng tên; thư mục tạm nằm ở `.aizen-work/` (đã git-ignore).
- Skill chép về không có giấy phép → agent báo trước khi tuỳ biến; bạn quyết định giữ riêng hay không.


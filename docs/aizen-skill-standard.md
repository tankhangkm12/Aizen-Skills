# Chuẩn skill Aizen (Aizen Universal Structure)

Nguồn duy nhất cho quy tắc viết skill trong repo này. `skill-creator` (tạo/sửa skill) và `skill-cloner` (chép +
tuỳ biến skill) đều theo tài liệu này; `npm test` (`tests/check-skills.js`) kiểm phần máy kiểm được.

## 1. Cấu trúc — 8 phần, luôn có đủ

```text
skills/<name>/
├── SKILL.md          # bắt buộc: front-matter + quy trình chính, ngắn
├── manifest.json     # bắt buộc: metadata
├── rules/            # luật bắt buộc (vd. mcp.md, các ranh giới quyền)
├── agents/           # prompt sub-agent (khi skill giao việc)
├── references/       # kiến thức dài, nạp khi cần
├── tools/            # định nghĩa tool (nếu có)
├── scripts/          # mã chạy được (Python/Node), cho việc lặp lại và cần kết quả giống nhau
└── assets/           # template, file tĩnh
```

- Thư mục chưa có gì giữ bằng `.gitkeep`; có file thật thì xoá `.gitkeep`.
- Knowledge pack (`manifest.partOf` = skill chính) chỉ cần `SKILL.md`, `manifest.json`, `references/`.
- `evals/` (tuỳ chọn) chứa `evals.json` để chạy lại đánh giá.
- **Self-contained**: skill chỉ dùng file của chính nó. Ngoại lệ: pack của cùng một gia đình skill, và tài liệu
  của repo (`docs/`) với skill làm việc trên chính repo (`skill-creator`, `skill-cloner`).

## 2. `SKILL.md`

```markdown
---
name: <name>                     # trùng tên thư mục: chữ thường, số, gạch ngang
description: <xem §3>
---

# <Tiêu đề> (vN nếu skill ghi version ở tiêu đề — phải khớp major của manifest)

<1–2 câu: skill làm gì, cho ai.>
**Read first:** `rules/<...>.md`

## Workflow
1. … (mệnh lệnh, mỗi bước có đầu ra kiểm được; nói *vì sao* khi bước không hiển nhiên)

## Rules / Output / Knowledge (bảng "cần gì → đọc file nào")
```

- Dưới ~150 dòng. Kiến thức dài → `references/`, kèm câu "khi nào đọc".
- Mọi đường dẫn trong backtick (`` `references/x.md` ``, `` `scripts/y.py` ``) và mọi link `](x.md)` phải tồn tại.
- Viết mệnh lệnh, có ví dụ input/output; giải thích lý do thay vì chỉ "MUST".
- Bước cần hỏi người dùng: nói rõ hỏi gì, có phương án đề xuất; bước nguy hiểm (xoá, ghi ra ngoài, push) phải hỏi.

## 3. `description` — quyết định khi nào agent chọn skill

- ≤ 1024 ký tự, một dòng. Cấu trúc: **làm gì** → **"Use when …"** (tình huống, từ khoá Anh + Việt) →
  **"Not for: …"** (các skill gần giống, để không tranh trigger).
- Đọc description của mọi skill có sẵn trước khi viết; trùng phạm vi → nói rõ ranh giới ở "Not for".
- Knowledge pack: ghi "not a standalone skill, do not trigger it directly".

## 4. `manifest.json`

```json
{
  "name": "<name>",
  "version": "1.0.0",
  "description": "<một câu>",
  "framework": "Aizen Universal Structure"
}
```

- `name` = tên thư mục; `version` semver: sửa nhỏ → patch, thêm khả năng → minor, đổi cách dùng → major.
- Skill chép từ nơi khác thêm `"source": {"url": "...", "ref": "<branch|commit>", "license": "<tên>"}`.
- Không còn placeholder `{{...}}`.

## 5. `scripts/`

- Python 3 thư viện chuẩn (hoặc Node không cần cài thêm). Phụ thuộc ngoài → kiểm tra có chưa, in lệnh cài,
  hỏi trước khi cài.
- Có `--help`; exit code rõ (0 ok, 1 lỗi, 2 sai cách dùng); không ghi đè dữ liệu người dùng khi chưa có `--force`.
- Logic không hiển nhiên có `--selfcheck` (assert) và một dòng trong `tests/check-scripts.js`.
- Gọi bằng đường dẫn tuyệt đối `python "<SKILL_DIR>/scripts/x.py"` để chạy được từ thư mục nào cũng được.

## 6. `rules/`

- `rules/mcp.md` cho skill kỹ thuật: dùng `context7` / `sequentialthinking` khi có, không có thì báo một lần và
  làm tiếp.
- Luật riêng của skill (ranh giới quyền, việc phải hỏi) — mỗi luật một dòng, kèm lý do.

## 7. Tài liệu bắt buộc khi thêm skill (lint kiểm)

| File | Thêm |
|---|---|
| `README.md` | một dòng trong bảng "Danh sách skill": `` [`<name>`](skills/<name>) `` + dùng khi nào |
| `docs/huong-dan-su-dung.md` | một dòng ở bảng §2 (skill · từ khoá) và một dòng ở bảng §4 (luôn kèm gì) |
| `docs/prompt-mau.md` | ít nhất một prompt mẫu bắt đầu bằng `/<name>` |

Knowledge pack không cần (README đã có dòng `cecilia-*`).

## 8. Kiểm tra và đưa lên

```bash
npm test                         # cấu trúc, đường dẫn, version, docs, script
node bin/cli.js sync             # liên kết vào thư mục skill của các agent
git add <đúng các file đã sửa>   # không dùng `git add .`
git commit -m "feat(<name>): <mô tả>"
```

`git push` chỉ khi người dùng đồng ý rõ ràng cho lần push đó; nếu không, in sẵn lệnh để họ tự chạy.
Thư mục làm việc tạm (baseline, kết quả eval) nằm ở `.aizen-work/` (đã git-ignore), không bao giờ trong `skills/`
— mọi thư mục trong `skills/` đều bị cài như một skill.

# Chuẩn skill Aizen (v3)

Nguồn duy nhất cho quy tắc viết skill trong repo này. `aizen-skill-creator` (tạo/sửa skill) và `aizen-skill-importer`
(chép skill, vendor kiến thức) đều theo tài liệu này; `npm test` (`tests/check-skills.js`) kiểm phần máy kiểm được.

## 1. Hai loại skill

| `kind` | Là gì | Ví dụ | Kích hoạt |
|---|---|---|---|
| `entry` | một quy trình người dùng gọi, có đầu ra riêng | `aizen-build`, `aizen-init`, `aizen-skill-creator` | theo `description`, hoặc `/<tên>` |
| `pack` | kho kiến thức theo **topic**, được entry nạp | `aizen-core`, `aizen-database` | không bao giờ trực tiếp |

Trước khi tạo skill mới, hỏi: đây là một quy trình mới (entry) hay chỉ là kiến thức cho một topic đã có (thêm file vào
pack)? Hai entry cùng làm một việc sẽ tranh trigger của nhau — gộp lại thành *route* của entry sẵn có.

## 2. Cấu trúc — chỉ tạo thư mục khi có nội dung

```text
skills/<name>/
├── SKILL.md                 # bắt buộc: front-matter + quy trình chính, ngắn
├── manifest.json            # bắt buộc: name, version, kind, topics, requires
├── rules/                   # luật riêng của skill (luật chung ở aizen-core)
├── agents/                  # prompt sub-agent (entry giao việc)
├── references/<topic>/      # kiến thức dài, nạp khi cần; skill không có topic dùng references/ phẳng
│   └── vendor/<nguồn>/      # kiến thức upstream chép nguyên văn: UPSTREAM.md + LICENSE bắt buộc
├── assets/<topic>/          # template, file tĩnh
├── scripts/<topic>/         # mã chạy được (Python stdlib / Node không cần cài thêm)
└── evals/evals.json         # tuỳ chọn: bộ eval để chạy lại (aizen-skill-eval)
```

- Không giữ thư mục rỗng, không `.gitkeep`. Không có `SKILL.md` lồng bên trong skill (installer sẽ coi là skill khác) —
  file upstream tên `SKILL.md` đổi thành `guide.md`.
- Skill có `topics`: mọi thư mục con của `references/`, `assets/`, `scripts/` phải là một topic đã khai báo.

### Đường dẫn và topic (Dependency Inversion)

`references|assets|scripts/<topic>/…` luôn thuộc skill có `<topic>` trong `manifest.json` → `topics`, ở bất kỳ skill nào
viết đường dẫn đó. Ví dụ `references/core/rules.md` từ `aizen-init` resolve tới `aizen-core`. Vì vậy:

- Thêm pack/topic mới **không phải sửa code**: `state.py` (brief) và lint đều đọc manifest.
- Một topic chỉ có một chủ; lint báo topic trùng.
- `agents/` và `rules/` luôn thuộc chính skill đang viết.
- Script chạy bằng đường dẫn tuyệt đối: `python "<SKILL_DIR>/scripts/<topic>/x.py"`; script của skill khác dùng
  `<CORE_DIR>`, `<FRONTEND_DIR>`… = thư mục của `aizen-core`, `aizen-frontend`… (brief in bảng đường dẫn).

## 3. `SKILL.md`

```markdown
---
name: <name>                     # trùng tên thư mục: chữ thường, số, gạch ngang; tiền tố aizen-
description: <xem §4>
---

# <name> — <tiêu đề> (vN — khớp major của manifest)

<1–2 câu: skill làm gì, cho ai.>
**Read first:** `references/core/rules.md` (+ luật riêng trong `rules/` nếu có)

## Workflow
1. … (mệnh lệnh, mỗi bước có đầu ra kiểm được; nói *vì sao* khi bước không hiển nhiên)

## Knowledge (bảng "cần gì → đọc file nào")
```

- Dưới ~150 dòng. Kiến thức dài → `references/`, kèm câu "khi nào đọc".
- **Không chép lại luật chung.** Quyền A0–A4, evidence, git local-only, code-quality, MCP đã ở `aizen-core` — link tới đó.
- Mọi đường dẫn trong backtick (`` `references/x.md` ``, `` `scripts/y.py` ``) và mọi link `](x.md)` phải tồn tại.
- Viết mệnh lệnh, có ví dụ input/output; giải thích lý do thay vì chỉ "MUST".
- Bước cần hỏi người dùng: nói rõ hỏi gì, có phương án đề xuất; bước nguy hiểm (xoá, ghi ra ngoài, push) phải hỏi.

## 4. `description` — quyết định khi nào agent chọn skill

- ≤ 1024 ký tự, một dòng; có `: ` thì đặt trong nháy kép (YAML).
- Entry: **làm gì** → **"Use when …"** (tình huống, từ khoá Anh + Việt) → **"Not for: …"** (bắt buộc — nêu skill nào sở
  hữu các trường hợp gần giống).
- Pack: ghi "not a standalone skill, do not trigger it directly" và entry nào nạp nó.

## 5. `manifest.json`

```json
{
  "name": "<name>",
  "version": "1.0.0",
  "description": "<một câu>",
  "framework": "Aizen",
  "kind": "entry",
  "topics": ["<topic>"],
  "requires": ["aizen-core"]
}
```

- `name` = tên thư mục; `version` semver: sửa nhỏ → patch, thêm khả năng → minor, đổi cách dùng/đổi tên → major.
- `topics`: chỉ khi skill sở hữu kiến thức/template/script mà skill khác dùng. `requires`: các skill phải cài cạnh nó.
- Skill chép nguyên từ nơi khác thêm `"source": {"url": "...", "ref": "<branch|commit>", "license": "<tên>"}`.

## 6. Kiến thức vendored (đứng trên vai người khổng lồ)

Best practice của đội làm ra công cụ được chép **nguyên văn** vào `references/<topic>/vendor/<nguồn>/` của pack phù hợp.

1. Có giấy phép mới chép; không có → chỉ link.
2. Khai báo trong `vendor.lock.json` (repo, ref, phần chép, giấy phép, ghi chú giữ/bỏ gì và vì sao), rồi
   `node bin/vendor.js sync <name>` — ghim commit, ghi `UPSTREAM.md` và `LICENSE`.
3. Không sửa file vendored; quan điểm của Aizen viết ở guide của pack (bảng "Deeper": cần gì → file nào).
4. Thứ tự ưu tiên: luật core > guide của pack > vendored (`references/core/workspace.md` §3 trong `aizen-core`).
5. Cập nhật có chủ đích: `node bin/vendor.js update <name>`, đọc `git diff`, rồi commit.

### 6b. Chép hay dùng trực tiếp?

| Chọn | Khi | Cách |
|---|---|---|
| **Vendor** (chép, ghim commit) | tài liệu/luật thuần, ít thay đổi, cần ổn định và đọc offline | `vendor.lock.json` + `bin/vendor.js` |
| **External** (dùng trực tiếp, theo bản mới) | skill có công cụ chạy được, có cơ chế cập nhật riêng, giá trị nằm ở việc theo kịp cộng đồng | `externals.json` + `bin/external.js`; pack khai báo `"optional": ["<tên>"]` |

External: không bao giờ tự cài/cập nhật (người dùng gõ `aizen external install|update`); pack dùng nó phải có
đường lui khi chưa cài và ghi rõ trong guide; brief in dòng `Optional tools:` cho biết đã cài hay chưa.

## 7. `scripts/`

- Python 3 thư viện chuẩn (hoặc Node không cần cài thêm). Phụ thuộc ngoài → kiểm tra có chưa, in lệnh cài, hỏi trước.
- Có `--help`; exit code rõ (0 ok, 1 lỗi, 2 sai cách dùng, 3 chưa kiểm chứng được); không ghi đè file của người dùng
  khi chưa có `--force`; không bao giờ nhận giá trị secret qua tham số dòng lệnh.
- Logic không hiển nhiên có `--selfcheck` (assert) và một dòng trong `tests/check-scripts.js`.

## 8. Tài liệu bắt buộc khi thêm entry (lint kiểm)

| File | Thêm |
|---|---|
| `README.md` | một dòng trong bảng "Danh sách skill": `` [`<name>`](skills/<name>) `` + dùng khi nào |
| `docs/huong-dan-su-dung.md` | một dòng ở bảng §2 (skill · từ khoá) và một dòng ở bảng §4 (luôn kèm gì) |
| `docs/prompt-mau.md` | ít nhất một prompt mẫu bắt đầu bằng `/<name>` |

Pack ghi một dòng trong bảng pack của README.

## 9. Kiểm tra và đưa lên

```bash
npm test                         # manifest, topic, đường dẫn, version, vendor, docs, script
node bin/cli.js sync             # liên kết vào thư mục skill của các agent
git add <đúng các file đã sửa>   # không dùng `git add .`
git commit -m "feat(<name>): <mô tả>"
```

`git push` chỉ khi người dùng đồng ý rõ ràng cho lần push đó; nếu không, in sẵn lệnh để họ tự chạy.
Thư mục làm việc tạm (baseline, kết quả eval) nằm ở `.aizen-work/` (đã git-ignore), không bao giờ trong `skills/`
— mọi thư mục trong `skills/` đều bị cài như một skill.

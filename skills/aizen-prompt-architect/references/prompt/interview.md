# Interview — ask little, ask well

## 1. Task types and the fields each one needs

| Type | Prompt starts with | Must have | Good to have |
|---|---|---|---|
| feature | `/aizen-build` | goal, acceptance criteria, scope / non-goals | numbers (latency, limits), permissions, docs to read |
| bug | `/aizen-build` | expected vs actual, how to reproduce | evidence (log ≤ 30 lines), since when, environment |
| refactor | `/aizen-build` | what changes, what must **not** change in behaviour | how behaviour is pinned (existing tests / new tests first) |
| idea → PR | `/aizen-build` | who uses it, the problem, the first-version must-haves | stack constraints, what can wait |
| database design | `/aizen-build thiết kế (chưa code)` | entities, relations, main queries | volume and retention, team conventions |
| CI/CD | `/aizen-build dựng pipeline` | CI system, deploy target, branch → environment | registry, secret names (never values) |
| project bootstrap | `/aizen-init` | repo URL, project documents | stack if the documents do not say, auth, push policy |

Every type also gets a **task id** (the owner's ticket, or a short one you propose), a **business name** and a
**stop point** (`references/prompt/format.md` §2).

## 2. What never to ask

The run measures these itself — asking wastes a round and the owner's answer is often out of date:

- language, framework, versions, folder layout, test runner, lint config, existing patterns;
- which files to change, how the code is organised, what the current behaviour is (when the repo shows it);
- how to implement it (the plan proposes options; the owner chooses then, with the code in view);
- anything already in the owner's message — re-read it before asking.

## 3. How to ask

One message, at most five questions, numbered, each answerable in a word:

```
1. Giữ ghế bao lâu?  A) 5 phút (mặc định)  B) 10 phút  C) khác: …
2. Hết giờ mà chưa thanh toán thì?  A) tự nhả ghế (mặc định)  B) báo người dùng gia hạn 1 lần
3. Phạm vi lần này?  A) chỉ API (mặc định)  B) API + màn hình chọn ghế
```

- Put the default you would choose first and mark it; "theo mặc định" from the owner accepts all defaults.
- Prefer questions whose answer changes the acceptance criteria, the scope or what is irreversible (data, money,
  public API, security). Skip questions whose answer would not change the prompt.
- A number the owner does not know (load, limits) → offer a reasonable default with its source, or mark it as a
  question the plan must settle; never present a guess as a fact.
- After the answers: a remaining gap that changes the result → one more round (two rounds total). Otherwise
  write the prompt and list the open points under `Câu hỏi mở` so the run asks them at plan time.

## 4. Turning answers into acceptance criteria

Each criterion is observable from outside the code: a status code, an error code, a stored row, a message, a
screen state, a number with a unit.

| Vague | Observable |
|---|---|
| giữ ghế an toàn | hai người giữ cùng ghế cùng lúc → đúng 1 người thành công, người kia nhận 409 `SEAT_ALREADY_HELD` |
| tìm chuyến nhanh | `GET /trips?from&to&date` p95 < 300 ms với 10k chuyến/ngày |
| báo lỗi rõ ràng | thanh toán quá hạn giữ → 410 `HOLD_EXPIRED`, không trừ tiền |

For each criterion add at least one **+** case (it works) and one **−** case (it refuses or fails safely), plus
**edge** cases for time, limits, concurrency, permissions and money when they apply. These become the acceptance
seeds; the planner turns them into the frozen `acceptance.md`.

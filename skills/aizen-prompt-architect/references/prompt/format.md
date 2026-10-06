# The Aizen task prompt

## 1. What the agent on the other side does with it

An agent running `aizen-build` reads the prompt, opens a run (`state.py init --task <id> --slug <business-name>
--type <type> --goal "…"`), measures the repo, writes a plan with one module per unit of work and an
`acceptance.md` of Given/When/Then cases, and **stops for the owner's approval**. After approval it builds, an
independent tester runs every acceptance case, a guard checks the run's contract, and the owner pushes. So the
prompt must give what the repo cannot: intent, rules of the business, limits, permissions and where to stop.

Words the owner will see in Aizen, so the prompt can use them:

| Word | Meaning |
|---|---|
| run / task | one piece of work with its own folder `.aizen/runs/<id>/` |
| plan, module | the agent's proposal, split into units the owner confirms one by one |
| approve | the owner's go-ahead; nothing is built before it |
| acceptance cases `TC-nn` | the frozen tests written from the plan, not from the code |
| A0–A4 | how much the agent may do alone: A3 (install, migrate, start services) needs the owner's yes, A4 (push, deploy, delete data) is the owner's |
| journal, `latest.md` | the agent's one-line thoughts and the hand-off report in `.aizen/out/latest.md` |
| business name | the branch name: `feature/<business-name>`, `bugfix/<business-name>` |

## 2. Shape

Fields in this order; drop a line the owner left empty unless it is required (★).

```text
/aizen-build
Task: <id> ★                         — the owner's ticket (TET-12) or a short one you propose
Tên nghiệp vụ: <business-name> ★     — 2–4 words, lowercase, "-" between: seat-hold, search-trips
Loại: feature | bugfix | hotfix | refactor | test | docs | ci | infra | chore ★
Mục tiêu: <one checkable sentence> ★
Tiêu chí xong: ★
- AC-1: <when … then … — observable>
- AC-2: <the refusal / error case>
- <numbers: p95 < 300 ms, at most 50 items, …>
Phạm vi: làm <…>; KHÔNG làm <…> ★
Ràng buộc: <API/schema unchanged · no new library · follow <module>'s pattern>
Tài liệu / chỗ cần nhìn: <paths, links, ticket>
Branch gốc: <develop>
Cho phép sẵn (A3): <start Postgres with docker compose · add a migration · npm install>
Gợi ý case kiểm thử (planner viết acceptance.md từ đây):
- TC AC-1 +    : Given <state> · When <action> · Then <observable result>
- TC AC-1 −    : Given … · When … · Then …
- TC AC-2 edge : Given … · When … · Then …
Câu hỏi mở: <what the plan must settle with me>
Điểm dừng: lập plan + acceptance.md, xác nhận từng module với tôi; approve xong thì làm hết không hỏi thêm. ★
```

Bug, refactor, database design, CI/CD and bootstrap prompts keep this order but swap the middle fields for the
ones in `references/prompt/interview.md` §1 (bug: `Lỗi: mong đợi … thực tế …`, `Tái hiện:`, `Bằng chứng:`; refactor:
`Hành vi bên ngoài: KHÔNG đổi`, `Chốt hành vi bằng:`). `/aizen-init` prompts have no business name: the run is
the bootstrap itself.

## 3. Writing it in the owner's language

Write the field labels as above (the agents recognise them) and the content in the language the owner used.
Keep each line to one idea. No greetings, no explanation of Aizen inside the prompt — the agent has the skills.

## 4. Quality check before delivering

- [ ] Every ★ field is present.
- [ ] The goal is one sentence someone could check without asking you.
- [ ] Each AC is observable (status, error code, row, message, screen state, number with unit) — no "works
      well", "fast", "secure".
- [ ] At least one refusal or error case per AC; edge cases for time, limits, concurrency, money, permissions
      when the feature touches them.
- [ ] The business name has no task code, no agent words and is ≤ 4 words.
- [ ] Non-goals say what will **not** be done, so the run cannot drift.
- [ ] Nothing invented: ids, numbers, paths and secrets come from the owner or are marked as questions.
- [ ] Irreversible actions (deleting data, pushing, deploying, paying) are not pre-approved unless the owner said
      so explicitly.
- [ ] The stop point is stated.

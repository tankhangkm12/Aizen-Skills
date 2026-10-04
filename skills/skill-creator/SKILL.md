---
name: skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance. Aizen optimized version. Use when users want to create a skill from scratch following the Aizen Universal Structure, edit an existing skill, or run evals to test a skill using Antigravity Artifacts.
---

# Skill Creator (Aizen Edition)

A skill for creating new skills and iteratively improving them.

At a high level, the process of creating a skill goes like this:

- **Phân tích yêu cầu và hệ thống**: Sử dụng MCP tools `context7` & `sequentialthinking`.
- **Write a draft of the skill**: Tuân thủ **Aizen Universal Structure**.
- **Create a few test prompts**: Run subagents on them via `invoke_subagent`.
- **Evaluate results**: Help the user evaluate the results both qualitatively and quantitatively via **Antigravity Artifacts**.
- **Iterate**: Rewrite the skill based on feedback from the user's evaluation of the results.
- **Repeat** until satisfied.

## Communicating with the user

The skill creator is liable to be used by people across a wide range of familiarity with coding jargon. Please pay attention to context cues to understand how to phrase your communication! 

## Creating a skill

### Capture Intent & Analyze

Start by understanding the user's intent. 

**QUAN TRỌNG:** Trước khi viết code, bạn BẮT BUỘC phải dùng MCP server `context7` (để tra cứu mã nguồn, tài liệu liên quan trong workspace) và `sequentialthinking` (để phân tích giải pháp từng bước). Điều này đảm bảo skill được tạo ra hiểu đúng context của project.

1. What should this skill enable the agent to do?
2. When should this skill trigger?
3. What's the expected output format?
4. Should we set up test cases to verify the skill works?

### Write the SKILL.md

Based on the user interview, fill in these components:

- **name**: Skill identifier
- **description**: When to trigger, what it does. Include both what the skill does AND specific contexts for when to use it. Make it slightly "pushy".

#### Anatomy of an Aizen Skill

Bạn PHẢI tuân thủ kiến trúc Aizen. Hãy đọc file `references/aizen-structure.md` để nắm rõ.
- Luôn chia các quy định/rules vào thư mục `rules/` (ví dụ: `rules/mcp.md` để bắt buộc dùng MCP).
- Phân tách agents vào `agents/` nếu cần.
- Lưu trữ file thực thi trong `scripts/`.
- Tuyệt đối giữ nguyên tắc Self-Contained.

#### Writing Patterns
- Prefer using the imperative form in instructions.
- Explain the **why** behind everything you're asking the model to do instead of heavy-handed musty MUSTs. 
- Use examples (Input/Output format).

### Test Cases

After writing the skill draft, come up with 2-3 realistic test prompts. Share them with the user.
Save test cases to `evals/evals.json`.

## Running and evaluating test cases

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Organize by iteration (`iteration-1/`, `iteration-2/`, etc.) and within that, each test case gets a directory (`eval-0/`, `eval-1/`, etc.).

### Step 1: Spawn all runs (with-skill AND baseline)

For each test case, spawn subagents (Antigravity: `invoke_subagent`; Claude Code: the Agent tool; no sub-agent tool: run them yourself one by one and say the baseline is not independent).
- **With-skill run**: Delegate to a subagent, explicitly telling it to use the new skill path.
- **Baseline run**: Delegate to another subagent without the skill (or using the old version of the skill).

### Step 2: Draft assertions

Draft quantitative assertions for each test case. Update `eval_metadata.json` and `evals/evals.json`.

### Step 3: Grade and Present via Artifacts

Once all runs are done:

1. **Grade each run**: Evaluate each assertion against the outputs.
2. **Present via Artifact**: Bạn **KHÔNG ĐƯỢC** sử dụng web server (`generate_review.py`) vì không tương thích. Thay vào đó, hãy tạo một báo cáo Markdown. Antigravity: dùng tool `write_to_file` (với ArtifactMetadata). Agent khác: ghi vào `<skill-name>-workspace/iteration-<N>/review.md` và đưa đường dẫn cho user.
   - Tên Artifact: `<skill-name>-review-iteration-<N>.md`
   - Nội dung: 
     - So sánh Output của bản cũ vs bản mới.
     - Các đánh giá định lượng (Assertions passed/failed).
     - Bảng tổng hợp thời gian/token.
   - Đặt `UserFacing=true` và hiển thị cho người dùng xem.

### Step 4: Read the feedback

User sẽ chat trực tiếp phản hồi của họ sau khi đọc Artifact. Bạn đọc phản hồi và tiến hành cải thiện skill.

## Improving the skill

1. **Generalize from the feedback.** Try branching out and using different metaphors, or recommending different patterns of working.
2. **Keep the prompt lean.** Remove things that aren't pulling their weight. 
3. **Explain the why.** Try hard to explain the why behind everything.
4. **Look for repeated work.** If multiple subagents write the same script, bundle it into `scripts/`.

Rerun test cases after making improvements.

## Antigravity (AGY) Specific Notes
- Khác với Claude Code, bạn có thể tự do sử dụng `invoke_subagent` và giao tiếp với chúng.
- Bỏ qua các bước Description Optimization bằng `claude -p` vì tool này không tồn tại trong AGY.
- Để đóng gói, chỉ cần nhắc user đẩy code lên repo `Aizen-Skills` thông qua CLI tool `node bin/cli.js sync` có sẵn.

Good luck!

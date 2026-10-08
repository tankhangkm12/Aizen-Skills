# Tài liệu Kiến trúc Hệ thống Aizen-Skills (Architecture Specifications)

Tài liệu này cung cấp toàn bộ đặc tả kiến trúc, sơ đồ thiết kế chi tiết (HLD, LLD), sơ đồ tuần tự (Sequence Diagrams), sơ đồ luồng dữ liệu (Data Flow Diagrams), cấu trúc trạng thái lưu trữ (Storage/State Schema) và hướng dẫn kết xuất sơ đồ trực quan thông qua công cụ **archify**.

---

## 1. Sơ đồ Kiến trúc Tổng thể Hệ thống (System Architecture Diagram)

```mermaid
graph TB
    subgraph UserInterface["Tầng Giao Diện & Điều Khiển"]
        CLI["Aizen CLI (bin/cli.js)"]
        NPX["skills.sh / npx skills"]
    end

    subgraph CoreEngine["Aizen Core Engine (bin/)"]
        Installer["install.js (Junction/Symlink Linker)"]
        Updater["updater.js (Git/NPM Auto Updater)"]
        ExternalMgr["external.js (Community Skills Manager)"]
        AgentsCfg["agents-config.js (Target Platform Mapping)"]
    end

    subgraph GuardAndContract["Bộ Giám Sát & Hợp Đồng (aizen-core)"]
        Guard["guard.py (Run Gate & Contract Engine)"]
        State["state.py (Workflow, Briefs & Waves)"]
        Docs["docs.py (Documentation Index & Check)"]
        Journal["journal.py (Natural Language Ledger & Stats)"]
        Check["check.py (Lint, Type, Security Gate)"]
    end

    subgraph TargetAgents["Môi Trường AI Agents Tích Hợp"]
        Claude["Claude Code (~/.claude/skills | .claude/rules)"]
        Antigravity["Antigravity / Gemini CLI (~/.gemini/ | .agents/)"]
        Cursor["Cursor (.cursor/rules/*.mdc)"]
        Windsurf["Windsurf (~/.codeium/windsurf/skills)"]
    end

    subgraph StorageAndKnowledge["Kho Tri Thức & Trạng Thái Dự Án"]
        SkillsRepo["skills/ (15 Skills, Topics & Vendor)"]
        Externals["externals.json (~/.aizen/external/)"]
        ProjectState[".aizen/ (runs/, knowledge/, PROJECT.md)"]
        TeamDocs["docs/ (architecture/, api/, data/, ops/)"]
    end

    CLI --> Installer
    CLI --> Updater
    CLI --> ExternalMgr
    CLI --> Guard

    Installer --> AgentsCfg
    Installer --> SkillsRepo
    Installer --> TargetAgents
    Installer --> ProjectState

    Guard --> ProjectState
    State --> ProjectState
    Journal --> ProjectState
    Docs --> TeamDocs

    ExternalMgr --> Externals
    ExternalMgr --> TargetAgents
```

---

## 2. Sơ đồ Thiết kế Mức cao (High-Level Design - HLD)

```mermaid
graph TD
    subgraph L1_Presentation["1. Presentation & Execution Layer"]
        Developer["Lập trình viên"]
        AgentSession["AI Agent Session (Claude Code / Antigravity / Cursor)"]
    end

    subgraph L2_Control["2. Control & Orchestration Layer"]
        CLI_Entry["Aizen CLI Engine"]
        GitHooks["Pre-Push & Tool Hooks (hooks.json, pre-push)"]
        Coordinator["Skill Coordinator (aizen-build / planner)"]
    end

    subgraph L3_DomainLogic["3. Domain Rules & Quality Gate Layer"]
        ContractGate["Run Contract Engine (sheet.md, evidence verification)"]
        ParallelWaves["Parallel Wave Scheduler (state.py waves)"]
        Verification["Independent Verifier (verdict.json >= 80%)"]
    end

    subgraph L4_DataInfrastructure["4. Data, Knowledge & Infrastructure Layer"]
        Symlinks["Platform Links (Junction / Symlink / .mdc)"]
        ProjectMap[".aizen/PROJECT.md & Run Ledger"]
        DesignDocs["docs/ (SRS, HLD, LLD, DDL, API)"]
        CommunitySkills["Community Vendor Cache"]
    end

    Developer -->|aizen sync / install| CLI_Entry
    AgentSession -->|PostToolUse / Stop Hook| GitHooks
    GitHooks --> ContractGate

    CLI_Entry --> Symlinks
    Coordinator --> ParallelWaves
    ParallelWaves --> ContractGate
    ContractGate --> Verification

    Verification --> ProjectMap
    Verification --> DesignDocs
```

---

## 3. Sơ đồ Thiết kế Mức chi tiết (Low-Level Design - LLD)

```mermaid
classDiagram
    class AizenCLI {
        +rawArgs: string[]
        +flags: Set~string~
        +positional: string[]
        +command: string
        +forwardArgs: string[]
        +main()
        +printHelp()
        +showStatus()
    }

    class Installer {
        +rootDir: string
        +skillsDir: string
        +discoverSkills() Skill[]
        +createLink(source, dest) LinkResult
        +pruneStaleLinks(dir, skills)
        +installGlobalRules(verbose, homedir)
        +updateAgentsMd(skills, projectDir)
        +runInstall(options)
        +refreshAfterUpdate()
        +hasUv() boolean
    }

    class Updater {
        +getLatestNpmVersion(packageName, timeoutMs) Promise~string~
        +checkGitUpdate() string
        +updateSkills(options) Promise~void~
        +setupScheduler(enable)
    }

    class ExternalManager {
        +list()
        +install(name)
        +update(name)
        +remove(name)
        +main(args) int
    }

    class GuardEngine {
        +cmd_install(projectDir)
        +cmd_check(runId)
        +cmd_waive(runId, stepId, reason, evidence)
        +cmd_done(runId)
        +verify_contract(sheetMd, ledger)
    }

    class StateEngine {
        +cmd_init(task, goal, slug, type)
        +cmd_brief(task, role, stage)
        +cmd_approve(task)
        +cmd_waves(task, maxUnits)
        +plan_waves(units, limit)
    }

    AizenCLI --> Installer : delegates install/sync
    AizenCLI --> Updater : delegates update/check
    AizenCLI --> ExternalManager : delegates external
    AizenCLI --> GuardEngine : executes guard commands
    StateEngine --> GuardEngine : communicates run state
```

---

## 4. Các Sơ đồ Tuần tự về Luồng Hoạt động (Sequence Diagrams)

### 4.1. Luồng Cài đặt & Đồng bộ (`aizen sync / install`)

```mermaid
sequenceDiagram
    autonumber
    actor User as Lập trình viên
    participant CLI as bin/cli.js
    participant Ins as bin/install.js
    participant FS as File System
    participant Guard as aizen-core/guard.py
    participant Agent as AI Agent Editor

    User->>CLI: aizen sync --project
    CLI->>Ins: runInstall({ project: true })
    Ins->>FS: discoverSkills() đọc skills/
    FS-->>Ins: Danh sách 15 skills hợp lệ

    Ins->>FS: createLink (NTFS Junction / Symlink)
    Note over Ins,FS: Liên kết vào ./.agents/skills và ./.claude/skills
    Ins->>FS: Sinh .cursor/rules/*.mdc (Cursor)
    Ins->>FS: Cập nhật AGENTS.md

    Ins->>Guard: runGuard(['install']) qua uv run
    Guard->>FS: Ghi .agents/hooks.json & .claude/settings.local.json
    Guard->>FS: Cài đặt .git/hooks/pre-push
    Guard->>FS: Ghi session rules (.agents/rules/ & .claude/rules/)
    Guard-->>Ins: Hoàn tất cài đặt Guard

    Ins-->>CLI: Cài đặt thành công
    CLI-->>User: In trạng thái liên kết & Live-Sync
    User->>Agent: Mở phiên làm việc mới (Agent tự nhận rules & skills)
```

### 4.2. Luồng Kiểm tra & Cập nhật (`aizen update / check`)

```mermaid
sequenceDiagram
    autonumber
    actor User as Lập trình viên / Cron
    participant CLI as bin/cli.js
    participant Upd as bin/updater.js
    participant Git as Git Remote
    participant NPM as NPM Registry
    participant Ins as bin/install.js

    User->>CLI: aizen update
    CLI->>Upd: updateSkills({ apply: true })

    alt Nếu là Git Repository
        Upd->>Git: git fetch --quiet
        Upd->>Git: git rev-list --count HEAD..@{u}
        opt Có commit mới (behind)
            Upd->>Git: git pull --rebase
            Upd->>Ins: refreshAfterUpdate()
            Ins-->>User: Cập nhật mã nguồn Git thành công
        end
    else Nếu cài đặt qua NPM package
        Upd->>NPM: getLatestNpmVersion('aizen-skills')
        opt Có version mới hơn
            Upd->>NPM: npm update -g aizen-skills
            Upd->>Ins: refreshAfterUpdate()
            Ins-->>User: Cập nhật package NPM thành công
        end
    end
    Upd-->>User: Hệ thống ở phiên bản mới nhất
```

### 4.3. Vòng đời Nhiệm vụ & Kiểm soát Chất lượng (Guard & State Flow)

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Developer / Lead
    participant Coord as AI Coordinator
    participant State as state.py
    participant Worker as Sub-agent (Dev/Tester/Reviewer)
    participant Guard as guard.py
    participant Ledger as .aizen/runs/<TASK>/ledger.jsonl

    Dev->>Coord: Giao task mới (SHOP-42)
    Coord->>State: state.py init --task SHOP-42 --goal "..."
    Coord->>State: state.py brief --role planner
    Coord->>State: state.py waves --task SHOP-42
    Note over State: Tính toán write sets & after để chia đợt song song (<= 2 units)
    Dev->>State: state.py approve --task SHOP-42 (Đóng băng acceptance.md)

    loop Cho từng Wave (Song song)
        Coord->>Worker: invoke_subagent (Module API / Module UI)
        Worker->>Ledger: Hook tự động ghi PostToolUse (file write, exec cmd)
        Worker-->>Coord: Hoàn thành code + self-test
    end

    Coord->>Worker: invoke_subagent (Reviewer)
    Worker->>Guard: Kiểm tra path:line và verdict >= 80%
    Coord->>Guard: guard.py done --run SHOP-42
    Guard->>Ledger: Kiểm tra tính toàn vẹn chữ ký hash chain & evidence
    Guard-->>Coord: Verdict: PASS -> Lưu trữ run vào archive/
    Coord-->>Dev: Tạo Pull Request (clean git history, không dấu vết AI)
```

---

## 5. Sơ đồ Luồng Dữ liệu (Data Flow Diagrams - DFD)

### 5.1. DFD Level 0 (Context Diagram)

```mermaid
flowchart TD
    User([Lập trình viên])
    ExtRepo([Kho Skill Cộng Đồng])
    GitRemote([Git Remote / NPM])
    
    AizenSystem[[HỆ THỐNG AIZEN-SKILLS]]
    
    AIEngine([AI Coding Assistants: Cursor, Claude, Antigravity])
    LocalProject[([Thư Mục Dự Án Cục Bộ])]

    User -->|1. Lệnh CLI sync / update / guard| AizenSystem
    GitRemote -->|2. Mã nguồn & Version cập nhật| AizenSystem
    ExtRepo -->|3. Community Skills| AizenSystem

    AizenSystem -->|4. Symlink / Rules / Manifests| LocalProject
    AizenSystem -->|5. Hooks / Session Rules| AIEngine

    AIEngine -->|6. Ghi chép Ledger & Evidence| LocalProject
    LocalProject -->|7. Bản đồ PROJECT.md & Design Docs| User
```

### 5.2. DFD Level 1 (Engine Data Flow)

```mermaid
flowchart LR
    subgraph Inputs
        CLIArgs[CLI Arguments]
        ExtJSON[externals.json]
        VendorLock[vendor.lock.json]
    end

    subgraph Processing[Core Processing]
        ParseArgs[Parser & Dispatcher]
        LinkEngine[Symlink & Junction Engine]
        ContractEngine[Contract Verifier Engine]
    end

    subgraph Outputs[Artifacts & Targets]
        EditorRules[Editor Rules: .mdc, .claude/rules]
        RunState[.aizen/runs/<TASK>/]
        ProjectMap[.aizen/PROJECT.md]
        DocsDir[docs/architecture, api, data]
    end

    CLIArgs --> ParseArgs
    ParseArgs --> LinkEngine
    ParseArgs --> ContractEngine

    ExtJSON --> LinkEngine
    VendorLock --> LinkEngine

    LinkEngine --> EditorRules
    ContractEngine --> RunState
    ContractEngine --> ProjectMap
    ContractEngine --> DocsDir
```

---

## 6. Sơ đồ Cấu trúc Dữ liệu & Lưu trữ (Database & State Schema)

### 6.1. Schema Khóa Phiên bản & Cấu hình

```mermaid
erDiagram
    VENDOR_LOCK_JSON {
        string name PK
        string upstream_url
        string commit_sha
        string license
        string fetched_at
    }

    EXTERNALS_JSON {
        string name PK
        string repo_url
        string branch
        string setup_command
        boolean auto_link
    }

    PLUGIN_JSON {
        string name PK
        string version
        string description
        string[] capabilities
    }

    VENDOR_LOCK_JSON ||--o{ EXTERNALS_JSON : references
```

### 6.2. Cấu trúc Trạng thái Thực thi Một Nhiệm vụ (`.aizen/runs/<TASK>/`)

```mermaid
erDiagram
    RUN_SESSION ||--|| RUN_METADATA : contains
    RUN_SESSION ||--|| PLAN_DOCUMENT : has
    RUN_SESSION ||--|| ACCEPTANCE_TESTS : enforces
    RUN_SESSION ||--o{ LEDGER_ENTRY : records
    RUN_SESSION ||--o{ WAIVER_RECORD : permits
    RUN_SESSION ||--|| VERDICT : results_in

    RUN_METADATA {
        string task_id PK
        string goal
        string slug
        string branch_name
        string status "planning | running | blocked | done"
        int parallel_max
    }

    PLAN_DOCUMENT {
        string task_id FK
        string[] modules
        string[] write_sets
        string[] delivery_waves
    }

    ACCEPTANCE_TESTS {
        string task_id FK
        string content_hash "SHA256 frozen at approve"
        string[] test_cases_Given_When_Then
    }

    LEDGER_ENTRY {
        string entry_id PK
        timestamp time
        string actor "coordinator | subagent_id"
        string action "write | exec"
        string target_path_or_cmd
        string prev_hash
        string current_hash
    }

    WAIVER_RECORD {
        string step_id PK
        string reason
        string evidence_hash
        string status "pending | accepted | rejected"
    }

    VERDICT {
        string reviewer_id
        float score ">= 0.8"
        string[] verified_evidence
    }
```

---

## 7. Tích hợp Sơ đồ Tương tác với Archify (Archify Rendering Guide)

Theo quy chuẩn thiết kế của Aizen (`skills/aizen-design/references/design/diagrams.md`), các sơ đồ văn bản / Mermaid trong `docs/` là **nguồn sự thật duy nhất (Source of Truth)**. Khi cần kết xuất sang sơ đồ tương tác chuyên nghiệp hoặc ảnh phục vụ báo cáo:

### Cách cài đặt & Kích hoạt Archify
Archify được khai báo trong `externals.json` của Aizen. Bạn có thể cài đặt thông qua:

```bash
# Cách 1: Cài đặt qua Aizen External Manager
node bin/cli.js external install archify
node bin/cli.js sync

# Cách 2: Cài đặt trực tiếp qua skills.sh
npx skills add tt-a1i/archify -a antigravity -y
```

### Quy trình Render Sơ đồ:
1. Agent đọc cấu trúc Mermaid / ASCII từ `docs/architecture/README.md`.
2. Archify xử lý các khối sơ đồ HLD, LLD, Sequence, DFD và kết xuất ra các file đồ họa tương tác tại `.aizen/docs/architecture/diagrams/*.html` (hoặc SVG/PNG).
3. Các file sơ đồ kết xuất được gắn nhãn nghiệm thu `[verified]` làm bằng chứng hoàn thành nhiệm vụ thiết kế kiến trúc.

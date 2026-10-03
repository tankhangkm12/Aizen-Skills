# Aizen Universal Structure

Mọi skill được tạo ra phải tuân thủ nghiêm ngặt kiến trúc Self-Contained của Aizen:

```
skill-name/
├── SKILL.md (bắt buộc)
│   ├── YAML frontmatter (name, description bắt buộc)
│   └── Hướng dẫn Markdown (Workflow chính)
├── rules/ (bắt buộc)
│   └── Các file .md chứa quy định bắt buộc phải tuân thủ (ví dụ: mcp.md quy định sử dụng tool).
├── agents/ (nếu có delegation)
│   └── Chứa các prompt cho sub-agent. Dùng `define_subagent` để load.
├── tools/ & scripts/ (tùy chọn)
│   └── Mã nguồn thực thi (Python, Node.js, bash,...) cho các tác vụ lặp lại.
├── references/ (tùy chọn)
│   └── Kiến thức nghiệp vụ, guidelines.
└── assets/ (tùy chọn)
    └── File tĩnh, templates.
```

## Các quy tắc quan trọng:
1. **Self-Contained**: Skill không được tham chiếu đến file nằm ngoài thư mục của nó.
2. **MCP Integration**: Luôn luôn yêu cầu tích hợp MCP server `context7` và `sequentialthinking` trong `rules/mcp.md` (nếu skill liên quan đến kỹ thuật/phân tích).

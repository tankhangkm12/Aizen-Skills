import os

KNOWLEDGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'knowledge'))
INDEX_FILE = os.path.join(KNOWLEDGE_DIR, 'INDEX.md')

def generate_index():
    if not os.path.exists(KNOWLEDGE_DIR):
        print(f"Error: Knowledge directory not found at {KNOWLEDGE_DIR}")
        return

    index_lines = [
        "# 📚 Bản Đồ Tri Thức (Knowledge Index)",
        "> **Agent Instruction:** Read this file first to find the exact path of the domain knowledge you need. Do not brute-force read the entire knowledge directory.",
        "",
        "| File Path | Description |",
        "|-----------|-------------|"
    ]

    for root, _, files in os.walk(KNOWLEDGE_DIR):
        for file in files:
            if file.endswith(".md") and file != "INDEX.md":
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, KNOWLEDGE_DIR)
                # Dùng dấu sẹc tới để path luôn chuẩn trên mọi HĐH
                rel_path = rel_path.replace('\\', '/')
                
                # Đọc 5 dòng đầu tiên để lấy mô tả (tìm thẻ Header H1 hoặc H2)
                description = "Tài liệu chuyên môn (Không có tiêu đề)"
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for _ in range(10):
                            line = f.readline().strip()
                            if line.startswith("#"):
                                description = line.lstrip("#").strip()
                                break
                except Exception:
                    pass
                
                index_lines.append(f"| `knowledge/{rel_path}` | {description} |")

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(index_lines))
        f.write('\n')

    print(f"✅ Đã tạo/cập nhật thành công {INDEX_FILE} với {len(index_lines) - 5} tài liệu.")

if __name__ == "__main__":
    generate_index()

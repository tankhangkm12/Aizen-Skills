import os
import shutil
import re

base_dir = r"D:\aizen-skill\Aizen-Skills"
scratch_cecilia_skills = os.path.join(base_dir, "scratch", "cecilia", "cecilia-skills", "skills")

# 1. Directories setup
dirs_to_make = [
    "skills/programming/database",
    "skills/programming/devops",
    "skills/programming/review",
    "skills/programming/backend",
    "skills/programming/frontend",
    "skills/programming/api",
    "skills/workflow/discovery",
    "skills/workflow/design",
    "skills/workflow/planning",
    "skills/workflow/orchestration",
    "skills/tools/testing",
    "tools/cecilia",
    "knowledge/cecilia",
    "frameworks/cecilia"
]
for d in dirs_to_make:
    os.makedirs(os.path.join(base_dir, d.replace('/', '\\')), exist_ok=True)

# 2. Rename system-rules to rules
sys_rules = os.path.join(base_dir, "system-rules")
rules = os.path.join(base_dir, "rules")
if os.path.exists(sys_rules) and not os.path.exists(rules):
    os.rename(sys_rules, rules)

# 3. Create plugin.json
with open(os.path.join(base_dir, "plugin.json"), "w", encoding="utf-8") as f:
    f.write('{\n  "name": "aizen-skills",\n  "description": "Universal AI Agent Skills, Knowledge Base, and Cecilia OS Framework.",\n  "version": "1.0.0"\n}')

# 4. Move Cecilia skills to tree
skill_map = {
    "cecilia-db": "skills/programming/database",
    "cecilia-devops": "skills/programming/devops",
    "cecilia-review": "skills/programming/review",
    "cecilia-dev-be": "skills/programming/backend",
    "cecilia-dev-fe": "skills/programming/frontend",
    "cecilia-ui": "skills/programming/frontend",
    "cecilia-api-ux": "skills/programming/api",
    "cecilia-discovery": "skills/workflow/discovery",
    "cecilia-design": "skills/workflow/design",
    "cecilia-plan": "skills/workflow/planning",
    "cecilia-orchestrator": "skills/workflow/orchestration",
    "cecilia-test": "skills/tools/testing"
}
# Notice cecilia-extend is ignored/skipped to discard it.

if os.path.exists(scratch_cecilia_skills):
    for s_name, dest_sub in skill_map.items():
        src = os.path.join(scratch_cecilia_skills, s_name)
        dest = os.path.join(base_dir, dest_sub.replace('/', '\\'), s_name)
        if os.path.exists(src) and not os.path.exists(dest):
            shutil.copytree(src, dest)
            
# Also save framework stuff
framework_src = os.path.join(base_dir, "scratch", "cecilia", "cecilia-skills")
framework_dest = os.path.join(base_dir, "frameworks", "cecilia")
for d in ["src", "templates", "tests", "tools"]:
    src = os.path.join(framework_src, d)
    dest = os.path.join(framework_dest, d)
    if os.path.exists(src) and not os.path.exists(dest):
        shutil.copytree(src, dest)

# Remove MCP from frameworks
for root, dirs, files in os.walk(framework_dest, topdown=False):
    for name in files:
        if "mcp" in name.lower():
            os.remove(os.path.join(root, name))
    for name in dirs:
        if "mcp" in name.lower():
            shutil.rmtree(os.path.join(root, name))

# 5. Extract tools/knowledge and rewrite SKILL.md
tools_dir = os.path.join(base_dir, "tools", "cecilia")
knowledge_dir = os.path.join(base_dir, "knowledge", "cecilia")
skills_dir = os.path.join(base_dir, "skills")

for root_path, dirs, files in os.walk(skills_dir):
    for d in list(dirs):
        if d.startswith("cecilia-"):
            skill_path = os.path.join(root_path, d)
            skill_name = d
            
            # move scripts -> tools
            scripts_dir = os.path.join(skill_path, "scripts")
            if os.path.exists(scripts_dir):
                for f in os.listdir(scripts_dir):
                    src_file = os.path.join(scripts_dir, f)
                    dest_file = os.path.join(tools_dir, f)
                    if os.path.isfile(src_file) and not os.path.exists(dest_file):
                        shutil.copy2(src_file, dest_file)
                shutil.rmtree(scripts_dir)
                
            # move references -> knowledge
            refs_dir = os.path.join(skill_path, "references")
            assets_dir = os.path.join(skill_path, "assets")
            skill_k_dir = os.path.join(knowledge_dir, skill_name)
            os.makedirs(skill_k_dir, exist_ok=True)
            
            if os.path.exists(refs_dir):
                for item in os.listdir(refs_dir):
                    src = os.path.join(refs_dir, item)
                    if item == "common":
                        dest = os.path.join(knowledge_dir, "common")
                        if not os.path.exists(dest): shutil.copytree(src, dest)
                    else:
                        dest = os.path.join(skill_k_dir, item)
                        if os.path.isdir(src) and not os.path.exists(dest): shutil.copytree(src, dest)
                        elif os.path.isfile(src) and not os.path.exists(dest): shutil.copy2(src, dest)
                shutil.rmtree(refs_dir)
                
            if os.path.exists(assets_dir):
                for item in os.listdir(assets_dir):
                    src = os.path.join(assets_dir, item)
                    dest = os.path.join(skill_k_dir, item)
                    if os.path.isfile(src) and not os.path.exists(dest): shutil.copy2(src, dest)
                    elif os.path.isdir(src) and not os.path.exists(dest): shutil.copytree(src, dest)
                shutil.rmtree(assets_dir)
                
            # Rewrite SKILL.md
            md_path = os.path.join(skill_path, "SKILL.md")
            if os.path.exists(md_path):
                with open(md_path, "r", encoding="utf-8") as f:
                    content = f.read()
                content = re.sub(r'\bscripts/', r'tools/cecilia/', content)
                content = re.sub(r'\breferences/common/', r'knowledge/cecilia/common/', content)
                content = re.sub(r'\breferences/', f'knowledge/cecilia/{skill_name}/', content)
                content = re.sub(r'\bassets/', f'knowledge/cecilia/{skill_name}/', content)
                
                flex = "\n\n## Aizen-Skills Integration (Flexible Execution)\n- **Knowledge Retrieval:** You are encouraged to retrieve any relevant domain knowledge from `knowledge/` as needed rather than adhering strictly to rigid paths.\n- **Skill Delegation:** Do not hesitate to use `invoke_subagent` to call other skills (both Cecilia and external skills) if they are better suited for a specific sub-task.\n"
                if "Aizen-Skills Integration" not in content:
                    content += flex
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(content)

# 6. Update install.js for plugin support & rules rename
install_js = os.path.join(base_dir, "bin", "install.js")
if os.path.exists(install_js):
    with open(install_js, "r", encoding="utf-8") as f:
        js_content = f.read()
    js_content = js_content.replace("'system-rules'", "'rules'")
    plugin_func = """
// Đăng ký toàn bộ repo như một Plugin cho Antigravity
function installAntigravityPlugin(verbose = true) {
  const homedir = os.homedir();
  const pluginTarget = path.join(homedir, '.gemini', 'config', 'plugins', 'aizen-skills');
  try {
    fs.mkdirSync(path.dirname(pluginTarget), { recursive: true });
    const res = createLink(rootDir, pluginTarget);
    if (verbose && (res.status === 'linked' || res.status === 'already-linked')) {
      console.log(`  ✓ [Antigravity Plugin] Đã đăng ký toàn bộ Aizen-Skills như một Plugin tại -> ${pluginTarget}`);
    }
  } catch (err) {
    if (verbose) console.warn(`  ! [Antigravity Plugin] Lỗi: ${err.message}`);
  }
}
"""
    if "installAntigravityPlugin" not in js_content:
        js_content = js_content.replace("// Entrypoint chính", plugin_func + "\n// Entrypoint chính")
        js_content = js_content.replace("installGlobalRules(true);", "installGlobalRules(true);\n    installAntigravityPlugin(true);")
    with open(install_js, "w", encoding="utf-8") as f:
        f.write(js_content)

# 7. Patch adversarial-code-reviewer
adv_md = os.path.join(base_dir, "skills", "programming", "review", "adversarial-code-reviewer", "SKILL.md")
if os.path.exists(adv_md):
    with open(adv_md, "r", encoding="utf-8") as f:
        content = f.read()
    if "DO NOT use when the user is asking you to write new features" not in content:
        content = content.replace("review pull requests.", "review pull requests. DO NOT use when the user is asking you to write new features, scaffold projects, or wants general programming tutorials without providing code to review.")
        with open(adv_md, "w", encoding="utf-8") as f:
            f.write(content)

# 8. Update rules/continuous-improvement.md
ci_md = os.path.join(rules, "continuous-improvement.md")
if os.path.exists(ci_md):
    with open(ci_md, "r", encoding="utf-8") as f:
        content = f.read()
    old_step = "1. **Cập nhật nội dung:** Cập nhật lại hoàn toàn nội dung/file của skill tương ứng trong thư mục `D:\aizen-skill\Aizen-Skills\skills\...`. Nếu skill cũ sai hoàn toàn, hãy viết lại toàn bộ. Đảm bảo cấu trúc cây thư mục chuẩn."
    new_step = "1. **Cập nhật nội dung theo cấu trúc phân tách:** \n   - Nếu là sửa/thêm Quy trình (Process): Sửa trong thư mục `skills/`\n   - Nếu là sửa/thêm Công cụ (Tools/Code): Sửa trong thư mục `tools/`\n   - Nếu là sửa/thêm Tri thức (Knowledge/Domain Rules): Sửa trong thư mục `knowledge/`\n   Nếu nội dung cũ sai hoàn toàn, hãy viết lại toàn bộ. Đảm bảo tuân thủ cấu trúc Decoupled Architecture."
    if "Cập nhật nội dung theo cấu trúc phân tách" not in content:
        content = content.replace(old_step, new_step)
        with open(ci_md, "w", encoding="utf-8") as f:
            f.write(content)

print("Architecture built successfully!")

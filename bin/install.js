#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const agentsConfig = require('./agents-config');
const { installedExternals, externalRoot } = require('./external');

const isWindows = process.platform === 'win32';
const rootDir = path.resolve(__dirname, '..');
const skillsDir = path.join(rootDir, 'skills');
// Đánh dấu thư mục do installer copy (khi không tạo được link) để lần sync sau thay thế được.
const COPY_MARKER = '.aizen-copy';

// Đảm bảo quyền thực thi cho các script trên Linux / macOS
function ensurePermissions(targetPath) {
  if (isWindows) return;
  try {
    const stats = fs.statSync(targetPath);
    if (stats.isDirectory()) {
      const items = fs.readdirSync(targetPath);
      for (const item of items) {
        ensurePermissions(path.join(targetPath, item));
      }
    } else if (/\.(sh|py|js)$/.test(targetPath) || path.basename(path.dirname(targetPath)) === 'bin') {
      fs.chmodSync(targetPath, 0o755);
    }
  } catch (err) {
    // Bỏ qua nếu không có quyền root
  }
}

// Trích xuất metadata từ SKILL.md
function parseSkillMetadata(skillPath) {
  const skillFile = path.join(skillPath, 'SKILL.md');
  if (!fs.existsSync(skillFile)) return null;

  try {
    const content = fs.readFileSync(skillFile, 'utf8');
    const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
    if (!match) return { name: path.basename(skillPath), description: '' };

    const frontmatter = match[1];
    const nameMatch = frontmatter.match(/^name:\s*(.+)$/m);
    const descMatch = frontmatter.match(/^description:\s*([>-]?\s*[\s\S]*?)(?=\n\w+:|$)/m);

    return {
      name: nameMatch ? nameMatch[1].trim() : path.basename(skillPath),
      description: descMatch ? descMatch[1].replace(/^[>-]\s*/, '').replace(/\s+/g, ' ').trim() : ''
    };
  } catch (err) {
    return { name: path.basename(skillPath), description: '' };
  }
}

// Quét toàn bộ skills hợp lệ (ưu tiên thư mục 'skills/', sau đó là root)
function discoverSkills(currentDir) {
  const baseDir = currentDir || (fs.existsSync(skillsDir) ? skillsDir : rootDir);
  const ignored = new Set(['.git', '.github', 'bin', 'node_modules', 'tests', 'dist', 'out']);
  let entries;
  try {
    entries = fs.readdirSync(baseDir, { withFileTypes: true });
  } catch (e) {
    return [];
  }

  let skills = [];
  for (const entry of entries) {
    if (entry.isDirectory() && !ignored.has(entry.name) && !entry.name.startsWith('.')) {
      const skillPath = path.join(baseDir, entry.name);
      if (fs.existsSync(path.join(skillPath, 'SKILL.md'))) {
        const meta = parseSkillMetadata(skillPath);
        skills.push({
          id: entry.name,
          name: meta ? meta.name : entry.name,
          description: meta ? meta.description : '',
          path: path.resolve(skillPath)
        });
      } else {
        skills = skills.concat(discoverSkills(skillPath));
      }
    }
  }
  return skills;
}

// Xóa link an toàn cho cả Windows (Junction) và Linux (Symlink)
function safeRemoveLink(linkPath) {
  try {
    const stat = fs.lstatSync(linkPath);
    if (stat.isSymbolicLink()) {
      try {
        fs.unlinkSync(linkPath);
      } catch (e) {
        fs.rmdirSync(linkPath);
      }
      return true;
    }
  } catch (e) {}
  return false;
}

// Tạo liên kết an toàn tối ưu cho cả Windows và Linux
function createLink(source, destination) {
  const resolvedSource = path.resolve(source);
  const resolvedDest = path.resolve(destination);

  // Dùng lstatSync để nhận diện chính xác cả broken/dangling symlink & junction
  let destLstat = null;
  try {
    destLstat = fs.lstatSync(resolvedDest);
  } catch (e) {
    // Thư mục đích chưa tồn tại
  }

  if (destLstat) {
    if (destLstat.isSymbolicLink()) {
      let isSame = false;
      try {
        const currentTarget = fs.realpathSync(resolvedDest);
        if (currentTarget === resolvedSource) {
          isSame = true;
        }
      } catch (e) {
        // Dangling link: không thể resolve target cũ
      }

      if (isSame) {
        return { status: 'already-linked', type: isWindows ? 'junction' : 'symlink' };
      }

      // Nếu trỏ sai đường dẫn hoặc bị đứt link, xóa để tạo lại
      safeRemoveLink(resolvedDest);
    } else if (destLstat.isDirectory()) {
      if (fs.existsSync(path.join(resolvedDest, COPY_MARKER))) {
        // Bản copy do chính installer tạo (fallback): xóa và tạo lại để không giữ file đã bị xóa ở nguồn.
        fs.rmSync(resolvedDest, { recursive: true, force: true });
      } else {
        // Thư mục thật (có thể là skill người dùng tự viết/sửa): không bao giờ tự xóa.
        console.warn(`  ! Bỏ qua ${resolvedDest}: đã có thư mục thật. Xóa hoặc đổi tên thủ công nếu muốn Live-Sync.`);
        return { status: 'directory-exists', type: 'directory' };
      }
    } else {
      try {
        fs.unlinkSync(resolvedDest);
      } catch (e) {}
    }
  }

  // Windows: 'junction' (Không cần quyền Admin). Linux/macOS: 'dir'
  const linkType = isWindows ? 'junction' : 'dir';

  try {
    fs.symlinkSync(resolvedSource, resolvedDest, linkType);
    return { status: 'linked', type: linkType };
  } catch (err) {
    // Fallback: Copy toàn bộ nếu hệ thống không cho phép symlink/junction
    try {
      copyRecursiveSync(resolvedSource, resolvedDest);
      fs.writeFileSync(path.join(resolvedDest, COPY_MARKER), 'Copied by Aizen Skills installer; the next sync replaces this folder.\n');
      return { status: 'copied-fallback', type: 'copy' };
    } catch (copyErr) {
      throw new Error(`Không thể liên kết hoặc sao chép: ${err.message}`);
    }
  }
}

// Hàm sao chép dự phòng nếu symlink bị cấm
function copyRecursiveSync(src, dest) {
  const exists = fs.existsSync(src);
  const stats = exists && fs.statSync(src);
  const isDirectory = exists && stats.isDirectory();
  if (isDirectory) {
    fs.mkdirSync(dest, { recursive: true });
    fs.readdirSync(src).forEach((childItemName) => {
      copyRecursiveSync(path.join(src, childItemName), path.join(dest, childItemName));
    });
  } else {
    fs.copyFileSync(src, dest);
  }
}

// Xóa các link trỏ vào repo nhưng skill không còn tồn tại (đổi tên/xóa skill). Chỉ đụng tới link, không đụng thư mục thật.
function pruneStaleLinks(targetDir, skills) {
  const current = new Set(skills.map(s => s.id));
  const skillsRoot = path.resolve(skillsDir) + path.sep;
  let entries = [];
  try { entries = fs.readdirSync(targetDir); } catch (e) { return; }
  for (const name of entries) {
    const p = path.join(targetDir, name);
    try {
      if (current.has(name)) continue;
      if (!fs.lstatSync(p).isSymbolicLink()) {
        // Bản copy fallback của một skill đã bị xóa khỏi repo.
        if (fs.existsSync(path.join(p, COPY_MARKER))) fs.rmSync(p, { recursive: true, force: true });
        continue;
      }
      const raw = fs.readlinkSync(p).replace(/^\\\\\?\\/, ''); // junction trên Windows có tiền tố \\?\
      const target = path.resolve(targetDir, raw) + path.sep;
      const extRoot = path.resolve(externalRoot()) + path.sep;
      // Links into this repo, or to a community skill that was removed with `aizen external remove`.
      if (target.toLowerCase().startsWith(skillsRoot.toLowerCase())) safeRemoveLink(p);
      else if (target.toLowerCase().startsWith(extRoot.toLowerCase()) && !fs.existsSync(target)) safeRemoveLink(p);
    } catch (e) {}
  }
}

// Cài đặt toàn cục (Global - Cho mọi AI Agent trên máy)
function installGlobal(skills, verbose = true) {
  const results = [];
  for (const agent of agentsConfig.global) {
    try {
      fs.mkdirSync(agent.targetDir, { recursive: true });
      pruneStaleLinks(agent.targetDir, skills);
      let count = 0;
      for (const skill of skills) {
        const dest = path.join(agent.targetDir, skill.id);
        const res = createLink(skill.path, dest);
        if (res.status === 'linked' || res.status === 'already-linked' || res.status === 'copied-fallback') {
          count++;
        }
      }
      results.push({ agent: agent.name, path: agent.targetDir, installed: count, ok: true });
      if (verbose) {
        console.log(`  ✓ [${agent.name}] Đã liên kết ${count}/${skills.length} skills -> ${agent.targetDir}`);
      }
    } catch (err) {
      results.push({ agent: agent.name, path: agent.targetDir, installed: 0, ok: false, error: err.message });
      if (verbose) {
        console.warn(`  ! [${agent.name}] Lỗi: ${err.message}`);
      }
    }
  }
  return results;
}

// Cài đặt theo dự án (Project-level)
function installProject(skills, projectDir = process.cwd(), verbose = true) {
  const results = [];

  for (const agent of agentsConfig.project) {
    try {
      const targetDir = agent.targetDir(projectDir);
      fs.mkdirSync(targetDir, { recursive: true });

      if (agent.type === 'skill-dir') {
        pruneStaleLinks(targetDir, skills);
        let count = 0;
        for (const skill of skills) {
          const dest = path.join(targetDir, skill.id);
          const res = createLink(skill.path, dest);
          if (res.status === 'linked' || res.status === 'already-linked') count++;
        }
        results.push({ agent: agent.name, path: targetDir, installed: count, ok: true });
        if (verbose) console.log(`  ✓ [${agent.name}] Đã liên kết ${count} skills -> ${targetDir}`);
      } else if (agent.type === 'cursor-mdc') {
        for (const skill of skills) {
          const mdcPath = path.join(targetDir, `${skill.id}.mdc`);
          const skillMd = path.join(skill.path, 'SKILL.md');
          const mdcContent = `---
description: ${skill.description}
globs: *
alwaysApply: false
${fs.readFileSync(skillMd, 'utf8')}
`;
          fs.writeFileSync(mdcPath, mdcContent, 'utf8');
        }
        for (const src of repoRules()) {
          const mdcPath = path.join(targetDir, path.basename(src, '.md') + '.mdc');
          fs.writeFileSync(mdcPath, `---\nalwaysApply: true\n---\n${fs.readFileSync(src, 'utf8')}`, 'utf8');
        }
        results.push({ agent: agent.name, path: targetDir, installed: skills.length, ok: true });
        if (verbose) console.log(`  ✓ [${agent.name}] Đã tạo ${skills.length} Cursor rules (.mdc) -> ${targetDir}`);
      }
    } catch (err) {
      results.push({ agent: agent.name, error: err.message, ok: false });
    }
  }

  // Cập nhật bảng chỉ dẫn AGENTS.md
  updateAgentsMd(skills, projectDir, verbose);
  // Hook ép quy trình aizen-build (Claude Code + Antigravity + git pre-push) cho riêng dự án này
  installGuard(projectDir, verbose);
  return results;
}

// guard.py của aizen-core: hợp đồng chung cho mọi skill — hook Claude Code + Antigravity + pre-push, chỉ trong dự án
const coreScripts = path.join(skillsDir, 'aizen-core', 'scripts', 'core');
const guardScript = path.join(coreScripts, 'guard.py');

function hasUv() {
  return true;
}

function runGuard(args, options = {}, script = guardScript) {
  const { spawnSync } = require('child_process');
  const r = spawnSync('uv', ['run', '--quiet', '--script', script, ...args], { stdio: options.stdio || 'inherit', encoding: 'utf8' });
  return r.status === null ? 1 : r.status;
}

function installGuard(projectDir = process.cwd(), verbose = true) {
  if (!fs.existsSync(guardScript)) return;
  if (verbose) console.log('  [Aizen Guard] Cài hợp đồng chung cho dự án (hook, .aizen/, PROJECT.md):');
  runGuard(['install', '--workspace', projectDir], { stdio: verbose ? 'inherit' : 'ignore' });
}

// Cập nhật AGENTS.md
function updateAgentsMd(skills, projectDir, verbose = true) {
  const agentsMdFile = path.join(projectDir, 'AGENTS.md');
  const sectionHeader = '## Available Skills (Auto-managed by Aizen Skills)';
  const skillList = skills.map(s => `- **${s.name}** (\`.agents/skills/${s.id}/SKILL.md\`): ${s.description}`).join('\n');
  const ruleList = repoRules().map(r => `- Luôn áp dụng rule: \`${r}\``).join('\n');
  const block = [skillList, ruleList].filter(Boolean).join('\n\n');

  try {
    let existingContent = '';
    if (fs.existsSync(agentsMdFile)) {
      existingContent = fs.readFileSync(agentsMdFile, 'utf8');
    }

    if (existingContent.includes(sectionHeader)) {
      const escaped = sectionHeader.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp(`${escaped}[\\s\\S]*?(?=\n## |$)`);
      existingContent = existingContent.replace(regex, () => `${sectionHeader}\n\n${block}\n`);
    } else {
      existingContent = existingContent ? `${existingContent.trim()}\n\n${sectionHeader}\n\n${block}\n` : `# Project Agents Guide\n\n${sectionHeader}\n\n${block}\n`;
    }

    fs.writeFileSync(agentsMdFile, existingContent, 'utf8');
    if (verbose) console.log(`  ✓ [AGENTS.md] Đã cập nhật bảng kỹ năng -> ${agentsMdFile}`);
  } catch (e) {
    if (verbose) console.warn(`  ! Không thể cập nhật AGENTS.md: ${e.message}`);
  }
}

// Luật phiên làm việc nằm trong aizen-core/rules/ để đi cùng skill khi cài bằng skills.sh
function repoRules() {
  const rulesDir = path.join(skillsDir, 'aizen-core', 'rules');
  return fs.existsSync(rulesDir) ? fs.readdirSync(rulesDir).filter(f => f.endsWith('.md')).map(f => path.join(rulesDir, f)) : [];
}

// Cài system-rules toàn cục: Antigravity (~/.gemini/config/rules) và Claude Code (~/.claude/rules)
function installGlobalRules(verbose = true, homedir = os.homedir()) {
  const rules = repoRules();
  if (!rules.length) return;
  // Antigravity bỏ qua file rule thiếu front-matter `trigger`
  const targets = [
    ['Antigravity Rules', path.join(homedir, '.gemini', 'config', 'rules'), '---\ntrigger: always_on\n---\n'],
    ['Claude Code Rules', path.join(homedir, '.claude', 'rules'), ''],
  ];
  for (const [name, dir, head] of targets) {
    try {
      fs.mkdirSync(dir, { recursive: true });
      for (const src of rules) fs.writeFileSync(path.join(dir, path.basename(src)), head + fs.readFileSync(src, 'utf8'), 'utf8');
      if (verbose) console.log(`  ✓ [${name}] Đã sao chép ${rules.length} system rules -> ${dir}`);
    } catch (err) {
      if (verbose) console.warn(`  ! [${name}] Lỗi: ${err.message}`);
    }
  }
}

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

// Entrypoint chính
function runInstall(options = {}) {
  const argv = options.argv || process.argv;
  if (options.postinstall || argv.includes('--postinstall')) {
    // npm install không còn tự liên kết toàn máy: người dùng chọn rõ phạm vi.
    console.log('\n[Aizen Skills] Đã tải mã nguồn. Chưa liên kết vào agent nào. Chọn một:');
    console.log('  · Cho một dự án:  cd <dự án> && node ' + path.join(rootDir, 'bin', 'cli.js') + ' sync --project');
    console.log('  · Cho toàn máy:   node ' + path.join(rootDir, 'bin', 'cli.js') + ' sync --global');
    console.log('  · Không cần clone: npx skills add tankhangkm12/Aizen-Skills (xem README)\n');
    return;
  }

  const isGlobal = options.global || argv.includes('--global');
  const isProject = options.project || argv.includes('--project') || !isGlobal;
  if (isProject && !isGlobal && path.resolve(process.cwd()) === path.resolve(rootDir)) {
    console.error('[Aizen Skills] Đang đứng trong repo Aizen-Skills. Hãy `cd` vào dự án rồi `sync --project`, hoặc dùng `sync --global`.');
    process.exitCode = 2;
    return;
  }

  // Cấp quyền thực thi nếu chạy trên Linux / macOS
  ensurePermissions(rootDir);

  console.log('\n==================================================');
  console.log('  🚀 AIZEN SKILLS - MULTI-AGENT AUTO INSTALLER');
  console.log(`  OS: ${process.platform} (${isWindows ? 'NTFS Junction' : 'Symlink'})`);
  console.log('==================================================\n');

  const own = discoverSkills();
  const ext = installedExternals();
  const skills = own.concat(ext.filter(e => !own.some(s => s.id === e.id)));
  console.log(`[1] Phát hiện ${own.length} skills trong thư mục 'skills/' + ${ext.length} skill cộng đồng đã cài (aizen external):`);
  skills.forEach(s => console.log(`  - ${s.id}${s.external ? ' [cộng đồng]' : ''}: ${s.description.slice(0, 75)}...`));
  console.log('');

  if (isGlobal) {
    console.log('[2] Đang tự động liên kết vào các AI Agent trên máy (Global Mode):');
    installGlobal(skills, true);
    installGlobalRules(true);
    installAntigravityPlugin(true);
  }

  if (isProject) {
    console.log('\n[3] Đang triển khai vào thư mục dự án hiện tại (Project Mode):');
    installProject(skills, process.cwd(), true);
  }

  console.log('\n==================================================');
  console.log('  ✨ Hoàn tất! Toàn bộ AI Agent đã sẵn sàng dùng skills.');
  console.log('     Mọi cập nhật trong repo sẽ tự động đồng bộ (Live-Sync).');
  console.log('==================================================\n');
}

// Sau `aizen update`: junction đã tự thấy nội dung mới; chỉ cần liên kết lại toàn máy nếu trước đó đã cài toàn máy.
function refreshAfterUpdate() {
  const hadGlobal = agentsConfig.global.some(a => fs.existsSync(path.join(a.targetDir, 'aizen-core')));
  if (hadGlobal) runInstall({ global: true });
  console.log('  ℹ Dự án cài bằng `sync --project` tự thấy bản mới; skill mới thêm vào thì chạy lại `sync --project` trong dự án đó.');
  console.log('  ℹ Dự án cài bằng skills.sh: chạy `npx skills update` trong dự án đó.');
}

if (require.main === module) {
  runInstall();
}

module.exports = {
  discoverSkills,
  installGlobal,
  installProject,
  installGlobalRules,
  updateAgentsMd,
  installGuard,
  runGuard,
  coreScripts,
  createLink,
  safeRemoveLink,
  pruneStaleLinks,
  runInstall,
  refreshAfterUpdate,
  hasUv
};

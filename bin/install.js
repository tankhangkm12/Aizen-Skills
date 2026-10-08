#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const { installedExternals, externalRoot } = require('./external');
const { discoverPlugins, getPlugin, validatePlugin, createPluginScaffold } = require('./plugins');

const isWindows = process.platform === 'win32';
const rootDir = path.resolve(__dirname, '..');
const skillsDir = path.join(rootDir, 'skills');
const COPY_MARKER = '.aizen-copy';

// Đảm bảo quyền thực thi cho script
function ensurePermissions(targetPath) {
  if (isWindows) return;
  try {
    const stats = fs.statSync(targetPath);
    if (stats.isDirectory()) {
      const items = fs.readdirSync(targetPath);
      for (const item of items) ensurePermissions(path.join(targetPath, item));
    } else if (/\.(sh|py|js)$/.test(targetPath) || path.basename(path.dirname(targetPath)) === 'bin') {
      fs.chmodSync(targetPath, 0o755);
    }
  } catch (err) {}
}

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

function discoverSkills(currentDir) {
  const baseDir = currentDir || (fs.existsSync(skillsDir) ? skillsDir : rootDir);
  const ignored = new Set(['.git', '.github', 'bin', 'plugins', 'node_modules', 'tests', 'dist', 'out']);
  let entries;
  try { entries = fs.readdirSync(baseDir, { withFileTypes: true }); } catch (e) { return []; }

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

function safeRemoveLink(linkPath) {
  try {
    const stat = fs.lstatSync(linkPath);
    if (stat.isSymbolicLink()) {
      try { fs.unlinkSync(linkPath); } catch (e) { fs.rmdirSync(linkPath); }
      return true;
    }
  } catch (e) {}
  return false;
}

function createLink(source, destination) {
  const resolvedSource = path.resolve(source);
  const resolvedDest = path.resolve(destination);

  let destLstat = null;
  try { destLstat = fs.lstatSync(resolvedDest); } catch (e) {}

  if (destLstat) {
    if (destLstat.isSymbolicLink()) {
      let isSame = false;
      try {
        if (fs.realpathSync(resolvedDest) === resolvedSource) isSame = true;
      } catch (e) {}
      if (isSame) return { status: 'already-linked', type: isWindows ? 'junction' : 'symlink' };
      safeRemoveLink(resolvedDest);
    } else if (destLstat.isDirectory()) {
      if (fs.existsSync(path.join(resolvedDest, COPY_MARKER))) {
        fs.rmSync(resolvedDest, { recursive: true, force: true });
      } else {
        console.warn(`  ! Bỏ qua ${resolvedDest}: đã có thư mục thật.`);
        return { status: 'directory-exists', type: 'directory' };
      }
    } else {
      try { fs.unlinkSync(resolvedDest); } catch (e) {}
    }
  }

  const linkType = isWindows ? 'junction' : 'dir';
  try {
    fs.symlinkSync(resolvedSource, resolvedDest, linkType);
    return { status: 'linked', type: linkType };
  } catch (err) {
    try {
      copyRecursiveSync(resolvedSource, resolvedDest);
      fs.writeFileSync(path.join(resolvedDest, COPY_MARKER), 'Copied by Aizen; the next sync replaces this folder.\n');
      return { status: 'copied-fallback', type: 'copy' };
    } catch (copyErr) {
      throw new Error(`Không thể liên kết hoặc sao chép: ${err.message}`);
    }
  }
}

function copyRecursiveSync(src, dest) {
  const exists = fs.existsSync(src);
  const stats = exists && fs.statSync(src);
  if (exists && stats.isDirectory()) {
    fs.mkdirSync(dest, { recursive: true });
    fs.readdirSync(src).forEach((child) => copyRecursiveSync(path.join(src, child), path.join(dest, child)));
  } else if (exists) {
    fs.copyFileSync(src, dest);
  }
}

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
        if (fs.existsSync(path.join(p, COPY_MARKER))) fs.rmSync(p, { recursive: true, force: true });
        continue;
      }
      const raw = fs.readlinkSync(p).replace(/^\\\\\?\\/, '');
      const target = path.resolve(targetDir, raw) + path.sep;
      const extRoot = path.resolve(externalRoot()) + path.sep;
      if (target.toLowerCase().startsWith(skillsRoot.toLowerCase())) safeRemoveLink(p);
      else if (target.toLowerCase().startsWith(extRoot.toLowerCase()) && !fs.existsSync(target)) safeRemoveLink(p);
    } catch (e) {}
  }
}

function setupProjectMcp(projectDir, plugin, verbose = true) {
  const mcpConfigFile = path.join(projectDir, '.mcp.json');
  let currentConfig = { mcpServers: {} };

  if (fs.existsSync(mcpConfigFile)) {
    try { currentConfig = JSON.parse(fs.readFileSync(mcpConfigFile, 'utf8')); } catch (e) {}
  }
  if (!currentConfig.mcpServers) currentConfig.mcpServers = {};

  const templateFile = path.join(plugin.path, 'mcp.template.json');
  if (fs.existsSync(templateFile)) {
    try {
      const template = JSON.parse(fs.readFileSync(templateFile, 'utf8'));
      if (template.mcpServers) {
        for (const [k, v] of Object.entries(template.mcpServers)) {
          if (!currentConfig.mcpServers[k]) currentConfig.mcpServers[k] = v;
        }
      }
      fs.writeFileSync(mcpConfigFile, JSON.stringify(currentConfig, null, 2), 'utf8');
      if (verbose) console.log(`  ✓ [.mcp.json] Đã cấu hình MCP Servers cho dự án -> ${mcpConfigFile}`);
    } catch (e) {
      if (verbose) console.warn(`  ! Không thể ghi .mcp.json: ${e.message}`);
    }
  }
}

function generateSlashCommands(projectDir, plugin, verbose = true) {
  const claudeCommandsDir = path.join(projectDir, '.claude', 'commands');
  try {
    fs.mkdirSync(claudeCommandsDir, { recursive: true });
    const pluginCmdFile = path.join(claudeCommandsDir, `aizen-skills:${plugin.id.replace(/^aizen-/, '')}.md`);
    const workflowContent = fs.existsSync(path.join(plugin.path, 'workflow.md'))
      ? fs.readFileSync(path.join(plugin.path, 'workflow.md'), 'utf8')
      : plugin.description;
    
    const cmdBody = `---
description: ${plugin.description}
---

# Aizen Plugin: ${plugin.name}

${workflowContent}
`;
    fs.writeFileSync(pluginCmdFile, cmdBody, 'utf8');

    const shortcuts = [
      ['penpot', 'Thiết kế giao diện Canvas trực tiếp trên Penpot qua MCP.'],
      ['playwright', 'Kiểm thử trình duyệt thật, chụp ảnh màn hình và visual regression qua Playwright MCP.'],
      ['archify', 'Trực quan hóa sơ đồ kiến trúc HLD, LLD, Sequence, DFD sang HTML/SVG.']
    ];

    for (const [tool, desc] of shortcuts) {
      const toolFile = path.join(claudeCommandsDir, `aizen-skills:${tool}.md`);
      fs.writeFileSync(toolFile, `---\ndescription: ${desc}\n---\n# Aizen Tool: ${tool}\n\n${desc}\n`, 'utf8');
    }

    if (verbose) console.log(`  ✓ [Slash Commands] Đã đăng ký lệnh /aizen-skills:* vào .claude/commands/`);
  } catch (e) {
    if (verbose) console.warn(`  ! Không thể sinh Slash Commands: ${e.message}`);
  }
}

function installProject(skills, projectDir = process.cwd(), plugin, verbose = true) {
  const results = [];
  const targets = [
    { name: 'Antigravity / Gemini CLI', dir: path.join(projectDir, '.agents', 'skills') },
    { name: 'Claude Code', dir: path.join(projectDir, '.claude', 'skills') }
  ];

  for (const t of targets) {
    try {
      fs.mkdirSync(t.dir, { recursive: true });
      pruneStaleLinks(t.dir, skills);
      let count = 0;
      for (const skill of skills) {
        const dest = path.join(t.dir, skill.id);
        const res = createLink(skill.path, dest);
        if (res.status === 'linked' || res.status === 'already-linked') count++;
      }
      results.push({ agent: t.name, path: t.dir, installed: count, ok: true });
      if (verbose) console.log(`  ✓ [${t.name}] Đã liên kết ${count} skills -> ${t.dir}`);
    } catch (err) {
      results.push({ agent: t.name, error: err.message, ok: false });
    }
  }

  if (plugin) {
    setupProjectMcp(projectDir, plugin, verbose);
    generateSlashCommands(projectDir, plugin, verbose);
  }

  updateAgentsMd(skills, projectDir, verbose);
  installGuard(projectDir, verbose);
  return results;
}

const coreScripts = path.join(skillsDir, 'aizen-core', 'scripts', 'core');
const guardScript = path.join(coreScripts, 'guard.py');

function hasUv() { return true; }

function runGuard(args, options = {}, script = guardScript) {
  const { spawnSync } = require('child_process');
  const r = spawnSync('uv', ['run', '--quiet', '--script', script, ...args], { stdio: options.stdio || 'inherit', encoding: 'utf8' });
  return r.status === null ? 1 : r.status;
}

function installGuard(projectDir = process.cwd(), verbose = true) {
  if (!fs.existsSync(guardScript)) return;
  if (verbose) console.log('  [Aizen Guard] Cài hợp đồng kiểm soát chất lượng (hook, .aizen/, PROJECT.md):');
  runGuard(['install', '--workspace', projectDir], { stdio: verbose ? 'inherit' : 'ignore' });
}

function updateAgentsMd(skills, projectDir, verbose = true) {
  const agentsMdFile = path.join(projectDir, 'AGENTS.md');
  const sectionHeader = '## Available Skills (Auto-managed by Aizen Skills)';
  const skillList = skills.map(s => `- **${s.name}** (\`.agents/skills/${s.id}/SKILL.md\`): ${s.description}`).join('\n');
  const ruleList = repoRules().map(r => `- Luôn áp dụng rule: \`${r}\``).join('\n');
  const block = [skillList, ruleList].filter(Boolean).join('\n\n');

  try {
    let existingContent = fs.existsSync(agentsMdFile) ? fs.readFileSync(agentsMdFile, 'utf8') : '';
    if (existingContent.includes(sectionHeader)) {
      const escaped = sectionHeader.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp(`${escaped}[\\s\\S]*?(?=\n## |$)`);
      existingContent = existingContent.replace(regex, () => `${sectionHeader}\n\n${block}\n`);
    } else {
      existingContent = existingContent ? `${existingContent.trim()}\n\n${sectionHeader}\n\n${block}\n` : `# Project Instructions\n\n${sectionHeader}\n\n${block}\n`;
    }
    fs.writeFileSync(agentsMdFile, existingContent, 'utf8');
    if (verbose) console.log(`  ✓ [AGENTS.md] Đã cập nhật bảng kỹ năng -> ${agentsMdFile}`);
  } catch (e) {
    if (verbose) console.warn(`  ! Không thể cập nhật AGENTS.md: ${e.message}`);
  }
}

function repoRules() {
  const rulesDir = path.join(skillsDir, 'aizen-core', 'rules');
  return fs.existsSync(rulesDir) ? fs.readdirSync(rulesDir).filter(f => f.endsWith('.md')).map(f => path.join(rulesDir, f)) : [];
}

function installGlobalRules(verbose = true, homedir = os.homedir()) {
  const rules = repoRules();
  if (!rules.length) return;
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

// Entrypoint chính: Chuyên biệt hóa cho dự án cục bộ (Project-Level Only)
function runInstall(options = {}) {
  const argv = options.argv || process.argv;
  const projectDir = options.projectDir || process.cwd();

  if (path.resolve(projectDir) === path.resolve(rootDir)) {
    console.error('[Aizen Skills] Đang đứng trong repo Aizen-Skills gốc. Hãy `cd` vào dự án cần cài rồi chạy lệnh.');
    process.exitCode = 2;
    return;
  }

  let pluginArg = options.plugin;
  if (!pluginArg) {
    const pIdx = argv.indexOf('--plugin');
    if (pIdx !== -1 && argv[pIdx + 1]) pluginArg = argv[pIdx + 1];
  }
  const targetPlugin = getPlugin(pluginArg || 'full') || getPlugin('aizen-full') || discoverPlugins()[0];

  ensurePermissions(rootDir);

  console.log('\n==================================================');
  console.log('  🚀 AIZEN PLUGIN SUITE - PROJECT INSTALLER');
  console.log(`  Plugin Mục Tiêu: [${targetPlugin ? targetPlugin.name : 'All'}]`);
  console.log(`  Thư Mục Dự Án : ${projectDir}`);
  console.log('==================================================\n');

  const allSkills = discoverSkills();
  const ext = installedExternals();
  let selectedSkills = allSkills;

  if (targetPlugin && targetPlugin.manifest && Array.isArray(targetPlugin.manifest.skills) && targetPlugin.manifest.skills.length > 0) {
    const wanted = new Set(targetPlugin.manifest.skills);
    wanted.add('aizen-core');
    selectedSkills = allSkills.filter(s => wanted.has(s.id));
  }
  const skills = selectedSkills.concat(ext.filter(e => !selectedSkills.some(s => s.id === e.id)));

  console.log(`[1] Triển khai ${skills.length} skills vào dự án:`);
  skills.forEach(s => console.log(`  - 📦 ${s.id}: ${s.description.slice(0, 65)}...`));
  console.log('');

  console.log('[2] Đang thiết lập các môi trường AI Agent (Antigravity & Claude Code):');
  installProject(skills, projectDir, targetPlugin, true);

  console.log('\n==================================================');
  console.log(`  ✨ Hoàn tất! Plugin [${targetPlugin ? targetPlugin.name : 'Aizen'}] đã sẵn sàng.`);
  console.log('  💡 Gọi lệnh nhanh trong AI chat: /aizen-skills:design, /aizen-skills:code, /aizen-skills:penpot');
  console.log('==================================================\n');
}

function refreshAfterUpdate() {
  runInstall();
}

if (require.main === module) {
  runInstall();
}

module.exports = {
  discoverSkills,
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

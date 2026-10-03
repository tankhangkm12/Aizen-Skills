#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const agentsConfig = require('./agents-config');

const isWindows = process.platform === 'win32';
const rootDir = path.resolve(__dirname, '..');
const skillsDir = path.join(rootDir, 'skills');

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
    const descMatch = frontmatter.match(/^description:\s*([>|-]?\s*[\s\S]*?)(?=\n\w+:|$)/m);

    return {
      name: nameMatch ? nameMatch[1].trim() : path.basename(skillPath),
      description: descMatch ? descMatch[1].replace(/^[>|-]\s*/, '').replace(/\s+/g, ' ').trim() : ''
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
      // Nếu là thư mục tĩnh cũ (ví dụ do skills.sh copy trước đó), tự động nâng cấp sang Junction/Symlink để kích hoạt Live-Sync!
      const destSkillMd = path.join(resolvedDest, 'SKILL.md');
      const hasGit = fs.existsSync(path.join(resolvedDest, '.git'));
      if (fs.existsSync(destSkillMd) && !hasGit) {
        try {
          fs.rmSync(resolvedDest, { recursive: true, force: true });
        } catch (e) {
          return { status: 'directory-exists', type: 'directory' };
        }
      } else {
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

// Cài đặt toàn cục (Global - Cho mọi AI Agent trên máy)
function installGlobal(skills, verbose = true) {
  const results = [];

  for (const agent of agentsConfig.global) {
    try {
      fs.mkdirSync(agent.targetDir, { recursive: true });
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
---
${fs.readFileSync(skillMd, 'utf8')}
`;
          fs.writeFileSync(mdcPath, mdcContent, 'utf8');
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
  return results;
}

// Cập nhật AGENTS.md
function updateAgentsMd(skills, projectDir, verbose = true) {
  const agentsMdFile = path.join(projectDir, 'AGENTS.md');
  const sectionHeader = '## Available Skills (Auto-managed by Aizen Skills)';
  const skillList = skills.map(s => `- **${s.name}** (\`.agents/skills/${s.id}/SKILL.md\`): ${s.description}`).join('\n');

  try {
    let existingContent = '';
    if (fs.existsSync(agentsMdFile)) {
      existingContent = fs.readFileSync(agentsMdFile, 'utf8');
    }

    if (existingContent.includes(sectionHeader)) {
      const regex = new RegExp(`${sectionHeader}[\\s\\S]*?(?=\\n## |$)`);
      existingContent = existingContent.replace(regex, `${sectionHeader}\n\n${skillList}\n`);
    } else {
      existingContent = existingContent ? `${existingContent.trim()}\n\n${sectionHeader}\n\n${skillList}\n` : `# Project Agents Guide\n\n${sectionHeader}\n\n${skillList}\n`;
    }

    fs.writeFileSync(agentsMdFile, existingContent, 'utf8');
    if (verbose) console.log(`  ✓ [AGENTS.md] Đã cập nhật bảng kỹ năng -> ${agentsMdFile}`);
  } catch (e) {
    if (verbose) console.warn(`  ! Không thể cập nhật AGENTS.md: ${e.message}`);
  }
}

// Entrypoint chính
function runInstall(options = {}) {
  const isAuto = options.auto || process.argv.includes('--auto');
  const isProject = options.project || process.argv.includes('--project');
  const isGlobal = options.global || process.argv.includes('--global') || !isProject;

  // Cấp quyền thực thi nếu chạy trên Linux / macOS
  ensurePermissions(rootDir);

  console.log('\n==================================================');
  console.log('  🚀 AIZEN SKILLS - MULTI-AGENT AUTO INSTALLER');
  console.log(`  OS: ${process.platform} (${isWindows ? 'NTFS Junction' : 'Symlink'})`);
  console.log('==================================================\n');

  const skills = discoverSkills();
  console.log(`[1] Phát hiện ${skills.length} skills trong thư mục 'skills/':`);
  skills.forEach(s => console.log(`    - ${s.id}: ${s.description.slice(0, 75)}...`));
  console.log('');

  if (isGlobal) {
    console.log('[2] Đang tự động liên kết vào các AI Agent trên máy (Global Mode):');
    installGlobal(skills, true);
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

if (require.main === module) {
  runInstall();
}

module.exports = {
  discoverSkills,
  installGlobal,
  installProject,
  createLink,
  safeRemoveLink,
  runInstall
};

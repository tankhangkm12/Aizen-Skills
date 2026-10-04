'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { discoverSkills, createLink, pruneStaleLinks, safeRemoveLink, installGlobalRules, updateAgentsMd } = require('../bin/install');

console.log('[TEST] Bắt đầu kiểm tra hệ thống Aizen Skills Installer...\n');

// 1. Test discoverSkills
const skills = discoverSkills();
console.log(`[TEST 1] Kiểm tra phát hiện skills: tìm thấy ${skills.length} skills.`);
assert(skills.length >= 2, 'Phải tìm thấy ít nhất 2 skills (database-table-design & video-to-skill)');

const dbSkill = skills.find(s => s.id === 'database-table-design');
assert(dbSkill, 'Phải tìm thấy database-table-design');
assert(dbSkill.description.length > 20, 'database-table-design phải có description hợp lệ');
console.log('  ✓ database-table-design: OK');

const videoSkill = skills.find(s => s.id === 'video-to-skill');
assert(videoSkill, 'Phải tìm thấy video-to-skill');
assert(videoSkill.description.length > 20, 'video-to-skill phải có description hợp lệ');
console.log('  ✓ video-to-skill: OK');

// 2. Test createLink (Junction trên Windows / Symlink trên Unix)
console.log('\n[TEST 2] Kiểm tra cơ chế Directory Junction / Symlink...');
const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'aizen-test-'));
const testTarget = path.join(tempDir, 'database-table-design');

try {
  const linkRes = createLink(dbSkill.path, testTarget);
  console.log(`  ✓ Kết quả liên kết: ${linkRes.status} (loại: ${linkRes.type})`);
  assert(fs.existsSync(testTarget), 'Thư mục đích phải tồn tại sau khi liên kết');

  const targetSkillMd = path.join(testTarget, 'SKILL.md');
  assert(fs.existsSync(targetSkillMd), 'SKILL.md phải đọc được từ thư mục đích');
  console.log('  ✓ SKILL.md đọc được xuyên qua Junction/Symlink: OK');

  // Kiểm tra tính Live-Sync
  const sourceStat = fs.statSync(path.join(dbSkill.path, 'SKILL.md'));
  const destStat = fs.statSync(targetSkillMd);
  assert.strictEqual(sourceStat.size, destStat.size, 'Kích thước file nguồn và đích phải hoàn toàn đồng nhất');
  console.log('  ✓ Tính đồng bộ tức thì (Live-Sync): OK');
} finally {
  // Dọn dẹp thư mục test
  try {
    if (fs.existsSync(testTarget)) {
      const stat = fs.lstatSync(testTarget);
      if (stat.isSymbolicLink()) {
        fs.unlinkSync(testTarget);
      } else {
        fs.rmSync(testTarget, { recursive: true, force: true });
      }
    }
    fs.rmSync(tempDir, { recursive: true, force: true });
  } catch (e) {}
}

// 3. Test pruneStaleLinks + không xóa thư mục thật
console.log('\n[TEST 3] Kiểm tra dọn link cũ và bảo vệ thư mục người dùng...');
const pruneDir = fs.mkdtempSync(path.join(os.tmpdir(), 'aizen-prune-'));
const ghost = path.join(skillsRoot(), '__ghost_skill__');
try {
  fs.mkdirSync(ghost);
  const linkType = process.platform === 'win32' ? 'junction' : 'dir';
  fs.symlinkSync(ghost, path.join(pruneDir, '__ghost_skill__'), linkType);
  fs.symlinkSync(dbSkill.path, path.join(pruneDir, 'database-table-design'), linkType);
  fs.mkdirSync(path.join(pruneDir, 'my-own-skill'));
  fs.writeFileSync(path.join(pruneDir, 'my-own-skill', 'SKILL.md'), 'x');
  fs.mkdirSync(path.join(pruneDir, 'video-to-skill'));
  fs.writeFileSync(path.join(pruneDir, 'video-to-skill', 'SKILL.md'), 'user edit');

  pruneStaleLinks(pruneDir, skills);
  assert(!fs.existsSync(path.join(pruneDir, '__ghost_skill__')), 'Link tới skill đã xóa phải bị dọn');
  assert(fs.existsSync(path.join(pruneDir, 'database-table-design', 'SKILL.md')), 'Link hợp lệ phải được giữ');
  assert(fs.existsSync(path.join(pruneDir, 'my-own-skill', 'SKILL.md')), 'Thư mục người dùng phải được giữ');

  const res = createLink(videoSkill.path, path.join(pruneDir, 'video-to-skill'));
  assert.strictEqual(res.status, 'directory-exists');
  assert.strictEqual(fs.readFileSync(path.join(pruneDir, 'video-to-skill', 'SKILL.md'), 'utf8'), 'user edit',
    'createLink không được ghi đè thư mục thật trùng tên');
  console.log('  ✓ Dọn link cũ / giữ thư mục thật: OK');
} finally {
  fs.rmSync(ghost, { recursive: true, force: true });
  for (const n of fs.readdirSync(pruneDir)) {
    const p = path.join(pruneDir, n);
    if (fs.lstatSync(p).isSymbolicLink()) safeRemoveLink(p);
  }
  fs.rmSync(pruneDir, { recursive: true, force: true });
}

// 4. Rules tới Antigravity + Claude Code; AGENTS.md cập nhật tại chỗ khi sync lại
console.log('\n[TEST 4] Kiểm tra cài rules và AGENTS.md...');
const fakeHome = fs.mkdtempSync(path.join(os.tmpdir(), 'aizen-home-'));
try {
  installGlobalRules(false, fakeHome);
  for (const dir of [['.gemini', 'config', 'rules'], ['.claude', 'rules']]) {
    assert(fs.existsSync(path.join(fakeHome, ...dir, 'continuous-improvement.md')), `Thiếu rule trong ${dir.join('/')}`);
  }
  fs.writeFileSync(path.join(fakeHome, 'AGENTS.md'), '# Mine\n\nkeep me\n');
  updateAgentsMd([dbSkill], fakeHome, false);
  updateAgentsMd(skills, fakeHome, false);
  const md = fs.readFileSync(path.join(fakeHome, 'AGENTS.md'), 'utf8');
  assert.strictEqual(md.split('## Available Skills').length, 2, 'Sync lại không được nhân đôi mục skill');
  assert(md.includes('video-to-skill/SKILL.md'), 'Sync lại phải cập nhật danh sách skill');
  assert(md.includes('keep me') && md.includes('continuous-improvement.md'), 'AGENTS.md phải giữ nội dung cũ và trỏ tới rule');
  console.log('  ✓ Rules toàn cục + AGENTS.md: OK');
} finally {
  fs.rmSync(fakeHome, { recursive: true, force: true });
}

function skillsRoot() { return path.join(__dirname, '..', 'skills'); }

console.log('\n[TEST] 🎉 Toàn bộ automated tests đã VƯỢT QUA thành công!\n');

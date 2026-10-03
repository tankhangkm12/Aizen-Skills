'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { discoverSkills, createLink } = require('../bin/install');

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

console.log('\n[TEST] 🎉 Toàn bộ automated tests đã VƯỢT QUA thành công!\n');

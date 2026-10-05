#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const { runInstall, discoverSkills } = require('./install');
const { updateSkills, setupScheduler } = require('./updater');
const agentsConfig = require('./agents-config');
const external = require('./external');

const args = process.argv.slice(2);
const command = args[0] ? args[0].toLowerCase() : 'status';

function printHelp() {
  console.log(`
Aizen Skills CLI - Quản lý kỹ năng cho mọi AI Agent

SỬ DỤNG:
  aizen [lệnh] [tùy chọn]

CÁC LỆNH CHÍNH:
  install, sync       Tự động nhận diện và liên kết toàn bộ skills vào các AI Agent
                      Tùy chọn: --global (mặc định), --project
  update              Kiểm tra và cập nhật phiên bản mới nhất từ git / npm
  auto-update         Cấu hình tác vụ tự động cập nhật ngầm hàng ngày
                      Ví dụ: aizen auto-update enable  (hoặc disable)
  status              Hiển thị danh sách skills và trạng thái liên kết với các Agent
  external            Skill cộng đồng dùng trực tiếp, không chép (externals.json):
                      aizen external list | install <tên> | update <tên> | remove <tên>
  help, -h            Hiển thị trợ giúp này
`);
}

function showStatus() {
  console.log('\n==================================================');
  console.log('  🔍 AIZEN SKILLS - TRẠNG THÁI HỆ THỐNG');
  console.log('==================================================\n');

  const skills = discoverSkills();
  console.log(`[1] Kỹ năng có sẵn (${skills.length}):`);
  skills.forEach(s => {
    console.log(`  - 📦 ${s.id} (${s.name})`);
  });

  console.log('\n[2] Tình trạng liên kết với các AI Agent (Global):');
  agentsConfig.global.forEach(agent => {
    const exists = fs.existsSync(agent.targetDir);
    let linkedCount = 0;
    if (exists) {
      skills.forEach(s => {
        const dest = path.join(agent.targetDir, s.id);
        if (fs.existsSync(dest)) linkedCount++;
      });
    }
    const statusIcon = linkedCount === skills.length && linkedCount > 0 ? '✓' : linkedCount > 0 ? '⚠' : '✗';
    console.log(`  ${statusIcon} [${agent.name}]: ${linkedCount}/${skills.length} skills (${agent.targetDir})`);
  });

  console.log('\n[3] Skill cộng đồng (externals.json — dùng trực tiếp, không chép):');
  external.list();

  console.log('\n==================================================\n');
}

async function main() {
  switch (command) {
    case 'install':
    case 'sync':
      runInstall();
      break;

    case 'update':
      await updateSkills({ apply: true });
      break;

    case 'check':
      await updateSkills({ apply: false });
      break;

    case 'auto-update':
      const enable = args[1] !== 'disable';
      setupScheduler(enable);
      break;

    case 'status':
      showStatus();
      break;

    case 'external':
      process.exitCode = external.main(args.slice(1));
      break;

    case 'help':
    case '-h':
    case '--help':
      printHelp();
      break;

    default:
      console.warn(`Lệnh không hợp lệ: '${command}'`);
      printHelp();
      process.exit(1);
  }
}

main().catch(err => {
  console.error('[Aizen Skills] Lỗi:', err);
  process.exit(1);
});

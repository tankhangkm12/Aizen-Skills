#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const { runInstall, discoverSkills, runGuard, coreScripts } = require('./install');
const { updateSkills, setupScheduler } = require('./updater');
const agentsConfig = require('./agents-config');
const external = require('./external');

const rawArgs = process.argv.slice(2);

// Phân loại flags và positional arguments để hỗ trợ cờ đứng trước hoặc sau subcommand
const flags = new Set();
const positional = [];

for (const arg of rawArgs) {
  if (arg.startsWith('-')) {
    flags.add(arg);
  } else {
    positional.push(arg);
  }
}

// Xử lý các cờ toàn cục trợ giúp / phiên bản
if (flags.has('-h') || flags.has('--help') || (positional.length === 1 && (positional[0] === 'help' || positional[0] === '-h' || positional[0] === '--help'))) {
  printHelp();
  process.exit(0);
}

if (flags.has('-v') || flags.has('--version')) {
  try {
    const pkg = JSON.parse(fs.readFileSync(path.resolve(__dirname, '..', 'package.json'), 'utf8'));
    console.log(`v${pkg.version}`);
  } catch (e) {
    console.log('v2.2.0');
  }
  process.exit(0);
}

// Xác định subcommand đầu tiên (mặc định là 'status' nếu không truyền gì)
const command = positional[0] ? positional[0].toLowerCase() : 'status';

// Xác định các tham số con được chuyển tiếp cho subcommand (các tham số đứng sau tên command)
const cmdIndex = rawArgs.findIndex(a => a.toLowerCase() === command);
const forwardArgs = cmdIndex !== -1 ? rawArgs.slice(cmdIndex + 1) : rawArgs;

function printHelp() {
  console.log(`
Aizen Skills CLI - Quản lý kỹ năng cho mọi AI Agent

SỬ DỤNG:
  aizen [tùy chọn toàn cục] [lệnh] [tùy chọn của lệnh]

CÁC LỆNH CHÍNH:
  install, sync    Liên kết skills vào agent. Mặc định --project (dự án đang đứng);
                   --global để cài cho mọi dự án trên máy. Script Python chạy bằng uv.
  update           Kiểm tra và cập nhật phiên bản mới nhất từ git / npm
  check            Kiểm tra trạng thái cập nhật (không tự động tải về)
  test             Chạy bộ kiểm thử tự động toàn diện (tests/check-skills, scripts, installer)
  auto-update      Cấu hình tác vụ tự động cập nhật ngầm hàng ngày
                   Ví dụ: aizen auto-update enable  (hoặc disable)
  status           Hiển thị danh sách skills và trạng thái liên kết với các Agent
  guard            Hợp đồng chung cho mọi skill (hook Claude Code + Antigravity + pre-push):
                   aizen guard install            cài cho dự án hiện tại (sync --project tự làm)
                   aizen guard check --run <ID>   xem checklist của một run còn thiếu gì
                   aizen guard stop --run <ID> --reason "..."
  project          Biên soạn lại .aizen/PROJECT.md – bản đồ dự án (tự cập nhật sau mỗi thay đổi)
  backlog          Việc sắp làm: aizen backlog list | add --title "..." --skill <skill> | approve BL-nn | drop BL-nn
  external         Skill cộng đồng dùng trực tiếp, không chép (externals.json):
                   aizen external list | install <tên> | update <tên> | remove <tên>
  help, -h         Hiển thị trợ giúp này
  -v, --version    Hiển thị phiên bản
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
    const statusIcon = linkedCount === skills.length && linkedCount > 0 ? '✓' : linkedCount > 0 ? '⚠️' : '❌';
    console.log(`  ${statusIcon} [${agent.name}]: ${linkedCount}/${skills.length} skills (${agent.targetDir})`);
  });

  console.log('\n[3] Skill cộng đồng (externals.json – dùng trực tiếp, không chép):');
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

    case 'test': {
      const { spawnSync } = require('child_process');
      const testFiles = ['check-skills.js', 'check-scripts.js', 'test-installer.js', 'test-external.js'];
      let failed = 0;
      for (const t of testFiles) {
        const testPath = path.join(__dirname, '..', 'tests', t);
        if (fs.existsSync(testPath)) {
          const res = spawnSync(process.execPath, [testPath], { stdio: 'inherit' });
          if (res.status !== 0) {
            failed++;
            process.exitCode = res.status || 1;
            break;
          }
        }
      }
      if (failed === 0) {
        console.log('\n[TEST PASS] Toàn bộ test suite đã hoàn thành đạt chuẩn.\n');
      }
      break;
    }

    case 'auto-update': {
      const enable = forwardArgs[0] !== 'disable';
      setupScheduler(enable);
      break;
    }

    case 'status':
      showStatus();
      break;

    case 'guard':
      process.exitCode = runGuard(forwardArgs.length ? forwardArgs : ['--help']);
      break;

    case 'backlog':
      process.exitCode = runGuard(['backlog', ...forwardArgs]);
      break;

    case 'project':
      process.exitCode = runGuard(forwardArgs, {}, path.join(coreScripts, 'project.py'));
      break;

    case 'external':
      process.exitCode = external.main(forwardArgs);
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

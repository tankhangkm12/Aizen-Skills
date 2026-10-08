#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const { runInstall, discoverSkills, runGuard, coreScripts } = require('./install');
const { updateSkills, setupScheduler } = require('./updater');
const { discoverPlugins, getPlugin, validatePlugin, createPluginScaffold } = require('./plugins');
const external = require('./external');

const rawArgs = process.argv.slice(2);
const flags = new Set();
const positional = [];

for (const arg of rawArgs) {
  if (arg.startsWith('-')) flags.add(arg);
  else positional.push(arg);
}

if (flags.has('-h') || flags.has('--help') || (positional.length === 1 && positional[0] === 'help')) {
  printHelp();
  process.exit(0);
}

if (flags.has('-v') || flags.has('--version')) {
  try {
    const pkg = JSON.parse(fs.readFileSync(path.resolve(__dirname, '..', 'package.json'), 'utf8'));
    console.log(`v${pkg.version}`);
  } catch (e) {
    console.log('v3.0.0');
  }
  process.exit(0);
}

const command = positional[0] ? positional[0].toLowerCase() : 'status';
const cmdIndex = rawArgs.findIndex(a => a.toLowerCase() === command);
const forwardArgs = cmdIndex !== -1 ? rawArgs.slice(cmdIndex + 1) : rawArgs;

function printHelp() {
  console.log(`
Aizen Skills & Plugin Suite CLI - Tối ưu cho Dự án (Antigravity & Claude Code)

SỬ DỤNG:
  aizen [tùy chọn toàn cục] [lệnh] [tùy chọn của lệnh]

CÁC LỆNH CHÍNH:
  install, sync       Liên kết plugin và skills vào dự án hiện tại (Project-level isolated).
                      Tùy chọn: --plugin <tên> (design, code, learn, full)
  plugin              Quản lý và mở rộng hệ sinh thái Plugin:
                        aizen plugin list              Liệt kê các plugin có sẵn
                        aizen plugin create <tên>      Tạo plugin mới chuẩn OCP/SRP
                        aizen plugin validate <path>   Kiểm tra tính hợp lệ của plugin
  update              Kiểm tra và cập nhật phiên bản mới nhất từ git / npm
  check               Kiểm tra trạng thái cập nhật (không tự động tải về)
  test                Chạy toàn bộ bộ kiểm thử tự động (tests/check-skills, scripts, plugins)
  status              Hiển thị danh sách plugins, skills và tình trạng dự án
  guard               Hợp đồng kiểm soát chất lượng (hook Claude Code + Antigravity + pre-push):
                        aizen guard install            cài cho dự án hiện tại (sync tự làm)
                        aizen guard check --run <ID>   xem checklist của một run còn thiếu gì
  project             Biên soạn lại .aizen/PROJECT.md – bản đồ dự án
  backlog             Quản lý việc sắp làm: aizen backlog list | add | approve BL-nn
  external            Skill cộng đồng dùng trực tiếp (externals.json, vd: archify):
                        aizen external list | install <tên> | update <tên> | remove <tên>
  help, -h            Hiển thị trợ giúp này
  -v, --version       Hiển thị phiên bản
`);
}

function showStatus() {
  console.log('\n==================================================');
  console.log('  🔍 AIZEN PLUGIN SUITE - TRẠNG THÁI HỆ THỐNG');
  console.log('==================================================\n');

  const plugins = discoverPlugins();
  console.log(`[1] Các Plugin có sẵn (${plugins.length}):`);
  plugins.forEach(p => {
    console.log(`  - 🧩 [${p.id}] ${p.name}: ${p.description}`);
  });

  const skills = discoverSkills();
  console.log(`\n[2] Kỹ năng cốt lõi (${skills.length} skills):`);
  skills.forEach(s => {
    console.log(`  - 📦 ${s.id} (${s.name})`);
  });

  console.log('\n[3] Tình trạng liên kết dự án hiện tại:');
  const projectDir = process.cwd();
  const agySkills = path.join(projectDir, '.agents', 'skills');
  const claudeSkills = path.join(projectDir, '.claude', 'skills');
  console.log(`  - Antigravity: ${fs.existsSync(agySkills) ? '✓ Đã liên kết (' + agySkills + ')' : '❌ Chưa liên kết'}`);
  console.log(`  - Claude Code: ${fs.existsSync(claudeSkills) ? '✓ Đã liên kết (' + claudeSkills + ')' : '❌ Chưa liên kết'}`);

  console.log('\n[4] Skill cộng đồng (externals.json):');
  external.list();

  console.log('\n==================================================\n');
}

async function handlePluginCommand(args) {
  const sub = args[0] ? args[0].toLowerCase() : 'list';
  if (sub === 'list') {
    const list = discoverPlugins();
    console.log(`\nDanh sách Aizen Plugins (${list.length}):\n`);
    list.forEach(p => {
      console.log(`  🧩 ${p.id.padEnd(16)} | ${p.name.padEnd(26)} | Miền: ${p.domain}`);
      console.log(`     ${p.description}\n`);
    });
    return 0;
  }

  if (sub === 'create') {
    const name = args[1];
    if (!name) {
      console.error('Lỗi: Thiếu tên plugin. Cú pháp: aizen plugin create <tên-plugin> [--domain <domain>]');
      return 1;
    }
    const dIdx = args.indexOf('--domain');
    const domain = dIdx !== -1 && args[dIdx + 1] ? args[dIdx + 1] : 'custom';
    try {
      const res = createPluginScaffold(name, { domain });
      console.log(`\n✓ Đã tạo thành công bộ khung plugin mới tại: ${res.path}`);
      console.log(`  - Tệp manifest : ${path.join(res.path, 'plugin.json')}`);
      console.log(`  - Quy trình     : ${path.join(res.path, 'workflow.md')}`);
      console.log(`  - Thư mục agent: ${path.join(res.path, 'agents')}\n`);
      return 0;
    } catch (e) {
      console.error(`Lỗi: ${e.message}`);
      return 1;
    }
  }

  if (sub === 'validate') {
    const target = args[1] || '.';
    const res = validatePlugin(path.resolve(target));
    if (res.ok) {
      console.log(`\n✓ Plugin tại '${target}' hoàn toàn ĐẠT CHUẨN Aizen Plugin Standard!`);
      if (res.warnings.length) res.warnings.forEach(w => console.warn(`  ⚠️ Cảnh báo: ${w}`));
      return 0;
    } else {
      console.error(`\n❌ Plugin tại '${target}' KHÔNG đạt chuẩn:`);
      res.errors.forEach(e => console.error(`  ✗ ${e}`));
      return 1;
    }
  }

  console.warn(`Lệnh plugin không hợp lệ: '${sub}'. Dùng 'list', 'create', hoặc 'validate'.`);
  return 1;
}

async function main() {
  switch (command) {
    case 'install':
    case 'sync':
      runInstall();
      break;

    case 'plugin':
      process.exitCode = await handlePluginCommand(forwardArgs);
      break;

    case 'update':
      await updateSkills({ apply: true });
      break;

    case 'check':
      await updateSkills({ apply: false });
      break;

    case 'test': {
      const { spawnSync } = require('child_process');
      const testFiles = ['check-skills.js', 'check-scripts.js', 'test-installer.js', 'test-external.js', 'test-plugins.js'];
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
      if (failed === 0) console.log('\n[TEST PASS] Toàn bộ test suite Aizen Plugins đã VƯỢT QUA thành công.\n');
      break;
    }

    case 'auto-update':
      setupScheduler(forwardArgs[0] !== 'disable');
      break;

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

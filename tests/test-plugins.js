'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { discoverPlugins, getPlugin, validatePlugin, createPluginScaffold } = require('../bin/plugins');
const { runInstall } = require('../bin/install');

console.log('[TEST] Bắt đầu kiểm tra hệ thống Aizen Multi-Plugin Suite...\n');

// 1. Test Auto-discovery (OCP Principle)
console.log('[TEST 1] Kiểm tra cơ chế Auto-discovery của các Plugins...');
const plugins = discoverPlugins();
console.log(`  ✓ Tìm thấy ${plugins.length} plugins hợp lệ.`);
assert(plugins.length >= 4, 'Phải tìm thấy ít nhất 4 plugins cốt lõi (design, code, learn, full)');

const expectedPlugins = ['aizen-design', 'aizen-code', 'aizen-learn', 'aizen-full'];
for (const pid of expectedPlugins) {
  const p = getPlugin(pid);
  assert(p, `Phải tìm thấy plugin: ${pid}`);
  console.log(`  ✓ Plugin [${p.id}]: OK (${p.name})`);
}

// 2. Test Contract Validation (Aizen Plugin Specification Standard)
console.log('\n[TEST 2] Kiểm tra tính hợp lệ của từng Plugin theo chuẩn OCP / SRP...');
for (const p of plugins) {
  const res = validatePlugin(p.path);
  assert(res.ok, `Plugin ${p.id} không đạt chuẩn: ${res.errors.join('; ')}`);
  console.log(`  ✓ ${p.id}: Đạt chuẩn Contract (có workflow.md, agents/, mcp declarations)`);
}

// 3. Test Scaffolding Engine (Khởi tạo Plugin Mới tự động)
console.log('\n[TEST 3] Kiểm tra công cụ tạo Plugin mới (aizen plugin create)...');
const tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'aizen-plugin-test-'));
try {
  const customName = 'test-security';
  const created = createPluginScaffold(customName, {
    domain: 'security',
    description: 'Chuyên biệt kiểm tra lỗ hổng bảo mật và SAST.'
  });

  assert(fs.existsSync(path.join(created.path, 'plugin.json')), 'Phải tạo plugin.json');
  assert(fs.existsSync(path.join(created.path, 'workflow.md')), 'Phải tạo workflow.md');
  assert(fs.existsSync(path.join(created.path, 'mcp.template.json')), 'Phải tạo mcp.template.json');

  const valRes = validatePlugin(created.path);
  assert(valRes.ok, `Plugin mới tạo phải tự động đạt chuẩn: ${valRes.errors.join('; ')}`);
  console.log('  ✓ Scaffolding plugin mới tuân thủ 100% chuẩn SRP & OCP: OK');

  // Dọn dẹp plugin test
  fs.rmSync(created.path, { recursive: true, force: true });
} finally {
  fs.rmSync(tempRoot, { recursive: true, force: true });
}

// 4. Test Project-level Installation & Slash Commands Generation
console.log('\n[TEST 4] Kiểm tra cài đặt Plugin vào Dự án và sinh Slash Commands...');
const mockProjectDir = fs.mkdtempSync(path.join(os.tmpdir(), 'mock-project-'));
try {
  runInstall({ projectDir: mockProjectDir, plugin: 'design' });

  // Kiểm tra thư mục đích của Antigravity và Claude Code
  assert(fs.existsSync(path.join(mockProjectDir, '.agents', 'skills')), 'Phải sinh .agents/skills');
  assert(fs.existsSync(path.join(mockProjectDir, '.agents', 'skills.json')), 'Phải sinh .agents/skills.json cho Antigravity');
  const agyJson = JSON.parse(fs.readFileSync(path.join(mockProjectDir, '.agents', 'skills.json'), 'utf8'));
  assert(Array.isArray(agyJson.entries) && agyJson.entries.length > 0, '.agents/skills.json phải chứa entries');
  assert(fs.existsSync(path.join(mockProjectDir, '.claude', 'skills')), 'Phải sinh .claude/skills');
  assert(!fs.existsSync(path.join(mockProjectDir, '.cursor')), 'Tuyệt đối không sinh thư mục Cursor (.cursor)');

  // Kiểm tra cấu hình MCP
  const mcpFile = path.join(mockProjectDir, '.mcp.json');
  assert(fs.existsSync(mcpFile), 'Phải tự động sinh .mcp.json cho dự án');
  const mcpData = JSON.parse(fs.readFileSync(mcpFile, 'utf8'));
  assert(mcpData.mcpServers.sequentialthinking, 'Phải có sequentialthinking MCP');
  assert(mcpData.mcpServers.penpot, 'Plugin design phải có penpot MCP');

  // Kiểm tra sinh Slash Commands
  const slashCmd = path.join(mockProjectDir, '.claude', 'commands', 'aizen-skills:design.md');
  assert(fs.existsSync(slashCmd), 'Phải sinh file Slash Command: aizen-skills:design.md');
  console.log('  ✓ Cài đặt Project-level cô lập + .mcp.json + Slash Commands: OK');
} finally {
  fs.rmSync(mockProjectDir, { recursive: true, force: true });
}

console.log('\n[TEST] 🏊 Toàn bộ kiểm thử Aizen Plugins Suite đã VƯỢT QUA thành công!\n');

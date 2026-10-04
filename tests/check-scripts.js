'use strict';
// Smoke test cho script Python của các skill: self-check + --help + một lần chạy thật cho mỗi công cụ.
const { spawnSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const scripts = path.join(__dirname, '..', 'skills', 'cecilia-coding-skills', 'scripts');
const python = ['python3', 'python'].find(p => spawnSync(p, ['--version']).status === 0);
if (!python) {
  // Máy dev không có Python thì bỏ qua; CI thì bắt buộc.
  console[process.env.CI ? 'error' : 'warn']('[SCRIPTS] không tìm thấy python3/python');
  process.exit(process.env.CI ? 1 : 0);
}

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'cecilia-'));
const run = (args, expect = 0) => {
  const r = spawnSync(python, args, { cwd: tmp, encoding: 'utf8', env: { ...process.env, PYTHONIOENCODING: 'utf-8' } });
  return { ok: r.status === expect, status: r.status, out: (r.stdout || '') + (r.stderr || '') };
};
const S = name => path.join(scripts, name);
const cases = [
  ['state.py self-check', [S('state.py'), '--selfcheck']],
  ['skill-creator new_skill.py self-check', [path.join(__dirname, '..', 'skills', 'skill-creator', 'scripts', 'new_skill.py'), '--selfcheck']],
  ['tech-learning-tree check_tree.py self-check', [path.join(__dirname, '..', 'skills', 'tech-learning-tree', 'scripts', 'check_tree.py'), '--selfcheck']],
  ['tech-learning-tree to_notion.py self-check', [path.join(__dirname, '..', 'skills', 'tech-learning-tree', 'scripts', 'to_notion.py'), '--selfcheck']],
  ['skill-cloner fetch_skill.py self-check', [path.join(__dirname, '..', 'skills', 'skill-cloner', 'scripts', 'fetch_skill.py'), '--selfcheck']],
  ...['state.py', 'check.py', 'graph.py', 'capacity.py', 'uikit.py', 'apikit.py'].map(n => [`${n} --help`, [S(n), '--help']]),
  ['check.py --plan', [S('check.py'), '--task', 'T-1', '--plan']],
  ['graph.py outside git → exit 2', [S('graph.py'), '--project', '.', '--check'], 2],
  ['capacity contention', [S('capacity.py'), 'contention', '--rps-per-key', '0.1,5,200', '--window-ms', '50', '--retries', '2']],
  ['capacity forecast short horizon', [S('capacity.py'), 'forecast', '--users', '10,20,30', '--monthly-growth', '0.01,0.02,0.03',
    '--rows-per-user-month', '1,2,3', '--row-bytes', '100', '--index-bytes-per-row', '50', '--months', '3']],
  ['uikit contrast', [S('uikit.py'), 'contrast', '#1a1a1a', '#ffffff']],
  ['apikit journey', [S('apikit.py'), 'journey', '--calls', 'GET /cart > GET /products/{id} x3', '--latency-ms', '80']],
  ['apikit bad latency → exit 2', [S('apikit.py'), 'journey', '--calls', 'GET /a', '--latency-ms', '1,2'], 2],
];
let failed = 0;
for (const [label, args, expect] of cases) {
  const r = run(args, expect);
  if (!r.ok) {
    failed++;
    console.error(`  ✗ ${label} (exit ${r.status})\n${r.out.split('\n').slice(-8).join('\n')}`);
  }
}
fs.rmSync(tmp, { recursive: true, force: true });
if (failed) process.exit(1);
console.log(`[SCRIPTS] ${cases.length} kiểm tra script Python đều đạt (${python}).`);

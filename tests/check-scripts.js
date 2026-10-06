'use strict';
// Smoke test cho script Python của các skill: self-check + --help + một lần chạy thật cho mỗi công cụ.
const { spawnSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const skill = (...p) => path.join(__dirname, '..', 'skills', ...p);
// Script chạy đúng như người dùng chạy: `uv run --script` (header PEP 723, uv tự tải Python).
if (spawnSync('uv', ['--version']).status !== 0) {
  // Máy dev không có uv thì bỏ qua; CI thì bắt buộc.
  console[process.env.CI ? 'error' : 'warn']('[SCRIPTS] không tìm thấy uv');
  process.exit(process.env.CI ? 1 : 0);
}

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'aizen-'));
const run = (args, expect = 0) => {
  const r = spawnSync('uv', ['run', '--quiet', '--script', ...args], { cwd: tmp, encoding: 'utf8', env: { ...process.env, PYTHONIOENCODING: 'utf-8' } });
  return { ok: r.status === expect, status: r.status, out: (r.stdout || '') + (r.stderr || '') };
};
const S = {
  'state.py': skill('aizen-build', 'scripts', 'flow', 'state.py'),
  'guard.py': skill('aizen-core', 'scripts', 'core', 'guard.py'),
  'project.py': skill('aizen-core', 'scripts', 'core', 'project.py'),
  'check.py': skill('aizen-core', 'scripts', 'core', 'check.py'),
  'journal.py': skill('aizen-core', 'scripts', 'core', 'journal.py'),
  'graph.py': skill('aizen-core', 'scripts', 'core', 'graph.py'),
  'capacity.py': skill('aizen-core', 'scripts', 'core', 'capacity.py'),
  'uikit.py': skill('aizen-frontend', 'scripts', 'frontend', 'uikit.py'),
  'apikit.py': skill('aizen-backend', 'scripts', 'api-ux', 'apikit.py'),
};
const cases = [
  ['state.py self-check', [S['state.py'], '--selfcheck']],
  ['guard.py self-check', [S['guard.py'], '--selfcheck']],
  ['project.py self-check', [S['project.py'], '--selfcheck']],
  ['journal.py self-check', [S['journal.py'], '--selfcheck']],
  ['aizen-build guard shim → core', [skill('aizen-build', 'scripts', 'flow', 'guard.py'), 'hook', 'stop', '--agent', 'claude']],
  ['guard.py hook without .aizen → allow', [S['guard.py'], 'hook', 'stop', '--agent', 'claude']],
  ['feedback.py self-check', [skill('aizen-skill-creator', 'scripts', 'authoring', 'feedback.py'), '--selfcheck']],
  ['new_skill.py self-check', [skill('aizen-skill-creator', 'scripts', 'authoring', 'new_skill.py'), '--selfcheck']],
  ['fetch_skill.py self-check', [skill('aizen-skill-importer', 'scripts', 'fetch_skill.py'), '--selfcheck']],
  ['check_tree.py self-check', [skill('aizen-tech-learning', 'scripts', 'check_tree.py'), '--selfcheck']],
  ['to_notion.py self-check', [skill('aizen-tech-learning', 'scripts', 'to_notion.py'), '--selfcheck']],
  ...['gate.py', 'check_inputs.py'].map(n => [`aizen-init ${n} self-check`, [skill('aizen-init', 'scripts', n), '--selfcheck']]),
  ['pipeline_scaffold.py self-check', [skill('aizen-infra', 'scripts', 'infra', 'pipeline_scaffold.py'), '--selfcheck']],
  ...['connectivity.py', 'secrets_checklist.py'].map(n => [`${n} --help`, [skill('aizen-infra', 'scripts', 'infra', n), '--help']]),
  ['aggregate_benchmark.py --help', [skill('aizen-skill-eval', 'scripts', 'eval', 'aggregate_benchmark.py'), '--help']],
  ...Object.keys(S).map(n => [`${n} --help`, [S[n], '--help']]),
  ['check.py --plan', [S['check.py'], '--task', 'T-1', '--plan']],
  ['graph.py outside git → exit 2', [S['graph.py'], '--project', '.', '--check'], 2],
  ['capacity contention', [S['capacity.py'], 'contention', '--rps-per-key', '0.1,5,200', '--window-ms', '50', '--retries', '2']],
  ['capacity forecast short horizon', [S['capacity.py'], 'forecast', '--users', '10,20,30', '--monthly-growth', '0.01,0.02,0.03',
    '--rows-per-user-month', '1,2,3', '--row-bytes', '100', '--index-bytes-per-row', '50', '--months', '3']],
  ['uikit contrast', [S['uikit.py'], 'contrast', '#1a1a1a', '#ffffff']],
  ['apikit journey', [S['apikit.py'], 'journey', '--calls', 'GET /cart > GET /products/{id} x3', '--latency-ms', '80']],
  ['apikit bad latency → exit 2', [S['apikit.py'], 'journey', '--calls', 'GET /a', '--latency-ms', '1,2'], 2],
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
console.log(`[SCRIPTS] ${cases.length} kiểm tra script Python đều đạt (uv run --script).`);

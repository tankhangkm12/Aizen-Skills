'use strict';
// Community skills (externals.json): install → link → update shows new commits → remove → prune. Offline: a local git repo.
const assert = require('assert');
const { spawnSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'aizen-ext-'));
const git = (args, cwd) => {
  const r = spawnSync('git', args, { cwd, encoding: 'utf8' });
  assert.strictEqual(r.status, 0, `git ${args.join(' ')}: ${r.stderr}`);
  return r.stdout.trim();
};
const upstream = path.join(tmp, 'upstream');
fs.mkdirSync(path.join(upstream, 'tool'), { recursive: true });
fs.writeFileSync(path.join(upstream, 'tool', 'SKILL.md'), '---\nname: tool\ndescription: "Draws things. Use when drawing."\n---\n# Tool\n');
git(['init', '-q', '-b', 'main'], upstream);
git(['-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-q', '--allow-empty', '-m', 'init'], upstream);
git(['add', '.'], upstream);
git(['-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-q', '-m', 'v1'], upstream);

const decl = path.join(tmp, 'externals.json');
fs.writeFileSync(decl, JSON.stringify({ externals: [{ name: 'tool', repo: upstream, ref: 'main', skill_path: 'tool',
  license: 'MIT', needs: 'nothing', used_by: ['aizen-design'], why: 'test' }] }));
process.env.AIZEN_EXTERNALS_FILE = decl;
process.env.AIZEN_EXTERNAL_DIR = path.join(tmp, 'installed');
const ext = require('../bin/external');
const quiet = fn => { const log = console.log; const out = []; console.log = (...a) => out.push(a.join(' ')); try { return [fn(), out.join('\n')]; } finally { console.log = log; } };

console.log('[TEST] Skill cộng đồng (externals.json)...');
assert.strictEqual(quiet(() => ext.main(['install']))[0], 2, 'install không tên phải bị từ chối');
assert.strictEqual(quiet(() => ext.main(['install', 'tool']))[0], 0);
const [skill] = ext.installedExternals();
assert(skill && skill.id === 'tool' && skill.description.startsWith('Draws'), 'installedExternals phải thấy skill vừa cài');
console.log('  ✓ install + phát hiện');

fs.appendFileSync(path.join(upstream, 'tool', 'SKILL.md'), '\nNew rule.\n');
git(['-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-q', '-am', 'v2: new rule'], upstream);
const [code, out] = quiet(() => ext.main(['update', 'tool']));
assert.strictEqual(code, 0);
assert(out.includes('v2: new rule'), 'update phải liệt kê commit mới của upstream:\n' + out);
assert(fs.readFileSync(path.join(skill.path, 'SKILL.md'), 'utf8').includes('New rule.'), 'update phải lấy bản mới');
console.log('  ✓ update hiển thị commit mới rồi fast-forward');

const { installGlobal } = require('../bin/install');
const agentDir = path.join(tmp, 'agent-skills');
fs.mkdirSync(agentDir);
fs.symlinkSync(skill.path, path.join(agentDir, 'tool'), process.platform === 'win32' ? 'junction' : 'dir');
assert.strictEqual(quiet(() => ext.main(['remove', 'tool']))[0], 0);
const agentsConfig = require('../bin/agents-config');
const saved = agentsConfig.global;
agentsConfig.global = [{ id: 't', name: 't', targetDir: agentDir, type: 'skill-dir' }];
try { quiet(() => installGlobal([], false)); } finally { agentsConfig.global = saved; }
const gone = (() => { try { fs.lstatSync(path.join(agentDir, 'tool')); return false; } catch (e) { return true; } })();
assert(gone, 'link (kể cả link treo) tới skill đã gỡ phải bị dọn');
console.log('  ✓ remove + sync dọn link');

fs.rmSync(tmp, { recursive: true, force: true });
console.log('[TEST] externals OK');

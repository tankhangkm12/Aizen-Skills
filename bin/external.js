#!/usr/bin/env node
'use strict';
// Community skills that Aizen uses but never copies — they stay current with their upstream.
//
//   aizen external list                 # declared externals, installed or not, at which commit
//   aizen external install <name...>    # shallow clone into ~/.aizen/external/<name>, run its declared setup
//   aizen external update <name...>     # fetch, show the new upstream commits, fast-forward, re-run setup
//   aizen external remove <name...>     # delete the checkout (links are pruned on the next sync)
//
// Declared in externals.json. Nothing here runs on npm install, `sync` or auto-update: installing or updating
// third-party code is the owner's explicit action. `sync` only links what is already installed.
// AIZEN_EXTERNAL_DIR overrides the install root (tests, portable setups).
const { spawnSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const root = path.join(__dirname, '..');
const declPath = process.env.AIZEN_EXTERNALS_FILE || path.join(root, 'externals.json'); // override: tests
const externalRoot = () => process.env.AIZEN_EXTERNAL_DIR || path.join(os.homedir(), '.aizen', 'external');

function declared() {
  if (!fs.existsSync(declPath)) return [];
  return JSON.parse(fs.readFileSync(declPath, 'utf8')).externals || [];
}

function run(cmd, args, cwd, { quiet = false } = {}) {
  const r = spawnSync(cmd, args, { cwd, encoding: 'utf8', shell: process.platform === 'win32' && cmd === 'npm' });
  if (r.status !== 0) {
    throw new Error(`${cmd} ${args.join(' ')} failed${r.stderr ? ': ' + r.stderr.trim().split('\n').slice(-3).join(' ') : ''}`);
  }
  if (!quiet && r.stdout.trim()) console.log(r.stdout.trimEnd());
  return r.stdout.trim();
}

const checkoutDir = e => path.join(externalRoot(), e.name);
const skillDir = e => path.join(checkoutDir(e), e.skill_path || '.');

// Installed externals as skill entries for the installer (same shape as discoverSkills()).
function installedExternals() {
  const out = [];
  for (const e of declared()) {
    const dir = skillDir(e);
    const md = path.join(dir, 'SKILL.md');
    if (!fs.existsSync(md)) continue;
    const fm = (fs.readFileSync(md, 'utf8').match(/^---\n([\s\S]*?)\n---/) || [])[1] || '';
    const desc = ((fm.match(/^description:\s*(.*)$/m) || [])[1] || '').replace(/^["']|["']$/g, '');
    out.push({ id: path.basename(dir) === '.' ? e.name : path.basename(dir), name: e.name, description: desc, path: dir, external: true });
  }
  return out;
}

function setup(e) {
  if (!e.setup || !e.setup.length) return;
  const [cmd, ...args] = e.setup;
  console.log(`  · setup: ${e.setup.join(' ')}  (in ${skillDir(e)})`);
  run(cmd, args, skillDir(e), { quiet: true });
}

function install(e) {
  const dir = checkoutDir(e);
  if (fs.existsSync(path.join(dir, '.git'))) { console.log(`  = ${e.name} already installed — use \`update\``); return; }
  fs.mkdirSync(path.dirname(dir), { recursive: true });
  run('git', ['clone', '-q', '--depth', '1', '--branch', e.ref, e.repo, dir], root, { quiet: true });
  setup(e);
  const sha = run('git', ['rev-parse', '--short=12', 'HEAD'], dir, { quiet: true });
  console.log(`  ✓ ${e.name} @ ${sha} (${e.license}) → ${skillDir(e)}`);
}

function update(e) {
  const dir = checkoutDir(e);
  if (!fs.existsSync(path.join(dir, '.git'))) throw new Error(`${e.name} is not installed — use \`install\``);
  const before = run('git', ['rev-parse', 'HEAD'], dir, { quiet: true });
  run('git', ['fetch', '-q', '--depth', '50', 'origin', e.ref], dir, { quiet: true });
  const after = run('git', ['rev-parse', 'FETCH_HEAD'], dir, { quiet: true });
  if (before === after) { console.log(`  = ${e.name} is current (${before.slice(0, 12)})`); return; }
  let log = '';
  try { log = run('git', ['log', '--oneline', '--no-decorate', `${before}..${after}`], dir, { quiet: true }); } catch (_) { /* shallow gap */ }
  console.log(`  ${e.name}: ${before.slice(0, 12)} → ${after.slice(0, 12)}`);
  console.log((log || '  (history not deep enough to list — see the upstream changelog)').split('\n').map(l => '    ' + l).join('\n'));
  run('git', ['checkout', '-q', '--detach', after], dir, { quiet: true });
  setup(e);
  console.log(`  ✓ ${e.name} updated — review the commits above; re-run \`aizen sync\` if the skill folder moved`);
}

function remove(e) {
  fs.rmSync(checkoutDir(e), { recursive: true, force: true });
  console.log(`  ✓ ${e.name} removed (run \`aizen sync\` to prune its links)`);
}

function list() {
  for (const e of declared()) {
    const dir = checkoutDir(e);
    const sha = fs.existsSync(path.join(dir, '.git')) ? run('git', ['rev-parse', '--short=12', 'HEAD'], dir, { quiet: true }) : 'not installed';
    console.log(`${e.name.padEnd(16)} ${sha.padEnd(14)} ${e.license.padEnd(10)} ${e.repo}`);
    console.log(`${''.padEnd(16)} used by ${e.used_by.join(', ')} · needs ${e.needs}`);
  }
}

function main(argv) {
  const [cmd = 'list', ...names] = argv;
  if (cmd === 'list') { list(); return 0; }
  const map = { install, update, remove };
  if (!map[cmd]) { console.error('usage: aizen external list | install <name...> | update <name...> | remove <name...>'); return 2; }
  if (!names.length) { console.error(`${cmd} needs explicit names — third-party code is never installed or updated in bulk`); return 2; }
  const all = declared();
  let failed = 0;
  for (const n of names) {
    const e = all.find(x => x.name === n);
    if (!e) { console.error(`  ✗ ${n}: not declared in externals.json`); failed++; continue; }
    try { map[cmd](e); } catch (err) { console.error(`  ✗ ${n}: ${err.message}`); failed++; }
  }
  return failed ? 1 : 0;
}

if (require.main === module) process.exit(main(process.argv.slice(2)));
module.exports = { main, declared, installedExternals, externalRoot };

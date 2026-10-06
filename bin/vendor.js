#!/usr/bin/env node
'use strict';
// Vendored upstream knowledge — "stand on the shoulders of giants" without letting them move under your feet.
//
//   node bin/vendor.js list                 # what is vendored, from where, at which commit
//   node bin/vendor.js sync [name...]       # re-copy the pinned commits into the packs (idempotent)
//   node bin/vendor.js update <name...>     # move entries to the upstream branch head, re-copy; review `git diff`
//
// Reads vendor.lock.json. Files are copied verbatim; each destination gets UPSTREAM.md (source, commit, licence,
// what was kept and why) and the upstream LICENSE. Never runs upstream code. Needs git; network only for sync/update.
const { spawnSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const root = path.join(__dirname, '..');
const lockPath = path.join(root, 'vendor.lock.json');

const MIT = (holder, year) => `MIT License

Copyright (c) ${year} ${holder}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
`;

function git(args, cwd) {
  const r = spawnSync('git', args, { cwd, encoding: 'utf8', env: { ...process.env, GIT_LFS_SKIP_SMUDGE: '1' } });
  if (r.status !== 0) throw new Error(`git ${args.join(' ')} failed: ${(r.stderr || '').trim()}`);
  return r.stdout.trim();
}

// Shallow checkout of one commit (or the branch head when commit is empty).
function checkout(v) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), `aizen-vendor-${v.name}-`));
  git(['init', '-q'], dir);
  git(['remote', 'add', 'origin', v.repo], dir);
  git(['fetch', '-q', '--depth', '1', 'origin', v.commit || v.ref], dir);
  git(['checkout', '-q', 'FETCH_HEAD'], dir);
  return { dir, sha: git(['rev-parse', 'HEAD'], dir) };
}

const glob = p => new RegExp('^' + p.replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*') + '$');

function copyEntry(src, dest, spec) {
  if (!fs.existsSync(src)) throw new Error(`upstream path missing: ${spec.from}`);
  const skip = (spec.exclude || []).map(glob);
  const rename = spec.rename || {};
  if (fs.statSync(src).isFile()) {
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.copyFileSync(src, dest);
    return 1;
  }
  let n = 0;
  for (const e of fs.readdirSync(src, { withFileTypes: true })) {
    if (skip.some(re => re.test(e.name))) continue;
    const to = path.join(dest, rename[e.name] || e.name);
    n += e.isDirectory() ? copyEntry(path.join(src, e.name), to, { ...spec, exclude: [], rename }) : copyEntry(path.join(src, e.name), to, {});
  }
  return n;
}

function upstreamMd(v, sha) {
  return `# Upstream: ${v.name}

Vendored, unmodified, into Aizen. Do not edit these files — change \`vendor.lock.json\` and run
\`node bin/vendor.js sync ${v.name}\`; put Aizen's own view in the pack's guides instead.

| | |
|---|---|
| Source | ${v.repo} |
| Commit | \`${sha}\` (branch \`${v.ref}\`) |
| Licence | ${v.license} — see \`LICENSE\` in this folder |
| Copied | ${v.copy.map(c => `\`${c.from}\` → \`${c.to}\``).join('<br>')} |

${v.notes}

**Precedence:** this is how to do things right *in this tool*. Aizen core rules still decide how much to build and
who decides (\`references/core/workspace.md\` §3 in aizen-core): an upstream "ask the user first", "announce",
"install" or "deploy" step becomes a plan question or an A3 item, never an action on its own.
`;
}

function sync(v, { update = false } = {}) {
  const pin = update ? { ...v, commit: '' } : v;
  const { dir, sha } = checkout(pin);
  try {
    const dest = path.join(root, v.dest);
    fs.rmSync(dest, { recursive: true, force: true });
    let files = 0;
    for (const spec of v.copy) {
      const to = path.join(dest, spec.to);
      const src = path.join(dir, spec.from);
      if (fs.existsSync(src) && fs.statSync(src).isDirectory()) files += copyEntry(src, to, spec);
      else files += copyEntry(src, to, spec);
    }
    const lic = v.license_file && path.join(dir, v.license_file);
    if (lic && fs.existsSync(lic)) fs.copyFileSync(lic, path.join(dest, 'LICENSE'));
    else if (v.license === 'MIT' && v.license_holder) fs.writeFileSync(path.join(dest, 'LICENSE'), MIT(v.license_holder, new Date().getFullYear()));
    else throw new Error(`${v.name}: no licence file upstream and no way to state it — do not vendor without a licence`);
    fs.writeFileSync(path.join(dest, 'UPSTREAM.md'), upstreamMd(v, sha));
    v.commit = sha;
    console.log(`  ✓ ${v.name} @ ${sha.slice(0, 12)} → ${v.dest} (${files} files)`);
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

function main(argv) {
  const [cmd = 'list', ...names] = argv;
  const lock = JSON.parse(fs.readFileSync(lockPath, 'utf8'));
  const pick = names.length ? lock.vendors.filter(v => names.includes(v.name)) : lock.vendors;
  const unknown = names.filter(n => !lock.vendors.some(v => v.name === n));
  if (unknown.length) { console.error(`unknown vendor(s): ${unknown.join(', ')}`); return 2; }
  if (cmd === 'list') {
    for (const v of lock.vendors) console.log(`${v.name.padEnd(34)} ${(v.commit || '(not pinned)').slice(0, 12)}  ${v.license.padEnd(10)} ${v.repo}`);
    return 0;
  }
  if (cmd !== 'sync' && cmd !== 'update') { console.error('usage: vendor.js list | sync [name...] | update <name...>'); return 2; }
  if (cmd === 'update' && !names.length) { console.error('update needs explicit names — never move every upstream at once'); return 2; }
  let failed = 0;
  for (const v of pick) {
    try { sync(v, { update: cmd === 'update' || !v.commit }); } catch (e) { failed++; console.error(`  ✗ ${v.name}: ${e.message}`); }
  }
  fs.writeFileSync(lockPath, JSON.stringify(lock, null, 2) + '\n');
  return failed ? 1 : 0;
}

if (require.main === module) process.exit(main(process.argv.slice(2)));
module.exports = { main };

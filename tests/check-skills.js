'use strict';
// Lint cho skills/: đủ 8 thành phần, tên frontmatter khớp thư mục, không có ký tự điều khiển, manifest không còn placeholder.
const fs = require('fs');
const path = require('path');

const skillsDir = path.join(__dirname, '..', 'skills');
const errors = [];
const REQUIRED = ['SKILL.md', 'manifest.json', 'rules', 'agents', 'references', 'tools', 'scripts', 'assets'];

function walk(dir, out = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else out.push(p);
  }
  return out;
}

for (const id of fs.readdirSync(skillsDir)) {
  const dir = path.join(skillsDir, id);
  const skillMd = path.join(dir, 'SKILL.md');
  if (!fs.existsSync(skillMd)) continue;

  for (const part of REQUIRED) {
    if (!fs.existsSync(path.join(dir, part))) errors.push(`${id}: thiếu ${part} (Aizen Universal Structure)`);
  }

  const name = (fs.readFileSync(skillMd, 'utf8').match(/^name:\s*(.+?)\s*$/m) || [])[1];
  if (name !== id) errors.push(`${id}/SKILL.md: name "${name}" khác tên thư mục "${id}"`);

  const manifest = path.join(dir, 'manifest.json');
  if (fs.existsSync(manifest) && /\{\{\w+\}\}/.test(fs.readFileSync(manifest, 'utf8'))) {
    errors.push(`${id}/manifest.json: còn placeholder {{...}}`);
  }

  for (const f of walk(dir).filter(f => f.endsWith('.md'))) {
    if (/[\x00-\x08\x0b\x0c\x0e-\x1f]/.test(fs.readFileSync(f, 'utf8'))) {
      errors.push(`${path.relative(skillsDir, f)}: chứa ký tự điều khiển (escape hỏng?)`);
    }
  }
}

if (errors.length) {
  console.error(errors.map(e => '  ✗ ' + e).join('\n'));
  process.exit(1);
}
console.log('[CHECK] skills/ hợp lệ.');

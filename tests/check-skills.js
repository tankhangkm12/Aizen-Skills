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

  for (const f of walk(dir).filter(f => /\.(md|py)$/.test(f))) {
    const text = fs.readFileSync(f, 'utf8');
    const rel = path.relative(skillsDir, f);
    if (f.endsWith('.md') && /[\x00-\x08\x0b\x0c\x0e-\x1f]/.test(text)) {
      errors.push(`${rel}: chứa ký tự điều khiển (escape hỏng?)`);
    }
    // Đường dẫn `skills/<x>/...` tới skill không tồn tại (sót lại từ bố cục cũ).
    for (const [, other] of text.matchAll(/\bskills\/([a-z0-9-]+)\/(?:references|scripts|agents|assets)\//g)) {
      if (!fs.existsSync(path.join(skillsDir, other))) errors.push(`${rel}: trỏ tới skill không tồn tại "skills/${other}/"`);
    }
    // `references/...` trong backtick phải tồn tại trong skill.
    for (const [, ref] of text.matchAll(/`(references\/[A-Za-z0-9_./-]+\.md)`/g)) {
      if (!fs.existsSync(path.join(dir, ref))) errors.push(`${rel}: tham chiếu hỏng ${ref}`);
    }
  }
}

if (errors.length) {
  console.error(errors.map(e => '  ✗ ' + e).join('\n'));
  process.exit(1);
}
console.log('[CHECK] skills/ hợp lệ.');

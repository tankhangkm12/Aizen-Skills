'use strict';
// Lint cho skills/: đủ thành phần, tên frontmatter khớp thư mục, description ≤ 1024 ký tự, không có ký tự điều khiển,
// manifest không còn placeholder, mọi đường dẫn nội bộ trỏ tới file có thật (kể cả xuyên knowledge pack),
// version (vNN) khớp manifest, manifest name/version hợp lệ, skill dùng trực tiếp có README + docs, không còn tên role cũ.
const fs = require('fs');
const path = require('path');

const skillsDir = path.join(__dirname, '..', 'skills');
const errors = [];
const REQUIRED = ['SKILL.md', 'manifest.json', 'rules', 'agents', 'references', 'tools', 'scripts', 'assets'];
// Knowledge pack (manifest.partOf = skill chính): chỉ chứa kiến thức, không có role/script/asset riêng.
const PACK_REQUIRED = ['SKILL.md', 'manifest.json', 'references'];
const STALE = /\b(cecilia-(discovery|design|dev-be|dev-fe|ui|api-ux|plan|review|test)\b(?!-)|dev-be|dev-fe|feat-be\/|feat-fe\/|workflow\.py|cecilia_check\.py|Cecilia OS)/;

function walk(dir, out = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.name === 'graphify-out' || e.name === 'node_modules') continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else out.push(p);
  }
  return out;
}

function readJson(p) {
  try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch (e) { return null; }
}

const root = path.join(__dirname, '..');
const read = f => (fs.existsSync(path.join(root, f)) ? fs.readFileSync(path.join(root, f), 'utf8') : '');
const docs = { readme: read('README.md'), guide: read('docs/huong-dan-su-dung.md'), prompts: read('docs/prompt-mau.md') };
for (const [k, f] of [['readme', 'README.md'], ['guide', 'docs/huong-dan-su-dung.md'], ['prompts', 'docs/prompt-mau.md']]) {
  if (/[\x00-\x08\x0b\x0c\x0e-\x1f]/.test(docs[k])) errors.push(`${f}: chứa ký tự điều khiển (escape hỏng?)`);
}
const ids = fs.readdirSync(skillsDir).filter(id => fs.existsSync(path.join(skillsDir, id, 'SKILL.md')));
const manifests = Object.fromEntries(ids.map(id => [id, readJson(path.join(skillsDir, id, 'manifest.json')) || {}]));
// Gia đình skill: skill chính + các pack của nó. `references/<topic>/` có thể nằm ở bất kỳ thành viên nào;
// assets/scripts/agents/rules nằm ở skill chính.
const familyOf = id => {
  const root = manifests[id].partOf || id;
  return { root, members: [root, ...ids.filter(x => manifests[x].partOf === root)] };
};

for (const id of ids) {
  const dir = path.join(skillsDir, id);
  const manifest = manifests[id];
  const isPack = Boolean(manifest.partOf);
  const { root, members } = familyOf(id);

  if (isPack && !ids.includes(root)) errors.push(`${id}/manifest.json: partOf "${root}" không tồn tại`);
  for (const part of isPack ? PACK_REQUIRED : REQUIRED) {
    if (!fs.existsSync(path.join(dir, part))) errors.push(`${id}: thiếu ${part} (Aizen Universal Structure)`);
  }

  const skillText = fs.readFileSync(path.join(dir, 'SKILL.md'), 'utf8');
  const name = (skillText.match(/^name:\s*(.+?)\s*$/m) || [])[1];
  if (name !== id) errors.push(`${id}/SKILL.md: name "${name}" khác tên thư mục "${id}"`);
  const desc = (skillText.match(/^description:\s*(.+?)\s*$/m) || [])[1] || '';
  if (!desc) errors.push(`${id}/SKILL.md: thiếu description`);
  if (desc.length > 1024) errors.push(`${id}/SKILL.md: description ${desc.length} ký tự (> 1024)`);
  // YAML thuần không cho ": " hay " #" trong scalar không nháy → `npx skills add` bỏ qua skill vì không parse được.
  if (desc && !/^["'>|]/.test(desc) && /: | #/.test(desc)) errors.push(`${id}/SKILL.md: description chứa ": " hoặc " #" nhưng không đặt trong nháy (YAML lỗi, skills CLI sẽ bỏ qua skill)`);

  if (manifest.name !== id) errors.push(`${id}/manifest.json: name "${manifest.name}" khác tên thư mục`);
  if (!/^\d+\.\d+\.\d+$/.test(manifest.version || '')) errors.push(`${id}/manifest.json: version "${manifest.version}" không phải semver`);
  // Skill dùng trực tiếp phải có tài liệu cho người dùng (docs/aizen-skill-standard.md §7).
  if (!isPack) {
    if (!docs.readme.includes(`[\`${id}\`](skills/${id})`)) errors.push(`README.md: thiếu dòng [\`${id}\`](skills/${id}) trong bảng skill`);
    if (!docs.guide.includes(`\`${id}\``)) errors.push(`docs/huong-dan-su-dung.md: chưa nhắc tới \`${id}\``);
    if (!docs.prompts.includes(`/${id}`)) errors.push(`docs/prompt-mau.md: thiếu prompt mẫu /${id}`);
  }

  const manifestPath = path.join(dir, 'manifest.json');
  if (fs.existsSync(manifestPath) && /\{\{\w+\}\}/.test(fs.readFileSync(manifestPath, 'utf8'))) {
    errors.push(`${id}/manifest.json: còn placeholder {{...}}`);
  }
  // `(vNN)` trong tiêu đề/description phải khớp major version của manifest.
  const major = String(manifest.version || '').split('.')[0];

  for (const f of walk(dir).filter(f => /\.(md|py|json)$/.test(f))) {
    const text = fs.readFileSync(f, 'utf8');
    const rel = path.relative(skillsDir, f);
    if (f.endsWith('.md') && /[\x00-\x08\x0b\x0c\x0e-\x1f]/.test(text)) {
      errors.push(`${rel}: chứa ký tự điều khiển (escape hỏng?)`);
    }
    // Đường dẫn `skills/<x>/...` tới skill không tồn tại (sót lại từ bố cục cũ).
    for (const [, other] of text.matchAll(/\bskills\/([a-z0-9-]+)\/(?:references|scripts|agents|assets)\//g)) {
      if (!fs.existsSync(path.join(skillsDir, other))) errors.push(`${rel}: trỏ tới skill không tồn tại "skills/${other}/"`);
    }
    if (!f.endsWith('.md')) continue;
    // Mọi `references|assets|scripts|agents|rules/...` trong backtick phải tồn tại trong gia đình skill.
    for (const [, ref] of text.matchAll(/`((?:references|assets|scripts|agents|rules)\/[A-Za-z0-9_./-]+\.(?:md|py|json|ya?ml))`/g)) {
      const homes = ref.startsWith('references/') ? members : [root];
      if (!homes.some(m => fs.existsSync(path.join(skillsDir, m, ref)))) errors.push(`${rel}: tham chiếu hỏng ${ref}`);
    }
    // Link markdown tương đối `](x.md)` phải tồn tại.
    for (const [, link] of text.matchAll(/\]\(((?!https?:|#|mailto:)[^)\s#]+\.md)(?:#[^)]*)?\)/g)) {
      if (!fs.existsSync(path.resolve(path.dirname(f), link))) errors.push(`${rel}: link hỏng ${link}`);
    }
    if (members.length > 1 && STALE.test(text)) errors.push(`${rel}: còn tên cũ "${text.match(STALE)[0]}"`);
    const isSkillDoc = /^(SKILL\.md|agents[\\/]|rules[\\/])/.test(path.relative(dir, f));
    if (isSkillDoc && major && (/^#[^\n]*\(v(\d+)\)/m.test(text) || /^description:.*\(v(\d+)\)/m.test(text))) {
      const v = (text.match(/^#[^\n]*\(v(\d+)\)/m) || text.match(/^description:.*\(v(\d+)\)/m))[1];
      if (v !== major) errors.push(`${rel}: ghi (v${v}) nhưng manifest là ${manifest.version}`);
    }
  }
}

if (errors.length) {
  console.error(errors.map(e => '  ✗ ' + e).join('\n'));
  process.exit(1);
}
console.log('[CHECK] skills/ hợp lệ.');

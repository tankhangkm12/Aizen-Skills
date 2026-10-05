'use strict';
// Lint cho skills/ theo chuẩn Aizen (docs/aizen-skill-standard.md):
// - manifest: name khớp thư mục, semver, kind entry|pack, topics không trùng giữa các skill, requires tồn tại;
// - SKILL.md: name khớp, description ≤ 1024 ký tự, YAML hợp lệ, (vNN) khớp major của manifest;
// - mọi đường dẫn `references|assets|scripts/<topic>/…` resolve qua sổ topic (skill nào khai báo topic thì sở hữu nó),
//   `agents/` và `rules/` thuộc chính skill; link markdown tương đối phải tồn tại;
// - thư mục vendor/ (kiến thức chép từ upstream) phải có UPSTREAM.md + LICENSE;
// - skill entry phải có README + docs; không còn tên cũ.
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const skillsDir = path.join(root, 'skills');
const errors = [];
const STALE = /\b(cecilia|Cecilia|CECILIA|tensura|thanhtan|\.thanhtan|skill-cloner|agent-skill-tester|adversarial-code-reviewer|database-table-design|devsecops-pipeline-flow|tech-learning-tree)\b/;
const STALE_OK = /[\\/]vendor[\\/]/; // upstream text is kept verbatim

function walk(dir, out = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (['graphify-out', 'node_modules', '__pycache__'].includes(e.name)) continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else out.push(p);
  }
  return out;
}
const readJson = p => { try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch (e) { return null; } };
const read = f => (fs.existsSync(path.join(root, f)) ? fs.readFileSync(path.join(root, f), 'utf8') : '');
const docs = { readme: read('README.md'), guide: read('docs/huong-dan-su-dung.md'), prompts: read('docs/prompt-mau.md') };

const ids = fs.readdirSync(skillsDir).filter(id => fs.existsSync(path.join(skillsDir, id, 'SKILL.md')));
for (const id of fs.readdirSync(skillsDir)) {
  if (!ids.includes(id)) errors.push(`skills/${id}: không có SKILL.md (mọi thư mục trong skills/ đều bị cài như một skill)`);
}
const manifests = Object.fromEntries(ids.map(id => [id, readJson(path.join(skillsDir, id, 'manifest.json'))]));

// Sổ topic: topic → skill sở hữu (Open/Closed: thêm pack mới chỉ cần khai báo topics trong manifest).
const topicOwner = {};
for (const id of ids) {
  for (const t of (manifests[id] && manifests[id].topics) || []) {
    if (topicOwner[t]) errors.push(`${id}/manifest.json: topic "${t}" đã thuộc ${topicOwner[t]}`);
    else topicOwner[t] = id;
  }
}
const resolveRef = (id, ref) => {
  const [kind, topic] = ref.split('/');
  if (['references', 'assets', 'scripts'].includes(kind) && topicOwner[topic]) return topicOwner[topic];
  return id;
};

for (const id of ids) {
  const dir = path.join(skillsDir, id);
  const m = manifests[id];
  if (!m) { errors.push(`${id}: thiếu hoặc hỏng manifest.json`); continue; }
  if (m.name !== id) errors.push(`${id}/manifest.json: name "${m.name}" khác tên thư mục`);
  if (!/^\d+\.\d+\.\d+$/.test(m.version || '')) errors.push(`${id}/manifest.json: version "${m.version}" không phải semver`);
  if (!['entry', 'pack'].includes(m.kind)) errors.push(`${id}/manifest.json: kind phải là "entry" hoặc "pack"`);
  for (const r of m.requires || []) if (!ids.includes(r)) errors.push(`${id}/manifest.json: requires "${r}" không tồn tại`);
  for (const t of m.topics || []) {
    if (!['references', 'assets', 'scripts'].some(k => fs.existsSync(path.join(dir, k, t)))) {
      errors.push(`${id}/manifest.json: topic "${t}" không có references/${t}/, assets/${t}/ hay scripts/${t}/`);
    }
  }
  for (const k of ['references', 'assets', 'scripts']) {
    if (!fs.existsSync(path.join(dir, k)) || !(m.topics || []).length) continue;
    for (const sub of fs.readdirSync(path.join(dir, k), { withFileTypes: true })) {
      if (sub.isDirectory() && !(m.topics || []).includes(sub.name)) {
        errors.push(`${id}/${k}/${sub.name}/: skill có topics nên mọi thư mục con phải là một topic đã khai báo`);
      }
    }
  }

  const skillText = fs.readFileSync(path.join(dir, 'SKILL.md'), 'utf8');
  const name = (skillText.match(/^name:\s*(.+?)\s*$/m) || [])[1];
  if (name !== id) errors.push(`${id}/SKILL.md: name "${name}" khác tên thư mục "${id}"`);
  const desc = (skillText.match(/^description:\s*(.+?)\s*$/m) || [])[1] || '';
  if (!desc) errors.push(`${id}/SKILL.md: thiếu description`);
  if (desc.length > 1024) errors.push(`${id}/SKILL.md: description ${desc.length} ký tự (> 1024)`);
  if (desc && !/^["'>|]/.test(desc) && /: | #/.test(desc)) errors.push(`${id}/SKILL.md: description chứa ": " hoặc " #" nhưng không đặt trong nháy (YAML lỗi)`);
  if (m.kind === 'pack' && !/not a standalone skill/i.test(desc)) errors.push(`${id}/SKILL.md: pack phải ghi "not a standalone skill" trong description`);
  if (m.kind === 'entry' && !/Not for:/.test(desc)) errors.push(`${id}/SKILL.md: description của entry phải có "Not for:"`);
  if (m.kind === 'entry') {
    if (!docs.readme.includes(`[\`${id}\`](skills/${id})`)) errors.push(`README.md: thiếu dòng [\`${id}\`](skills/${id})`);
    if (!docs.guide.includes(`\`${id}\``)) errors.push(`docs/huong-dan-su-dung.md: chưa nhắc tới \`${id}\``);
    if (!docs.prompts.includes(`/${id}`)) errors.push(`docs/prompt-mau.md: thiếu prompt mẫu /${id}`);
  }
  const major = String(m.version || '').split('.')[0];

  for (const f of walk(dir)) {
    const rel = path.relative(skillsDir, f);
    const inVendor = STALE_OK.test(rel);
    if (path.basename(f) === 'SKILL.md' && path.dirname(f) !== dir) errors.push(`${rel}: SKILL.md lồng bên trong skill (installer sẽ nhầm) — đổi tên thành guide.md`);
    if (!/\.(md|py|json|js)$/.test(f)) continue;
    const text = fs.readFileSync(f, 'utf8');
    if (/[\x00-\x08\x0b\x0c\x0e-\x1f]/.test(text)) errors.push(`${rel}: chứa ký tự điều khiển`);
    if (!inVendor && STALE.test(text)) errors.push(`${rel}: còn tên cũ "${text.match(STALE)[0]}"`);
    if (!f.endsWith('.md')) continue;
    if (!inVendor) {
      for (const [, ref] of text.matchAll(/`((?:references|assets|scripts|agents|rules)\/[A-Za-z0-9_./-]+\.(?:md|py|json|ya?ml|sh))`/g)) {
        const owner = resolveRef(id, ref);
        if (!fs.existsSync(path.join(skillsDir, owner, ref))) errors.push(`${rel}: tham chiếu hỏng ${ref} (tìm trong ${owner})`);
      }
    }
    for (const [, link] of inVendor ? [] : text.matchAll(/\]\(((?!https?:|#|mailto:)[^)\s#]+\.md)(?:#[^)]*)?\)/g)) {
      if (!fs.existsSync(path.resolve(path.dirname(f), link))) errors.push(`${rel}: link hỏng ${link}`);
    }
    const isSkillDoc = /^(SKILL\.md|agents[\\/]|rules[\\/])/.test(path.relative(dir, f));
    const v = (text.match(/^#[^\n]*\(v(\d+)\)/m) || text.match(/^description:.*\(v(\d+)\)/m) || [])[1];
    if (isSkillDoc && v && v !== major) errors.push(`${rel}: ghi (v${v}) nhưng manifest là ${m.version}`);
  }

  // Kiến thức chép từ upstream: nguồn + giấy phép đi kèm (docs/aizen-skill-standard.md §6).
  const vendorDirs = [...new Set(walk(dir).map(f => path.relative(dir, f).split(path.sep))
    .filter(p => p.indexOf('vendor') > 0 && p.length > p.indexOf('vendor') + 2)
    .map(p => path.join(dir, ...p.slice(0, p.indexOf('vendor') + 2))))];
  for (const vdir of vendorDirs) {
    const vrel = path.relative(skillsDir, vdir);
    if (!fs.existsSync(path.join(vdir, 'UPSTREAM.md'))) errors.push(`${vrel}: thiếu UPSTREAM.md`);
    if (!fs.readdirSync(vdir).some(n => /^LICEN[CS]E/i.test(n))) errors.push(`${vrel}: thiếu LICENSE của upstream`);
  }
}

// vendor.lock.json khớp các thư mục vendor/ đang có.
const lock = readJson(path.join(root, 'vendor.lock.json')) || { vendors: [] };
for (const v of lock.vendors || []) {
  if (!fs.existsSync(path.join(root, v.dest))) errors.push(`vendor.lock.json: ${v.name} trỏ tới ${v.dest} không tồn tại`);
  if (!/^[0-9a-f]{40}$/.test(v.commit || '')) errors.push(`vendor.lock.json: ${v.name} thiếu commit SHA đầy đủ`);
}

const unique = [...new Set(errors)];
if (unique.length) {
  console.error(unique.map(e => '  ✗ ' + e).join('\n'));
  console.error(`[CHECK] ${unique.length} lỗi`);
  process.exit(1);
}
console.log(`[CHECK] skills/ hợp lệ (${ids.length} skill, ${Object.keys(topicOwner).length} topic).`);

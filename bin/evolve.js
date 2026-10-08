#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

function run(cmd, args, cwd) {
  const r = spawnSync(cmd, args, { cwd, encoding: 'utf8', shell: process.platform === 'win32' });
  if (r.status !== 0) {
    throw new Error(`${cmd} ${args.join(' ')} failed: ${r.stderr || r.stdout}`);
  }
  return r.stdout.trim();
}

function usage() {
  console.log(`
Aizen Evolution Engine

Usage:
  node bin/evolve.js propose <base_skill> <new_skill_name>
      (For AI Agent) Creates a proposal to evolve a skill. This stops execution and requires human approval.

  node bin/evolve.js approve <proposal_id>
      (For Human) Approves a proposal, forks the skill, creates a branch, and opens a PR.
`);
  process.exit(1);
}

const action = process.argv[2];
const baseSkill = process.argv[3];
const newSkill = process.argv[4];

const projectDir = process.cwd();
const proposalsDir = path.join(projectDir, '.aizen', 'proposals');

if (!fs.existsSync(proposalsDir)) {
  fs.mkdirSync(proposalsDir, { recursive: true });
}

if (action === 'propose') {
  if (!baseSkill || !newSkill) usage();
  
  const id = `evo-${Date.now()}`;
  const proposalPath = path.join(proposalsDir, `${id}.json`);
  
  const proposal = {
    id,
    baseSkill,
    newSkill,
    timestamp: new Date().toISOString(),
    status: 'pending'
  };
  
  fs.writeFileSync(proposalPath, JSON.stringify(proposal, null, 2), 'utf8');
  
  console.log(`\n[EVOLUTION GATEKEEPER] Đề xuất đã được ghi nhận.`);
  console.log(`Agent phải dừng lại tại đây.`);
  console.log(`Yêu cầu Human chạy lệnh sau để duyệt và cấp quyền tạo nhánh:`);
  console.log(`\n    node bin/evolve.js approve ${id}\n`);
  
  // AI MUST exit here
  process.exit(0);
} 
else if (action === 'approve') {
  const id = process.argv[3];
  if (!id) usage();
  
  // Check if run interactively by a human
  if (!process.stdout.isTTY) {
    console.error('Lệnh này chỉ được phép chạy bởi con người từ Terminal TTY.');
    process.exit(1);
  }
  
  const proposalPath = path.join(proposalsDir, `${id}.json`);
  if (!fs.existsSync(proposalPath)) {
    console.error(`Không tìm thấy đề xuất: ${id}`);
    process.exit(1);
  }
  
  const proposal = JSON.parse(fs.readFileSync(proposalPath, 'utf8'));
  if (proposal.status !== 'pending') {
    console.error(`Đề xuất này đã được xử lý.`);
    process.exit(1);
  }
  
  console.log(`[EVOLUTION] Đang duyệt đề xuất tiến hóa từ ${proposal.baseSkill} -> ${proposal.newSkill}...`);
  
  // Create Branch
  const branchName = `evolve/${proposal.newSkill}`;
  console.log(`  - Tạo nhánh: ${branchName}`);
  run('git', ['checkout', '-b', branchName], projectDir);
  
  // Fork logic placeholder: in reality we copy the skill folder.
  // For Aizen-Skills architecture, skills are in `.agents/skills/` via symlinks or copies.
  // To truly fork, we'd need to fork the source repo, but within a project context, 
  // we can create a local override skill in `.aizen/skills/` or similar.
  console.log(`  - Hệ thống đã mở nhánh an toàn.`);
  console.log(`  - Agent bây giờ có quyền thực thi thay đổi trên nhánh ${branchName}.`);
  console.log(`  - Sau khi xong, Agent có thể chạy 'gh pr create'.`);
  
  proposal.status = 'approved';
  fs.writeFileSync(proposalPath, JSON.stringify(proposal, null, 2), 'utf8');
  
  console.log(`\n[OK] Đã duyệt! Agent có thể tiếp tục công việc.`);
} else {
  usage();
}

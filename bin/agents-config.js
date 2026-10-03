'use strict';

const path = require('path');
const os = require('os');

const home = os.homedir();

module.exports = {
  // Cấu hình Toàn cục (Global Agent Directories)
  global: [
    {
      id: 'universal-agents',
      name: 'Universal Agent Skills (~/.agents/skills)',
      targetDir: path.join(home, '.agents', 'skills'),
      type: 'skill-dir'
    },
    {
      id: 'antigravity',
      name: 'Google Antigravity / Gemini CLI',
      targetDir: path.join(home, '.gemini', 'config', 'skills'),
      type: 'skill-dir'
    },
    {
      id: 'claude',
      name: 'Claude Code',
      targetDir: path.join(home, '.claude', 'skills'),
      type: 'skill-dir'
    },
    {
      id: 'cursor',
      name: 'Cursor (Global Skills)',
      targetDir: path.join(home, '.cursor', 'skills'),
      type: 'skill-dir'
    },
    {
      id: 'windsurf',
      name: 'Windsurf (Global Memories)',
      targetDir: path.join(home, '.codeium', 'windsurf', 'memories'),
      type: 'rules-dir'
    }
  ],

  // Cấu hình Cục bộ cho Project (Project-level Directories)
  project: [
    {
      id: 'antigravity-project',
      name: 'Antigravity / Universal Agent Directory',
      targetDir: (cwd) => path.join(cwd, '.agents', 'skills'),
      type: 'skill-dir'
    },
    {
      id: 'cursor-project',
      name: 'Cursor Project Rules',
      targetDir: (cwd) => path.join(cwd, '.cursor', 'rules'),
      type: 'cursor-mdc'
    },
    {
      id: 'claude-project',
      name: 'Claude Project Skills',
      targetDir: (cwd) => path.join(cwd, '.claude', 'skills'),
      type: 'skill-dir'
    }
  ]
};

'use strict';

const { execSync, spawnSync } = require('child_process');
const https = require('https');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { runInstall } = require('./install');

const isWindows = process.platform === 'win32';
const packageJsonPath = path.resolve(__dirname, '..', 'package.json');
const pkg = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));

// Kiểm tra phiên bản mới từ npm registry
function getLatestNpmVersion(packageName, timeoutMs = 3000) {
  return new Promise((resolve) => {
    const url = `https://registry.npmjs.org/${packageName}/latest`;
    const req = https.get(url, { headers: { 'User-Agent': 'aizen-skills-updater' } }, (res) => {
      if (res.statusCode !== 200) {
        resolve(null);
        return;
      }
      let raw = '';
      res.on('data', chunk => { raw += chunk; });
      res.on('end', () => {
        try {
          const json = JSON.parse(raw);
          resolve(json.version);
        } catch (e) {
          resolve(null);
        }
      });
    });

    req.on('error', () => resolve(null));
    req.setTimeout(timeoutMs, () => {
      req.destroy();
      resolve(null);
    });
  });
}

// Kiểm tra git remote nếu là git repository
function checkGitUpdate() {
  try {
    const isGit = fs.existsSync(path.resolve(__dirname, '..', '.git'));
    if (!isGit) return null;

    // Phải chạy trong thư mục repo; --dry-run không cập nhật ref nên trước đây không bao giờ thấy "behind".
    const cwd = path.resolve(__dirname, '..');
    execSync('git fetch --quiet', { cwd, stdio: 'ignore', timeout: 15000 });
    const behind = execSync('git rev-list --count HEAD..@{u}', { cwd, encoding: 'utf8', timeout: 3000 });
    return parseInt(behind, 10) > 0 ? 'behind' : 'up-to-date';
  } catch (e) {
    return null;
  }
}

// Thực hiện cập nhật
async function updateSkills(options = {}) {
  console.log(`[Aizen Skills] Đang kiểm tra cập nhật (Phiên bản hiện tại: v${pkg.version})...`);

  // 1. Kiểm tra Git repo nếu người dùng đang dùng git clone
  const gitStatus = checkGitUpdate();
  if (gitStatus === 'behind') {
    console.log('  ➜ Phát hiện có bản cập nhật mới trên Git remote. Đang kéo mã nguồn mới...');
    try {
      execSync('git pull --rebase', { stdio: 'inherit', cwd: path.resolve(__dirname, '..') });
      console.log('  ✓ Đã cập nhật mã nguồn thành công.');
      runInstall();
      return;
    } catch (err) {
      console.error('  ! Lỗi khi git pull:', err.message);
    }
  }

  // 2. Kiểm tra NPM Registry
  const latestVer = await getLatestNpmVersion(pkg.name);
  if (latestVer && latestVer !== pkg.version) {
    console.log(`  ➜ Có phiên bản mới trên NPM: v${latestVer} (hiện tại: v${pkg.version})`);
    if (options.apply) {
      console.log('  ➜ Đang tiến hành cập nhật qua npm update...');
      try {
        execSync(`npm update -g ${pkg.name}`, { stdio: 'inherit' });
        console.log('  ✓ Đã cập nhật gói thành công.');
        runInstall();
      } catch (e) {
        console.warn(`  ! Hãy chạy thủ công: npm update -g ${pkg.name}`);
      }
    } else {
      console.log(`  💡 Bạn có thể cập nhật bằng cách chạy: npm update -g ${pkg.name} hoặc: aizen update`);
    }
  } else {
    console.log('  ✓ Bạn đang ở phiên bản mới nhất! Các AI Agent luôn được đồng bộ qua Live-Sync.');
  }
}

// Cấu hình tác vụ chạy ngầm tự động cập nhật
function setupScheduler(enable = true) {
  if (isWindows) {
    const taskName = 'AizenSkillsAutoUpdate';
    if (enable) {
      console.log(`[Auto-Update] Đang đăng ký Scheduled Task trên Windows: ${taskName}...`);
      try {
        const cliPath = path.resolve(__dirname, 'cli.js');
        const cmd = `schtasks /Create /SC DAILY /TN "${taskName}" /TR "node \\"${cliPath}\\" update" /F /ST 09:00`;
        execSync(cmd, { stdio: 'inherit' });
        console.log(`  ✓ Đã kích hoạt tự động cập nhật hàng ngày vào lúc 09:00 sáng.`);
      } catch (err) {
        console.warn(`  ! Không thể đăng ký Scheduled Task (có thể cần quyền Administrator):`, err.message);
      }
    } else {
      console.log(`[Auto-Update] Đang hủy đăng ký Scheduled Task: ${taskName}...`);
      try {
        execSync(`schtasks /Delete /TN "${taskName}" /F`, { stdio: 'inherit' });
        console.log(`  ✓ Đã hủy lịch tự động cập nhật.`);
      } catch (err) {
        console.warn(`  ! Lỗi khi xóa Scheduled Task:`, err.message);
      }
    }
  } else {
    // Linux / macOS: Hỗ trợ tự động cấu hình crontab
    try {
      const cliPath = path.resolve(__dirname, 'cli.js');
      const nodePath = process.execPath;
      const cronComment = '# aizen-skills-autoupdate';
      const cronLine = `0 9 * * * "${nodePath}" "${cliPath}" update >/dev/null 2>&1 ${cronComment}`;
      
      let currentCrontab = '';
      try {
        currentCrontab = execSync('crontab -l', { encoding: 'utf8', stdio: ['pipe', 'pipe', 'ignore'] });
      } catch (e) {}

      if (enable) {
        if (!currentCrontab.includes(cronComment)) {
          const newCrontab = currentCrontab ? `${currentCrontab.trim()}\n${cronLine}\n` : `${cronLine}\n`;
          execSync('crontab -', { input: newCrontab, stdio: ['pipe', 'pipe', 'inherit'] });
          console.log('  ✓ Đã tự động thêm lịch cập nhật vào crontab (hàng ngày lúc 09:00).');
        } else {
          console.log('  ✓ Lịch cập nhật đã tồn tại trong crontab.');
        }
      } else {
        if (currentCrontab.includes(cronComment)) {
          const filtered = currentCrontab
            .split('\n')
            .filter(line => !line.includes(cronComment))
            .join('\n');
          execSync('crontab -', { input: filtered.trim() ? `${filtered.trim()}\n` : '', stdio: ['pipe', 'pipe', 'inherit'] });
          console.log('  ✓ Đã xóa lịch cập nhật khỏi crontab.');
        } else {
          console.log('  ✓ Không tìm thấy tác vụ aizen trong crontab.');
        }
      }
    } catch (err) {
      console.log('[Auto-Update] Trên macOS/Linux, bạn có thể tự cấu hình trong crontab (`crontab -e`):');
      console.log(`0 9 * * * "${process.execPath}" "${path.resolve(__dirname, 'cli.js')}" update >/dev/null 2>&1`);
    }
  }
}

module.exports = {
  updateSkills,
  setupScheduler
};

'use strict';

const fs = require('fs');
const path = require('path');

const rootDir = path.resolve(__dirname, '..');
const pluginsDir = path.join(rootDir, 'plugins');

/**
 * Quét và phát hiện toàn bộ plugins có sẵn trong thư mục 'plugins/'
 * Tuân thủ Open/Closed Principle (OCP): tự động nhận diện không cần sửa core engine.
 */
function discoverPlugins() {
  if (!fs.existsSync(pluginsDir)) return [];
  const entries = fs.readdirSync(pluginsDir, { withFileTypes: true });
  const plugins = [];

  for (const entry of entries) {
    if (entry.isDirectory() && !entry.name.startsWith('.')) {
      const pluginPath = path.join(pluginsDir, entry.name);
      const manifestPath = path.join(pluginPath, 'plugin.json');
      if (fs.existsSync(manifestPath)) {
        try {
          const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
          plugins.push({
            id: manifest.id || entry.name,
            name: manifest.name || entry.name,
            description: manifest.description || '',
            domain: manifest.domain || 'custom',
            version: manifest.version || '1.0.0',
            path: pluginPath,
            manifest
          });
        } catch (err) {
          console.warn(`  ! [Plugin] Không thể đọc manifest của plugin ${entry.name}: ${err.message}`);
        }
      }
    }
  }

  return plugins;
}

/**
 * Lấy thông tin một plugin cụ thể theo ID hoặc tên
 */
function getPlugin(pluginId) {
  const all = discoverPlugins();
  const normalized = pluginId.toLowerCase().replace(/^aizen-/, '');
  return all.find(p => p.id.toLowerCase() === pluginId.toLowerCase()
    || p.id.toLowerCase().replace(/^aizen-/, '') === normalized);
}

/**
 * Kiểm tra tính hợp lệ của Plugin dựa trên Aizen Plugin Specification Standard (SRP / OCP)
 */
function validatePlugin(pluginPath) {
  const errors = [];
  const warnings = [];

  const manifestPath = path.join(pluginPath, 'plugin.json');
  if (!fs.existsSync(manifestPath)) {
    return { ok: false, errors: ['Thiếu tệp manifest bắt buộc: plugin.json'], warnings };
  }

  let manifest;
  try {
    manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  } catch (e) {
    return { ok: false, errors: [`plugin.json không hợp lệ định dạng JSON: ${e.message}`], warnings };
  }

  // 1. Kiểm tra các trường metadata bắt buộc
  for (const field of ['id', 'name', 'version', 'description', 'workflow']) {
    if (!manifest[field]) {
      errors.push(`Manifest thiếu trường bắt buộc: '${field}'`);
    }
  }

  // 2. Kiểm tra file workflow.md
  if (manifest.workflow) {
    const workflowPath = path.resolve(pluginPath, manifest.workflow);
    if (!fs.existsSync(workflowPath)) {
      errors.push(`Không tìm thấy tệp workflow tại: ${manifest.workflow}`);
    }
  }

  // 3. Kiểm tra danh sách chuyên gia (agents/) theo nguyên tắc SRP
  if (!manifest.agents || !Array.isArray(manifest.agents) || manifest.agents.length === 0) {
    errors.push('Plugin phải khai báo ít nhất một chuyên gia trong trường "agents"');
  } else {
    for (const ag of manifest.agents) {
      if (!ag.id || !ag.name || !ag.responsibility || !ag.file) {
        errors.push(`Agent '${ag.id || 'unnamed'}' thiếu các trường bắt buộc (id, name, responsibility, file)`);
      } else {
        const agentFile = path.resolve(pluginPath, ag.file);
        if (!fs.existsSync(agentFile)) {
          errors.push(`Không tìm thấy tệp prompt của Agent '${ag.id}' tại: ${ag.file}`);
        }
      }
    }
  }

  // 4. Kiểm tra cấu hình MCP bắt buộc
  if (!manifest.mcp || !Array.isArray(manifest.mcp.required)) {
    warnings.push('Plugin chưa khai báo trường "mcp.required". Nên có ít nhất sequentialthinking & context7.');
  } else {
    if (!manifest.mcp.required.includes('sequentialthinking')) {
      warnings.push('Khuyến nghị: Mọi plugin nên khai báo "sequentialthinking" trong mcp.required.');
    }
  }

  return {
    ok: errors.length === 0,
    errors,
    warnings
  };
}

/**
 * Tự động khởi tạo bộ khung mẫu cho một Plugin mới (Scaffolding Tool)
 */
function createPluginScaffold(pluginName, options = {}) {
  const normalizedId = pluginName.toLowerCase().startsWith('aizen-')
    ? pluginName.toLowerCase()
    : `aizen-${pluginName.toLowerCase()}`;
  const targetDir = path.join(pluginsDir, normalizedId);

  if (fs.existsSync(targetDir)) {
    throw new Error(`Plugin '${normalizedId}' đã tồn tại tại ${targetDir}`);
  }

  fs.mkdirSync(targetDir, { recursive: true });
  fs.mkdirSync(path.join(targetDir, 'agents'), { recursive: true });
  fs.mkdirSync(path.join(targetDir, 'skills'), { recursive: true });

  const domain = options.domain || 'custom';

  // 1. Tạo plugin.json
  const manifest = {
    id: normalizedId,
    name: options.name || pluginName,
    version: '1.0.0',
    description: options.description || `Aizen Plugin chuyên biệt cho miền ${domain} theo chuẩn SRP.`,
    domain: domain,
    workflow: './workflow.md',
    skills: [],
    agents: [
      {
        id: `${domain}-lead`,
        name: `Lead Specialist (${domain})`,
        responsibility: `Điều phối và kiểm soát chất lượng các tác vụ thuộc miền ${domain}`,
        file: `./agents/${domain}-lead.md`,
        tools: ['mcp:sequentialthinking', 'mcp:context7']
      }
    ],
    mcp: {
      required: ['sequentialthinking', 'context7'],
      optional: []
    }
  };
  fs.writeFileSync(path.join(targetDir, 'plugin.json'), JSON.stringify(manifest, null, 2), 'utf8');

  // 2. Tạo workflow.md
  const workflowContent = `# Chu Trình Làm Việc Cho Plugin ${manifest.name} (Workflow)

## 1. Mục tiêu duy nhất (Single Responsibility)
${manifest.description}

## 2. Quy trình từng bước (Step-by-step Execution)
1. **Bước 1 - Phân tích & Lập kế hoạch:** Phân rã bài toán thành các micro-modules (1-3 files/module).
2. **Bước 2 - Thực thi chuyên môn:** Chuyên gia đảm nhận đúng vai trò, sử dụng MCP tương ứng.
3. **Bước 3 - Nghiệm thu & Bằng chứng:** Tự động kiểm thử và tạo bằng chứng xác thực.
`;
  fs.writeFileSync(path.join(targetDir, 'workflow.md'), workflowContent, 'utf8');

  // 3. Tạo agent mẫu
  const agentContent = `# Role: Lead Specialist (${domain})

## Trách nhiệm cốt lõi (Single Responsibility)
Đảm nhận đúng vai trò điều phối kỹ thuật và giải quyết các bài toán trong miền ${domain}.

## Bảng phân quyền
| Quyền Hạn | Mô Tả |
|---|---|
| **Free (Tự do)** | Đọc tài liệu, phân tích mã nguồn, lập kế hoạch chi tiết. |
| **A3 (Cần hỏi)** | Thay đổi kiến trúc lớn, xóa dữ liệu, gọi API tốn phí. |
| **Never (Cấm)** | Tự ý sửa file ngoài phạm vi nhiệm vụ hoặc bỏ qua test. |

## Công cụ sử dụng
- MCP: \`sequentialthinking\`, \`context7\`
`;
  fs.writeFileSync(path.join(targetDir, 'agents', `${domain}-lead.md`), agentContent, 'utf8');

  // 4. Tạo mcp.template.json
  const mcpTemplate = {
    mcpServers: {
      sequentialthinking: {
        command: "npx",
        args: ["-y", "@modelcontextprotocol/server-sequential-thinking"]
      },
      context7: {
        command: "npx",
        args: ["-y", "@upstash/context7-mcp"]
      }
    }
  };
  fs.writeFileSync(path.join(targetDir, 'mcp.template.json'), JSON.stringify(mcpTemplate, null, 2), 'utf8');

  // 5. Tạo README.md
  fs.writeFileSync(path.join(targetDir, 'README.md'), `# ${manifest.name}\n\n${manifest.description}\n`, 'utf8');

  return { id: normalizedId, path: targetDir };
}

module.exports = {
  pluginsDir,
  discoverPlugins,
  getPlugin,
  validatePlugin,
  createPluginScaffold
};

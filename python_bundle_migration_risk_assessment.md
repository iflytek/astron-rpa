# Python 迁移至 .app Bundle 风险评估

## 背景

当前架构：Python 解释器位于用户目录 `~/Library/Application Support/astron-rpa/python_core/`，导致 macOS TCC 权限无法正常授权（辅助功能、屏幕录制、完全磁盘访问）。

拟改方案：将 Python 解释器迁移至 `.app/Contents/Resources/python_core/`，使其成为 app bundle 的一部分，从而继承 app 的 TCC 权限。

---

## 当前架构分析

### 目录结构
```
/Applications/astron-rpa.app/Contents/Resources/
  ├── python_core.7z              # 779MB 压缩包
  ├── python_core.7z.sha256.txt
  └── conf.yaml

~/Library/Application Support/astron-rpa/
  ├── python_core/                # 首次启动时从 .7z 解压到这里
  │   ├── bin/python3             # 真实解释器（Mach-O 可执行文件）
  │   └── lib/python3.13/site-packages/  # 590 个包（776MB）
  └── venvs/
      └── {project_id}/venv/
          └── bin/python3 -> ~/Library/.../python_core/bin/python3  # symlink
```

### 启动流程
1. Electron 主进程检查 `~/Library/.../python_core/` 是否存在
2. 不存在则从 `Resources/python_core.7z` 解压到用户目录
3. 启动命令：`"${pythonExe}" -m astronverse.scheduler --conf="${confPath}"`
4. `pythonExe` = `~/Library/.../python_core/bin/python3`

### 依赖管理
- **基础依赖**：590 个包打包在 `python_core/lib/site-packages/`（包括 pyobjc、PyQt5、fastapi 等）
- **项目依赖**：用户项目的 venv 在 `~/Library/.../venvs/{project_id}/venv/`，通过 symlink 指向 `python_core/bin/python3`
- **动态安装**：用户可通过前端界面安装额外的 Python 包到项目 venv

---

## 迁移方案

### 目标架构
```
/Applications/astron-rpa.app/Contents/Resources/
  ├── python_core/                # 不再是 .7z，直接内置
  │   ├── bin/python3             # TCC 认这个路径
  │   └── lib/python3.13/site-packages/  # 590 个包
  └── conf.yaml

~/Library/Application Support/astron-rpa/
  └── venvs/
      └── {project_id}/venv/
          └── bin/python3 -> /Applications/astron-rpa.app/.../python_core/bin/python3
```

### 核心改动

#### 1. `path.ts` 修改
```typescript
// 现在
export const pythonCore = path.join(appWorkPath, 'python_core')

// 改为
export const pythonCore = app.isPackaged
  ? path.join(resourcePath, 'python_core')  // bundle 内
  : path.join(appPath, 'data/python_core')  // 开发时保持不变
```

#### 2. 打包配置修改
- `electron-builder-config.js`：移除 `python_core.7z` 的复制逻辑
- 直接将 `python_core/` 目录打包进 `Resources/`
- 移除首次启动时的 7z 解压逻辑（`server.ts` 中的 `extract7z` 相关代码）

#### 3. venv 创建逻辑调整
- 确保 venv 的 symlink 指向 bundle 内的 Python：
  ```bash
  /Applications/astron-rpa.app/.../python_core/bin/python3 -m venv ~/Library/.../venvs/{project_id}/venv
  ```

---

## 风险评估

### 🔴 高风险

#### 1. **App 体积暴增**
- **现状**：`.7z` 压缩后约 200-300MB（压缩率 ~60%）
- **迁移后**：`python_core/` 未压缩 779MB 直接打包进 `.app`
- **影响**：
  - `.dmg` 安装包体积增加 500MB+
  - 用户下载时间显著增加（网络慢的用户体验极差）
  - App Store 分发受限（Apple 对大体积 app 有限制）
- **缓解方案**：
  - 使用 `asar` 打包 `python_core/`（Electron 原生支持，压缩率 ~30%）
  - 或保留 `.7z` 但首次解压到 bundle 内的临时目录（需要 root 权限，不可行）

#### 2. **App 只读导致 Python 无法自更新**
- **现状**：用户目录可写，可以通过前端触发 Python 解释器升级（如 3.13 → 3.14）
- **迁移后**：`/Applications/xxx.app` 是只读的，普通用户无法修改
- **影响**：
  - Python 版本锁死在打包时的版本
  - 安全补丁、bug 修复需要重新发布整个 app
  - 无法支持"在线升级 Python 解释器"功能
- **缓解方案**：
  - 放弃 Python 解释器的独立升级能力，只能随 app 整体更新
  - 或采用混合方案（见下文"中风险 #3"）

#### 3. **代码签名复杂度增加**
- **现状**：`python_core.7z` 是静态资源，签名简单
- **迁移后**：779MB 的二进制文件（包括 590 个 `.so`、`.dylib`）需要逐个签名
- **影响**：
  - 打包时间显著增加（每个 `.so` 都要 `codesign`）
  - 签名失败风险增加（某些第三方包的二进制可能签名不兼容）
  - 公证（notarization）时间增加
- **缓解方案**：
  - 在 CI/CD 中预先签名 `python_core/`，缓存签名结果
  - 使用 `--deep` 签名选项，但可能遇到第三方库的签名冲突

---

### 🟡 中风险

#### 1. **首次启动速度变慢**
- **现状**：首次启动需解压 `.7z`（~10-20 秒），后续启动秒开
- **迁移后**：无需解压，但 macOS 首次运行时会验证 bundle 内所有签名（779MB）
- **影响**：
  - 首次启动可能需要 30-60 秒（macOS Gatekeeper 验证）
  - 用户可能误以为 app 卡死
- **缓解方案**：
  - 在启动画面显示"正在验证应用安全性，请稍候..."
  - 使用 `asar` 打包可减少文件数量，加快验证速度

#### 2. **开发调试流程变化**
- **现状**：开发时 `python_core` 在 `data/` 目录，可以随时修改、测试
- **迁移后**：打包后的 `python_core` 在 bundle 内，调试需要重新打包
- **影响**：
  - 调试 Python 相关问题时，无法直接修改 bundle 内的文件
  - 需要维护两套路径逻辑（开发时 vs 打包后）
- **缓解方案**：
  - 保持开发时 `python_core` 在 `data/` 目录不变
  - 在 `path.ts` 中用 `app.isPackaged` 区分

#### 3. **混合方案的复杂性**
- **方案**：解释器在 bundle 内，site-packages 在用户目录
  ```
  .app/Resources/python_core/bin/python3  # 解释器（TCC 认）
  ~/Library/.../python_core/lib/site-packages/  # 包（可更新）
  ```
- **风险**：
  - Python 的 `sys.path` 需要手动配置指向用户目录
  - 解释器版本与包版本不匹配时可能崩溃（如 Python 3.13 + 3.12 编译的 `.so`）
  - 增加维护成本
- **优势**：
  - 解释器不可变（TCC 权限稳定）
  - 包可更新（保留灵活性）

---

### 🟢 低风险

#### 1. **venv 路径变化**
- **影响**：现有项目的 venv symlink 指向旧路径，需要重建
- **缓解方案**：
  - 首次启动检测旧 venv，自动重建 symlink
  - 或在迁移时清空 `~/Library/.../venvs/`，强制重建

#### 2. **权限检测逻辑调整**
- **影响**：`darwin_env_check()` 当前在 Python 侧检测，迁移后仍在 Python 侧，但 Python 在 bundle 内
- **缓解方案**：
  - 迁移后权限检测应该能正常工作（Python 在 bundle 内，TCC 认可）
  - 需要实际测试验证

#### 3. **跨版本升级兼容性**
- **影响**：用户从旧版本（Python 在用户目录）升级到新版本（Python 在 bundle 内）
- **缓解方案**：
  - 升级时检测旧 `python_core/` 存在，提示用户可以删除（释放 779MB 空间）
  - 或自动清理旧目录

---

## 对比：影刀的方案

### 影刀的架构
```
/Applications/影刀.app/Contents/Resources/app/node_modules/xbot-engine/lib/
  └── python310/
      ├── bin/python3.10
      └── lib/python3.10/site-packages/  # 101 个包，全部静态打包
```

### 关键差异
| 维度 | 影刀 | astron-rpa（现状） | astron-rpa（迁移后） |
|------|------|-------------------|---------------------|
| Python 位置 | bundle 内 | 用户目录 | bundle 内 |
| 包数量 | 101 个（静态） | 590 个（静态） | 590 个（静态） |
| 动态安装包 | ❌ 不支持 | ✅ 支持（venv） | ✅ 支持（venv） |
| 解释器更新 | ❌ 随 app 更新 | ✅ 可独立更新 | ❌ 随 app 更新 |
| TCC 权限 | ✅ 正常 | ❌ 失败 | ✅ 正常 |
| App 体积 | ~200MB | ~300MB | ~800MB |

---

## 推荐方案

### 方案 A：完全迁移（推荐）
- **做法**：Python + 所有包打包进 bundle，使用 `asar` 压缩
- **优势**：
  - TCC 权限彻底解决 ✅
  - 架构简单，维护成本低 ✅
- **劣势**：
  - App 体积增加 ~500MB
  - Python 解释器无法独立更新
- **适用场景**：用户对 app 体积不敏感，更看重稳定性

### 方案 B：混合方案
- **做法**：解释器在 bundle 内，site-packages 在用户目录
- **优势**：
  - TCC 权限解决 ✅
  - 包可独立更新 ✅
  - App 体积增加较小（~50MB）
- **劣势**：
  - 实现复杂度高
  - 版本兼容性风险
- **适用场景**：需要频繁更新 Python 包，且用户对 app 体积敏感

### 方案 C：权限检测移至 Electron（备选）
- **做法**：Python 保持在用户目录，权限检测用 Electron 的 `systemPreferences` API
- **优势**：
  - 无需改动 Python 位置
  - App 体积不变
- **劣势**：
  - **Python 自动化仍然无权限**（检测通过 ≠ Python 能用）
  - 治标不治本
- **适用场景**：仅用于展示权限状态，实际自动化功能可能仍失败

---

## 实施建议

1. **短期（1-2 周）**：
   - 实施方案 C，让前端权限弹窗能正常显示
   - 同时在测试环境验证方案 A 的可行性

2. **中期（1 个月）**：
   - 完整实施方案 A，发布 beta 版本
   - 收集用户反馈（app 体积、启动速度）

3. **长期（3 个月）**：
   - 如果用户对体积敏感，考虑方案 B
   - 或优化 Python 包体积（移除不必要的依赖）

---

## 结论

**推荐方案 A（完全迁移）**，理由：
1. TCC 权限问题是阻塞性 bug，必须解决
2. 影刀已验证此方案可行
3. 体积增加可通过 `asar` 压缩缓解（预计最终增加 300-400MB）
4. Python 解释器更新频率低，随 app 更新可接受

**不推荐方案 C**，因为它无法解决 Python 自动化的实际权限问题。

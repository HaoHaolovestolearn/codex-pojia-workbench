<div align="center">

# Codex 破甲工作台 · Codex Pojia Workbench

**Codex / codex破甲 / DeepSeek破甲：让任务说明、接口配置和排错准备更清楚。**

面向开发者的开源本地工作台 · Python 标准库 · 无运行依赖 · 中文界面

[![CI](https://github.com/HaoHaolovestolearn/codex-pojia-workbench/actions/workflows/ci.yml/badge.svg)](https://github.com/HaoHaolovestolearn/codex-pojia-workbench/actions)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)
![License](https://img.shields.io/badge/license-MIT-176651)

**[💬 Telegram 社群](https://t.me/HaoNB_6666) · [🌐 NB破甲官网](https://nbpojia.lol) · [📘 Codex 教程](https://nbpojia.lol/tutorials/armor) · [🛠 联系管理员](https://t.me/HaoNB_666) · [📦 Releases](https://github.com/HaoHaolovestolearn/codex-pojia-workbench/releases)**

</div>

## 这是什么？

Codex Pojia Workbench（NB Codex破甲工作台）把开发前经常重复的准备工作集中到一个本地页面：选模板写清任务、生成 API 调用示例、检查基础配置、估算 Token 费用、查找常见错误的排查方向。

如果你通过 **codex、codex破甲、破甲、DeepSeek破甲、Codex教程、Codex工具箱** 找到这里，可以先运行工作台，再根据自己的技术栈生成任务说明和请求示例。欢迎进入 [Telegram 社群](https://t.me/HaoNB_6666) 交流使用经验。

这里的“破甲”是 NB 品牌及社区搜索关键词。项目提供实际的开发辅助功能，不实现模型安全限制绕过，也不承诺模型解除限制。项目与 OpenAI、DeepSeek 官方无关联。

## 为什么单独做这个项目？

[NB Codex Hub](https://github.com/HaoHaolovestolearn/NB-Codex-Hub) 是桌面配置与连接诊断工具。本项目专注**任务组织、调用代码生成和离线排错资料**，界面运行在本地浏览器，两者功能互补。

| 能力 | 本项目做什么 | 边界 |
| --- | --- | --- |
| 任务模板 | 12 个场景，目标与上下文组合，复制或导出 Markdown | 模板不会自动执行任务 |
| 请求构建器 | 生成 Python、curl、PowerShell、JavaScript 示例 | 不发送模型请求，不验证模型是否存在 |
| 接口选择 | Responses 与 Chat Completions 两种格式 | 服务方是否支持需查对应文档 |
| 配置检查 | 规范 Base URL、模型 ID、接口类型 | 不读写 Codex CLI 配置 |
| 本地保存 | 浏览器保存 3 个非敏感配置字段 | 无 API Key 输入栏 |
| 费用估算 | 手动输入 Token、单价和次数，用 Decimal 计算 | 非实时官方价格，不含缓存、税费和汇率 |
| 错误排查 | 400 / 401 / 403 / 404 / 408 / 429 / 5xx / TLS | 是排查指南，不是在线故障检测 |
| 社区入口 | 官网、Codex教程、Telegram 社群及管理员 | 第三方服务规则以相应页面为准 |

## 快速开始

要求 **Python 3.10+**，运行程序不需要 `pip install`。

```bash
git clone https://github.com/HaoHaolovestolearn/codex-pojia-workbench.git
cd codex-pojia-workbench
python workbench.py
```

程序默认打开 `http://127.0.0.1:8765`，按 `Ctrl+C` 停止。macOS / Linux 也可用 `python3` 替换 `python`。

已有 8765 端口占用时：

```bash
python workbench.py --port 8766
```

只启动服务，不自动打开浏览器：

```bash
python workbench.py --no-browser
```

### Windows EXE

如果 [Releases](https://github.com/HaoHaolovestolearn/codex-pojia-workbench/releases) 中已有构建完成的版本，可以下载 `Codex-Pojia-Workbench-Windows-x64.exe` 双击启动。EXE 会保留一个控制台窗口显示地址，并打开默认浏览器；关闭控制台后服务停止。

EXE 由标签发布工作流构建；创建仓库或提交源码本身不会立即产生可执行文件。使用 `SHA256SUMS.txt` 核对下载文件。文件未做商业代码签名。

## 1. 用模板组织 Codex 任务

1. 打开「任务模板」。
2. 搜索或选择任务场景。
3. 填写目标，例如“修复登录成功后导航栏仍显示未登录”。
4. 填写上下文：框架、错误、现有文件、验收条件与不能改动的模块。
5. 生成后复制到你的编程助手，或导出 `codex-task.md`。

### 内置 12 个场景

| 场景 | 重点 |
| --- | --- |
| Bug 修复 | 最小复现、根因、最小改动、回归验证 |
| 新功能开发 | 验收条件、输入输出、兼容性 |
| 代码审查 | 触发条件、具体影响、证据 |
| 测试补充 | 业务不变量、边界、失败路径 |
| Python API | 参数校验、错误处理、脱敏示例 |
| 前端体验 | 响应式、状态、键盘与焦点 |
| 安全重构 | 外部行为保持、逐步验证 |
| 性能优化 | 基线测量、热点、前后对比 |
| README 文档 | 真实功能、安装运行、限制 |
| 数据清洗 | 保留原数据、质量摘要、异常输入 |
| 自动构建 | 平台、权限、产物、版本触发 |
| 项目接续 | 当前状态、决策、证据、下一步 |

见 [任务示例](examples/task-example.md) 与 [模板编写说明](docs/PROMPTS.md)。

## 2. 生成可读的 API 调用示例

1. 打开「请求构建器」。
2. 选 OpenAI、DeepSeek 示例地址，或填自定义服务商地址。
3. 填入**你实际拥有权限的模型 ID**；默认名称只是占位符。
4. 根据服务商文档选 Responses 或 Chat Completions。
5. 生成后切换 Python、curl、PowerShell、JavaScript 查看示例。

工作台**没有密钥输入栏**。复制的代码会在你执行时读取 `API_KEY` 环境变量。

```bash
# Bash / zsh，示例值请替换；不要提交到仓库。
export API_KEY='replace-with-your-own-key'
```

```powershell
# Windows PowerShell
$env:API_KEY = 'replace-with-your-own-key'
```

curl 示例面向 Bash / zsh；Windows 建议选 PowerShell。JavaScript 示例要求 Node.js 18+。生成的 Python 示例只使用标准库，执行请求仍可能产生服务方费用。

### Base URL 与接口端点

| Base URL | 接口选择 | 最终端点 |
| --- | --- | --- |
| `https://example.com/v1` | Responses | `https://example.com/v1/responses` |
| `https://example.com/v1` | Chat Completions | `https://example.com/v1/chat/completions` |
| `https://api.deepseek.com` | Chat Completions | `https://api.deepseek.com/chat/completions` |
| `http://localhost:1234/v1` | Responses | `http://localhost:1234/v1/responses` |

地址会拒绝内嵌用户名、密码、查询参数、URL 片段、空白字符和远程明文 HTTP。不要把完整的 `/responses`、`/chat/completions` 或 `/models` 端点当作 Base URL。

### 配置保存

仅将 `base`、`model`、`protocol` 存到当前浏览器的 `nb.workbench.profile.v1`。更换端口、浏览器或无痕窗口后，保存内容可能不同。导出的 `codex-provider.json` 是**本工具的通用配置示例**，不是可以直接覆盖的 Codex CLI 配置文件。

## 3. 费用估算

手动填写单价、每次输入输出 Token 和请求次数。公式：

```text
每次费用 = (输入 Token × 输入单价 + 输出 Token × 输出单价) / 1,000,000
总费用 = 每次费用 × 请求次数
```

例如输入 2000、输出 1000、输入单价 1、输出单价 2、请求 100 次，结果为 `0.40000000`。价格单位由你选择，两种价格必须使用同一货币。**这些初始数字只是算式示例。**

## 4. 常见错误与排查

| 状态 | 建议 |
| --- | --- |
| 400 | 核对 JSON、model、接口类型、`input` / `messages` |
| 401 | 检查密钥所属服务方、环境变量和认证格式 |
| 403 | 检查账号、模型及分组权限 |
| 404 | 核对 Base URL 与最终接口路径 |
| 408 / 超时 | 检查网络、代理、超时参数及服务端状态 |
| 429 | 区分速率、额度、余额，遵守有限退避与 Retry-After |
| 5xx | 保留脱敏请求 ID，查看上游状态，避免无上限重试 |
| TLS | 检查系统时间、证书和代理，不关闭证书验证 |

更多见 [排错文档](docs/TROUBLESHOOTING.md)。

## 测试、构建与发布

```bash
python -m unittest discover -s tests -v
python -m compileall -q workbench.py
```

仓库包含覆盖请求格式、特殊字符、URL 校验、配置字段、费用计算、任务模板和本地 HTTP 边界的测试。请以当前 Actions 页面显示的实际运行结果为准。

- `main` 分支及 Pull Request：在 Windows / macOS / Linux 运行测试。
- 推送 `v*` 标签：测试通过后构建 Windows x64 EXE、源码 ZIP 和 SHA256，创建对应 Release。
- 发布使用该仓库的临时 `GITHUB_TOKEN`，无需额外个人 Token。
- 支持 `workflow_dispatch` 手动运行测试；版本发布要求 `v*` 标签。

详细说明见 [开发文档](docs/DEVELOPMENT.md)。

## 文件导航

| 路径 | 内容 |
| --- | --- |
| `workbench.py` | 本地 HTTP 服务、配置校验和生成逻辑 |
| `catalog.json` | 12 个任务模板及 8 类排错资料 |
| `web/` | 界面、样式、浏览器交互 |
| `tests/` | 单元与 HTTP 集成测试 |
| `examples/` | 示例任务和通用配置 |
| `docs/` | 开发、模板、排错和发布说明 |
| `.github/workflows/ci.yml` | 跨平台测试及标签版本构建 |
| `package_release.py` | 源码打包与 SHA256 生成 |

## 社区与相关项目

- **Telegram 社群：** [t.me/HaoNB_6666](https://t.me/HaoNB_6666)
- **管理员：** [t.me/HaoNB_666](https://t.me/HaoNB_666)
- **NB破甲官网：** [nbpojia.lol](https://nbpojia.lol)
- **Codex 教程：** [使用教程](https://nbpojia.lol/tutorials/armor)
- **API 教程：** [接口教程](https://nbpojia.lol/tutorials/api)
- **桌面连接诊断：** [NB Codex Hub](https://github.com/HaoHaolovestolearn/NB-Codex-Hub)

欢迎报告可复现 Bug 和改进建议。请写明系统、Python 版本、复现步骤和脱敏错误，勿附上密钥或个人敏感信息。

## 隐私与限制

默认仅监听 `127.0.0.1`，无外部 JavaScript / CSS / 字体依赖，无遥测。页面输入会发到你本机的 Python 服务处理；工作台不向模型 API 发送请求。外部官网和 TG 链接只有你点击后才会打开。复制生成的 API 示例并自行执行后，会向你指定的服务方发送请求。

本工具没有多用户认证，不应直接暴露到公网。任务文本不会主动保存到本地存储，但导出的文件、剪贴板和浏览器可能保留数据。不要在任务输入中放密钥。

## 官方接口参考

- [OpenAI Responses API](https://developers.openai.com/api/reference/resources/responses/methods/create)
- [DeepSeek Chat Completions API](https://api-docs.deepseek.com/api/create-chat-completion/)
- [GitHub Actions Python 测试](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)

## English

Codex Pojia Workbench is a local developer toolkit for Codex workflows and OpenAI-compatible API preparation. It includes 12 task recipes, request examples in four languages, profile validation, manual cost estimation and troubleshooting guides. It runs on Python's standard library and does not call model APIs. “Codex破甲”, “DeepSeek破甲” and “破甲” are NB brand/community search terms, not a claim of model safety bypass capability.

## License

[MIT](LICENSE)。NB 品牌名称及第三方站点内容不因此授予商标或内容授权。

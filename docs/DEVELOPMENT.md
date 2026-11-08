# 开发与构建

## 架构

Python 标准库 `ThreadingHTTPServer` 仅监听 IPv4 loopback。静态资源通过固定映射提供，`POST /api/*` 处理本地生成操作，不代理外部网络请求。

| 接口 | 请求 | 响应 |
| --- | --- | --- |
| GET /api/catalog | 无 | 模板与排错资料 |
| POST /api/prompt | recipe / goal / context | prompt |
| POST /api/validate | base / model / protocol | 规范化且只含三个字段的配置 |
| POST /api/generate | 配置 + prompt | endpoint / payload / snippets |
| POST /api/estimate | input_tokens / output_tokens / input_price / output_price / requests | per_request / total / note |

POST 要求 JSON、对象结构，限制 64 KiB。本地 Host / Origin 校验帮助减少跨站访问。没有 CORS 放行，也没有多用户认证。它不是公网部署服务器。

## 运行测试

```bash
python -m unittest discover -s tests -v
python -m compileall -q workbench.py package_release.py
```

生成的 Python 示例也会进行语法解析；测试不连接真实 API，也不消耗模型额度。浏览器 UI 验证应覆盖模板生成、四种代码切换、保存/重置、估算、筛选、复制及移动布局。

## 本地打包 Windows

在 Windows 环境安装构建依赖后：

```powershell
python -m pip install "pyinstaller>=6.10,<7"
python -m PyInstaller --noconfirm --clean --onefile --name Codex-Pojia-Workbench --add-data "web:web" --add-data "catalog.json:." workbench.py
python package_release.py
```

EXE 与源码 ZIP 放在 `dist/`，校验和由打包脚本生成。macOS / Linux 推荐直接运行源码，不能用 Linux 上的 PyInstaller 交叉构建 Windows EXE。

## 发布

通过测试后，创建并推送 `v1.0.0` 等版本标签。CI 在三个系统上运行测试，再在 Windows 构建，最后使用临时仓库 Token 创建 Release 并上传附件。不要在 PR 中运行拥有写权限的发布任务。

版本号修改涉及 `workbench.py`、`catalog.json`、界面版本和发布文档，提交前保持一致。构建产物不应提交到源码分支。

## 可选浏览器自动化

安装 Node.js 后执行 `npm install` 与 `npx playwright install chromium`，先启动本地工作台，再执行 `npm run test:ui`。该检查覆盖任务生成、代码切换、配置保存、费用计算、错误筛选及移动端横向溢出；截图输出在 `dist/ui/`。这些仅是开发依赖，不影响 Python 标准库运行方式。

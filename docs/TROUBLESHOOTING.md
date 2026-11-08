# 运行与 API 排错

## 程序打不开

先用 `python --version` 确认 Python 3.10+。在终端进入含 `workbench.py` 的目录运行。双击源码后窗口立刻关闭时，终端会帮助你看到错误。

## 8765 端口占用

使用 `python workbench.py --port 8766`，打开终端显示的新地址。不要盲目结束其他程序。

## 页面资源加载失败

确认 Python 服务仍在运行，浏览器地址使用 `http://127.0.0.1:端口`；不要直接双击 `web/index.html`。页面需要本机 API 来生成内容。

## 存储或复制失败

无痕模式、浏览器权限或策略可能限制 localStorage / clipboard。可手动复制输出。配置只属于当前 origin；换端口后不会自动继承。

## 模型调用失败

工作台生成代码，不会测试真实密钥或实际模型。核对服务商文档、账号权限、模型 ID、认证格式和最终端点。Responses 使用 `input`，Chat Completions 使用 `messages`；同一服务未必都支持。

导出的 `codex-provider.json` 不是 Codex CLI 的 `config.toml`，不要覆盖已有客户端配置。需接入 Codex 时，阅读客户端与服务商的当前教程。

## 如何反馈

提供：系统、Python 版本、页面功能、输入的脱敏示例、期望行为、实际行为。涉及请求失败时提供状态码和脱敏请求 ID。隐藏 API Key、账号与业务数据。

[Telegram 社群](https://t.me/HaoNB_6666) · [管理员](https://t.me/HaoNB_666)

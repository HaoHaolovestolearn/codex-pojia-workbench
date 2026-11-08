"""Codex Pojia Workbench: local, dependency-free developer utilities."""

import argparse
from decimal import Decimal, InvalidOperation
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shlex
import sys
from urllib.parse import urlsplit
import webbrowser

VERSION = '1.0.0'
ROOT = Path(__file__).resolve().parent
COMMUNITY = {'telegram': 'https://t.me/HaoNB_6666', 'admin': 'https://t.me/HaoNB_666',
             'website': 'https://nbpojia.lol'}


def text(value, label, limit=16000):
    if not isinstance(value, str) or len(value) > limit:
        raise ValueError(f'{label}必须是最多 {limit} 字的文本。')
    return value.strip()


def normalize_profile(data):
    if not isinstance(data, dict):
        raise ValueError('配置必须是 JSON 对象。')
    base = text(data.get('base', ''), 'Base URL', 2000).rstrip('/')
    if any(c.isspace() or ord(c) < 32 for c in base):
        raise ValueError('Base URL 不能包含空白或控制字符。')
    try:
        parsed = urlsplit(base)
        host = parsed.hostname
        parsed.port
    except ValueError:
        raise ValueError('Base URL 主机或端口无效。') from None
    if parsed.scheme not in ('https', 'http') or not host:
        raise ValueError('请填写完整的 HTTPS Base URL。')
    if parsed.scheme == 'http' and host not in ('localhost', '127.0.0.1', '::1'):
        raise ValueError('远程 API 示例要求 HTTPS；HTTP 仅用于本地开发。')
    if parsed.username is not None or parsed.password is not None or parsed.query or parsed.fragment:
        raise ValueError('Base URL 不可包含账号、密码、查询参数或片段。')
    protocol = data.get('protocol', 'responses')
    if protocol not in ('responses', 'chat'):
        raise ValueError('接口类型必须是 responses 或 chat。')
    model = text(data.get('model', ''), '模型 ID', 200)
    if not model or any(ord(c) < 32 for c in model):
        raise ValueError('请填写有效的模型 ID。')
    return {'base': base, 'model': model, 'protocol': protocol}


def generate(data):
    profile = normalize_profile(data)
    prompt = text(data.get('prompt', '请用三句话解释这段代码的作用。'), '任务')
    if not prompt:
        raise ValueError('任务内容不能为空。')
    suffix = '/responses' if profile['protocol'] == 'responses' else '/chat/completions'
    base = profile['base']
    if base.endswith(('/responses', '/chat/completions', '/models')):
        raise ValueError('请填写 Base URL，不要填写完整的接口端点。')
    endpoint = base + suffix
    payload = {'model': profile['model']}
    if profile['protocol'] == 'responses':
        payload['input'] = prompt
    else:
        payload['messages'] = [{'role': 'user', 'content': prompt}]
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    python = ('import json, os, urllib.request\n\n'
              f'payload = json.loads({body!r})\n'
              f'request = urllib.request.Request({endpoint!r},\n'
              '    data=json.dumps(payload).encode("utf-8"),\n'
              '    headers={"Authorization": "Bearer " + os.environ["API_KEY"],\n'
              '             "Content-Type": "application/json"}, method="POST")\n'
              'with urllib.request.urlopen(request, timeout=60) as response:\n'
              '    print(response.read().decode("utf-8"))\n')
    curl = (f'curl {shlex.quote(endpoint)} \\\n'
            '  -H "Authorization: Bearer $API_KEY" \\\n'
            '  -H "Content-Type: application/json" \\\n'
            f'  --data-raw {shlex.quote(body)}')
    powershell = ("$headers = @{ Authorization = \"Bearer $env:API_KEY\" }\n"
                  + "$body = '" + body.replace("'", "''") + "'\n"
                  + "Invoke-RestMethod -Method Post -Uri '" + endpoint.replace("'", "''")
                  + "' -Headers $headers -ContentType 'application/json; charset=utf-8' "
                  + '-Body ([System.Text.Encoding]::UTF8.GetBytes($body))\n')
    javascript = ('// Node.js 18+; API_KEY is read from your environment.\n'
                  f'const response = await fetch({json.dumps(endpoint)}, {{\n'
                  '  method: "POST",\n'
                  '  headers: { Authorization: `Bearer ${process.env.API_KEY}`, "Content-Type": "application/json" },\n'
                  f'  body: JSON.stringify({body})\n'
                  '});\nif (!response.ok) throw new Error(`HTTP ${response.status}`);\n'
                  'console.log(await response.json());\n')
    return {'profile': profile, 'endpoint': endpoint, 'payload': payload,
            'snippets': {'Python': python, 'curl': curl, 'PowerShell': powershell, 'JavaScript': javascript}}


def estimate(data):
    result = {}
    for key in ('input_tokens', 'output_tokens', 'input_price', 'output_price', 'requests'):
        value = data.get(key, 1 if key == 'requests' else 0)
        if isinstance(value, bool):
            raise ValueError('数量与价格必须是非负数字。')
        try:
            number = Decimal(str(value))
        except (InvalidOperation, ValueError):
            raise ValueError('数量与价格必须是非负数字。') from None
        if not number.is_finite() or number < 0 or number > Decimal('1e12'):
            raise ValueError('数字必须在 0 到 10^12 之间。')
        if key in ('input_tokens', 'output_tokens', 'requests') and number != number.to_integral_value():
            raise ValueError('Token 数与请求数必须是整数。')
        result[key] = number
    per_request = (result['input_tokens'] * result['input_price']
                   + result['output_tokens'] * result['output_price']) / Decimal(1000000)
    return {'per_request': format(per_request, '.8f'),
            'total': format(per_request * result['requests'], '.8f'),
            'note': '价格由你手动填写，单位为所选货币 / 百万 Token；不是实时官方报价。'}


def make_prompt(data):
    catalog = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
    recipe = next((r for r in catalog['recipes'] if r['id'] == data.get('recipe')), None)
    if recipe is None:
        raise ValueError('任务模板不存在。')
    goal = text(data.get('goal', ''), '目标')
    context = text(data.get('context', ''), '上下文')
    if not goal:
        raise ValueError('请先填写任务目标。')
    return {'prompt': f"任务类型：{recipe['title']}\n\n目标：\n{goal}\n\n上下文与限制：\n{context or '请先检查现有项目，再选择最小必要改动。'}\n\n执行要求：\n"
            + '\n'.join(f'{i + 1}. {step}' for i, step in enumerate(recipe['steps']))
            + '\n\n交付要求：给出完成的修改、验证证据、未完成事项和明确的使用方法。不要编造运行结果。'}


class Handler(BaseHTTPRequestHandler):
    server_version = 'NBWorkbench/1.0'

    def log_message(self, *_):
        pass

    def allowed(self):
        allowed_hosts = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
        host = self.headers.get('Host', '')
        origin = self.headers.get('Origin')
        return host in allowed_hosts and (origin is None or origin == 'http://' + host)

    def send(self, status, body, kind='application/json; charset=utf-8'):
        if not isinstance(body, bytes):
            body = json.dumps(body, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self.allowed():
            return self.send(403, {'error': '仅接受本地工作台请求。'})
        path = urlsplit(self.path).path
        if path == '/api/catalog':
            return self.send(200, json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8')))
        files = {'/': ('index.html', 'text/html; charset=utf-8'),
                 '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
                 '/style.css': ('style.css', 'text/css; charset=utf-8')}
        if path not in files:
            return self.send(404, {'error': '页面不存在。'})
        name, kind = files[path]
        return self.send(200, (ROOT / 'web' / name).read_bytes(), kind)

    def do_POST(self):
        if not self.allowed():
            return self.send(403, {'error': '仅接受同源本地请求。'})
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            return self.send(415, {'error': '请发送 application/json。'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length < 1 or length > 65536:
                return self.send(413, {'error': '请求大小应为 1–65536 字节。'})
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError('请求必须是 JSON 对象。')
            operations = {'/api/generate': generate, '/api/estimate': estimate,
                          '/api/prompt': make_prompt, '/api/validate': normalize_profile}
            operation = operations.get(urlsplit(self.path).path)
            if operation is None:
                return self.send(404, {'error': '接口不存在。'})
            return self.send(200, operation(data))
        except (ValueError, UnicodeDecodeError) as error:
            return self.send(400, {'error': str(error)})


def main():
    parser = argparse.ArgumentParser(description='NB Codex破甲工作台：本地开发工具，无需第三方 Python 依赖。')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--version', action='version', version=VERSION)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('端口应在 1–65535 之间。')
    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    except OSError as error:
        parser.exit(1, f'启动失败：{error}；请尝试 --port 8766。\n')
    server.daemon_threads = True
    print(f'NB Codex Pojia Workbench v{VERSION}: http://127.0.0.1:{args.port}', flush=True)
    print('停止服务：Ctrl+C。此工作台仅生成示例，不会向模型服务发送请求。', flush=True)
    if not args.no_browser:
        webbrowser.open(f'http://127.0.0.1:{args.port}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()

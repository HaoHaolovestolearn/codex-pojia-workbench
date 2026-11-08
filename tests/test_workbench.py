import ast
import os
import subprocess
import sys
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

import workbench as w


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.profile = {'base': 'https://example.com/v1', 'model': 'demo-model', 'protocol': 'responses'}

    def test_responses_and_chat_payloads(self):
        result = w.generate({**self.profile, 'prompt': '中文任务'})
        self.assertEqual(result['endpoint'], 'https://example.com/v1/responses')
        self.assertEqual(result['payload']['input'], '中文任务')
        chat = w.generate({**self.profile, 'protocol': 'chat', 'prompt': 'hello'})
        self.assertEqual(chat['payload']['messages'], [{'role': 'user', 'content': 'hello'}])
        self.assertTrue(chat['endpoint'].endswith('/chat/completions'))

    def test_generated_python_is_valid_and_preserves_special_characters(self):
        prompt = "单引号'，双引号\"，换行\n和 $HOME `commands`"
        result = w.generate({**self.profile, 'prompt': prompt})
        ast.parse(result['snippets']['Python'])
        self.assertEqual(result['payload']['input'], prompt)
        self.assertEqual(len(result['snippets']), 4)
        self.assertIn('os.environ["API_KEY"]', result['snippets']['Python'])

    def test_credentials_queries_and_remote_plaintext_are_rejected(self):
        for base in ['file:///tmp/test', 'https://user:pass@example.com/v1',
                     'https://example.com?api_key=secret', 'https://example.com#secret',
                     'http://example.com/v1', 'https://example.com:bad', 'https://exa mple.com']:
            with self.subTest(base=base), self.assertRaises(ValueError):
                w.normalize_profile({**self.profile, 'base': base})

    def test_profile_whitelists_fields(self):
        result = w.normalize_profile({**self.profile, 'api_key': 'test-secret'})
        self.assertEqual(result, self.profile)
        self.assertNotIn('test-secret', json.dumps(result))

    def test_local_http_allowed_and_complete_endpoints_rejected(self):
        self.assertEqual(w.normalize_profile({**self.profile, 'base': 'http://localhost:1234/v1/'})['base'], 'http://localhost:1234/v1')
        for suffix in ['/models', '/responses', '/chat/completions']:
            with self.assertRaises(ValueError):
                w.generate({**self.profile, 'base': 'https://example.com/v1' + suffix})

    def test_cli_handles_legacy_windows_console_encoding(self):
        environment = dict(os.environ, PYTHONIOENCODING='cp1252')
        result = subprocess.run([sys.executable, str(w.ROOT / 'workbench.py'), '--help'],
                                env=environment, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8', errors='replace'))
        self.assertIn('本地开发工具', result.stdout.decode('utf-8'))

    def test_cost_decimal_arithmetic(self):
        result = w.estimate({'input_tokens': 2000, 'output_tokens': 1000, 'input_price': 1, 'output_price': 2, 'requests': 100})
        self.assertEqual(result['per_request'], '0.00400000')
        self.assertEqual(result['total'], '0.40000000')

    def test_cost_rejects_invalid_and_fractional_counts(self):
        for value in [-1, 'nan', 'Infinity', True, 'bad', 1.5, '1e1000']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                w.estimate({'requests': value})

    def test_all_task_recipes_generate_complete_prompts(self):
        catalog = json.loads((w.ROOT / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(len({r['id'] for r in catalog['recipes']}), 12)
        for recipe in catalog['recipes']:
            prompt = w.make_prompt({'recipe': recipe['id'], 'goal': '完成示例任务', 'context': 'Python 3.10'})['prompt']
            self.assertIn('完成示例任务', prompt)
            self.assertIn('Python 3.10', prompt)
            self.assertIn('交付要求', prompt)
        with self.assertRaises(ValueError):
            w.make_prompt({'recipe': 'unknown', 'goal': 'demo'})


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), w.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        try:
            connection.request(method, path, body, headers or {})
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def test_static_assets_and_community_link(self):
        for path in ['/', '/style.css', '/app.js', '/api/catalog']:
            status, headers, body = self.request('GET', path)
            self.assertEqual(status, 200)
            self.assertGreater(len(body), 10)
            self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
        self.assertIn(b'https://t.me/HaoNB_6666', self.request('GET', '/')[2])

    def test_valid_api_and_validation_error(self):
        headers = {'Content-Type': 'application/json'}
        self.assertEqual(self.request('POST', '/api/estimate', '{}', headers)[0], 200)
        self.assertEqual(self.request('POST', '/api/estimate', '{', headers)[0], 400)
        self.assertEqual(self.request('POST', '/api/estimate', '[]', headers)[0], 400)
        self.assertEqual(self.request('POST', '/api/validate', '{}', headers)[0], 400)

    def test_cross_origin_requests_are_blocked(self):
        headers = {'Content-Type': 'application/json', 'Origin': 'https://evil.example'}
        self.assertEqual(self.request('POST', '/api/estimate', '{}', headers)[0], 403)
        self.assertEqual(self.request('GET', '/', headers={'Host': 'evil.example'})[0], 403)

    def test_content_type_size_and_unknown_paths(self):
        self.assertEqual(self.request('POST', '/api/estimate', '{}')[0], 415)
        headers = {'Content-Type': 'application/json'}
        self.assertEqual(self.request('POST', '/api/estimate', ' ' * 65537, headers)[0], 413)
        self.assertEqual(self.request('GET', '/../workbench.py')[0], 404)
        self.assertEqual(self.request('POST', '/api/unknown', '{}', headers)[0], 404)


if __name__ == '__main__':
    unittest.main()

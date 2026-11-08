"""Start the packaged server and verify its bundled resources."""
import json
import socket
import subprocess
import sys
import time
import urllib.request
from urllib.error import URLError

with socket.socket() as candidate:
    candidate.bind(('127.0.0.1', 0))
    port = candidate.getsockname()[1]
process = subprocess.Popen([sys.argv[1], '--no-browser', '--port', str(port)])
try:
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f'Packaged server stopped: {process.returncode}')
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/catalog', timeout=2) as response:
                catalog = json.load(response)
            assert len(catalog['recipes']) == 12
            with urllib.request.urlopen(f'http://127.0.0.1:{port}/', timeout=2) as response:
                assert b'Codex' in response.read()
            print('Packaged server and bundled resources OK')
            break
        except (URLError, TimeoutError):
            time.sleep(.25)
    else:
        raise RuntimeError('Packaged server startup timed out')
finally:
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()

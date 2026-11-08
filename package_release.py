"""Build source ZIP and SHA256 files without third-party dependencies."""
import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
EXCLUDED = {'.git', '.venv', '__pycache__', 'dist', 'build', 'node_modules', 'test-results', '.pytest_cache'}


def build():
    output = ROOT / 'dist'
    output.mkdir(exist_ok=True)
    archive = output / 'Codex-Pojia-Workbench-Source.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(ROOT.rglob('*')):
            relative = path.relative_to(ROOT)
            if not path.is_file() or EXCLUDED.intersection(relative.parts):
                continue
            if path.name.startswith('.env') or path.suffix in ('.pyc', '.spec'):
                continue
            bundle.write(path, Path('codex-pojia-workbench') / relative)
    binary = output / 'Codex-Pojia-Workbench.exe'
    if binary.exists():
        binary.rename(output / 'Codex-Pojia-Workbench-Windows-x64.exe')
    artifacts = [archive]
    windows = output / 'Codex-Pojia-Workbench-Windows-x64.exe'
    if windows.exists():
        artifacts.append(windows)
    checksums = []
    for path in artifacts:
        checksums.append(hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + path.name)
    (output / 'SHA256SUMS.txt').write_text('\n'.join(checksums) + '\n', encoding='ascii')
    print('\n'.join(checksums))


if __name__ == '__main__':
    build()

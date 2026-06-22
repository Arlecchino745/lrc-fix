# lrc-fix

Fix encoding issues in `.lrc` (lyrics) files — auto-detect the original encoding and convert to UTF-8.

## What it does

- Scans a folder recursively for `*.lrc` files
- Detects the original encoding with [chardet](https://pypi.org/project/chardet/)
- Fixes HTML entities (`&#231;` → `ç` …)
- Converts and overwrites files in UTF-8
- Creates a raw backup before touching anything (`raw-original.lrc`)

## Usage

```bash
python lrc-fix.py <folder> [encoding]
```

| Argument | Default | Description |
|---|---|---|
| `folder` | `.` | Directory to scan for `.lrc` files |
| `encoding` | `utf-8` | Target encoding |

Example:

```bash
# Convert all .lrc files in D:\Music and subfolders to UTF-8
python lrc-fix.py D:\Music utf-8
```

## Download (Windows EXE)

Pre-built executables are available on the [Releases](https://github.com/Arlecchino745/lrc-fix/releases) page.

## Build from source

```bash
pip install -r requirements.txt
pyinstaller --onefile --name lrc-fix lrc-fix.py
```

The EXE will be at `dist/lrc-fix.exe`.

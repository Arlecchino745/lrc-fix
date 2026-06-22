import glob, chardet, html, sys, os

def convert_lrc(folder, target='utf-8'):
    lrc_files = glob.glob(os.path.join(folder, '**', '*.lrc'), recursive=True)

    if not lrc_files:
        print('No .lrc files found.')
        return

    for fpath in lrc_files:
        # 1. Read raw bytes
        with open(fpath, 'rb') as f:
            raw = f.read()

        # 2. Skip already-UTF8 files (fast path: try UTF-8 decode first)
        try:
            raw.decode('utf-8')
            print(f'⊘ {os.path.basename(fpath)}: already UTF-8, skipped')
            continue
        except UnicodeDecodeError:
            pass

        # 3. Backup original file as raw-<filename>
        dir_name = os.path.dirname(fpath)
        base_name = os.path.basename(fpath)
        backup_path = os.path.join(dir_name, f'raw-{base_name}')
        with open(backup_path, 'wb') as f:
            f.write(raw)
        print(f'⇄ {base_name}: backup → raw-{base_name}')

        # 4. Detect encoding & decode
        src = chardet.detect(raw)['encoding'] or 'utf-8'
        text = raw.decode(src)

        # 5. Fix HTML entities like &#231; -> ç
        text = html.unescape(text)

        # 6. Write in target encoding
        with open(fpath, 'w', encoding=target) as f:
            f.write(text)
        print(f'✓ {os.path.basename(fpath)}: {src} → {target}')

if __name__ == '__main__':
    folder = sys.argv[1] if len(sys.argv) > 1 else '.'
    target = sys.argv[2] if len(sys.argv) > 2 else 'utf-8'
    convert_lrc(folder, target)
    input('\nDone. Press Enter to exit.')
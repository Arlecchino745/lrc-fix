import glob, chardet, html, sys, os

# Priority order for Chinese LRC files.
# GB18030 is the superset of GBK/GB2312 — try it first for maximum coverage.
ENCODING_CANDIDATES = ['gb18030', 'gbk', 'gb2312', 'big5', 'shift_jis', 'euc_kr']

# Signature bytes that appear when GBK/GB2312 Chinese text
# is misinterpreted as Latin-1 (ISO-8859-1 / Windows-1252).
# The pair '¡¶' → '《' and '¡·' → '》' is the most reliable fingerprint.
MOJIBAKE_SIGNATURES = ['\xa1\xb6', '\xa1\xb7', '\xa1\xc0', '\xa1\xc1']


def is_mojibake(text):
    """Check if `text` shows signs of GBK-bytes-misread-as-Latin-1 corruption."""
    if not text:
        return False
    # Count how many signature byte-pairs appear
    hits = sum(text.count(sig) for sig in MOJIBAKE_SIGNATURES)
    return hits >= 2


def try_decode(raw):
    """
    Try to decode `raw` bytes into a string.
    1) chardet first
    2) if chardet result is Latin-based (or uncertain), try Chinese encodings
    3) if the result still looks like mojibake, try reinterpreting
       (Latin-1 round-trip → GBK decode) to recover double-encoded files
    """
    detected = chardet.detect(raw)
    src = detected.get('encoding') or 'utf-8'
    confidence = detected.get('confidence') or 0

    # Latin-based encodings that cannot represent Chinese —
    # almost certainly a misdetection for CJK content.
    LATIN_ENCODINGS = {'ISO-8859-1', 'Windows-1252', 'Latin-1', 'ISO-8859-15',
                       'ISO-8859-9', 'Windows-1254', 'windows-1252', 'latin-1'}

    # --- Strategy A: trust chardet for non-Latin, high-confidence hits ---
    if src.lower() not in {e.lower() for e in LATIN_ENCODINGS} and confidence >= 0.7:
        try:
            text = raw.decode(src)
            if not is_mojibake(text):
                return text, src
        except (UnicodeDecodeError, LookupError):
            pass

    # --- Strategy B: double-encoded recovery (MUST run before brute-force) ---
    # The original GBK bytes were treated as Latin-1 and re-encoded to UTF-8.
    # Undo: decode raw as UTF-8, encode back with Latin-1, then decode as GB18030.
    # Runs BEFORE brute-force because valid UTF-8 bytes can accidentally
    # decode as GB18030 without error, producing wrong-but-plausible Chinese.
    try:
        text_utf8 = raw.decode('utf-8')
        if is_mojibake(text_utf8):
            text_recovered = text_utf8.encode('latin-1').decode('gb18030')
            return text_recovered, 'gb18030 (double-encoded recovery)'
    except (UnicodeDecodeError, UnicodeEncodeError, LookupError):
        pass

    # --- Strategy C: brute-force Chinese encodings ---
    for enc in ENCODING_CANDIDATES:
        try:
            text = raw.decode(enc)
            if not is_mojibake(text):
                return text, enc
        except (UnicodeDecodeError, LookupError):
            continue

    # --- Strategy D: chardet fallback (even if Latin-based) ---
    try:
        return raw.decode(src), src
    except (UnicodeDecodeError, LookupError):
        pass

    # --- Strategy E: utter last resort ---
    return raw.decode('utf-8', errors='replace'), 'utf-8 (fallback)'


def convert_lrc(folder, target='utf-8'):
    lrc_files = glob.glob(os.path.join(folder, '**', '*.lrc'), recursive=True)

    if not lrc_files:
        print('No .lrc files found.')
        return

    for fpath in lrc_files:
        # Skip backup files created by previous runs
        base_name = os.path.basename(fpath)
        if base_name.startswith('raw-'):
            print(f'⊘ {base_name}: backup file, skipped')
            continue

        # 1. Read raw bytes
        with open(fpath, 'rb') as f:
            raw = f.read()

        # 2. Skip already-UTF8 files (fast path: try UTF-8 decode first)
        try:
            text = raw.decode('utf-8')
            if not is_mojibake(text):
                print(f'⊘ {os.path.basename(fpath)}: already UTF-8, skipped')
                continue
            # Falls through if UTF-8 decodes but is mojibake (double-encoded!)
            # No continue here — let try_decode() handle recovery below.
        except UnicodeDecodeError:
            pass

        # 3. Backup original file as raw-<filename>
        dir_name = os.path.dirname(fpath)
        base_name = os.path.basename(fpath)
        backup_path = os.path.join(dir_name, f'raw-{base_name}')
        with open(backup_path, 'wb') as f:
            f.write(raw)
        print(f'⇄ {base_name}: backup → raw-{base_name}')

        # 4. Detect encoding & decode (with fallback chain)
        text, src = try_decode(raw)

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
## What's New in v1.1.0

- **Priority-ordered encoding candidates** — GB18030 → GBK → GB2312 → Big5 → Shift_JIS → EUC-KR, tried systematically for maximum Chinese LRC coverage.
- **Mojibake signature detection** — byte-pair fingerprints (`¡¶`/`¡·` → `《`/`》`) detect Chinese text that was misread as Latin-1.
- **5-strategy `try_decode()` fallback chain:**
  - **A** — Trust high-confidence non-Latin chardet results.
  - **B** — Double-encoded recovery: Latin-1 round-trip → GB18030 decode (undoes the classic "GBK bytes treated as Latin-1, re-saved as UTF-8" corruption).
  - **C** — Brute-force Chinese encodings in priority order.
  - **D** — Chardet fallback (even if Latin-based).
  - **E** — UTF-8 with replacement characters as last resort.
- **Improved UTF-8 fast path** — now re-checks for mojibake before skipping; handles double-encoded files that happen to decode as valid UTF-8.
- **Skip `raw-*` backup files** from previous runs so they aren't re-processed.

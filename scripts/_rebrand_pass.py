"""One-shot rebrand pass for BRAINROT (kept for reference).
Run from D:\\firma\\culoton-fresh. Replaces visible-text CuloTon/CULOTON/$CULOTON
with BRAINROT/$BRT while preserving GitHub URL, t.me handle, and the rebrand banner.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# File globs to touch.
TARGETS = [
    'web/src/data/launch.ts',
    'web/src/pages/about.astro',
    'web/src/pages/[locale]/about.astro',
    'web/src/pages/culo.astro',
    'web/src/pages/[locale]/culo.astro',
    'web/src/pages/ecosystem.astro',
    'web/src/pages/[locale]/ecosystem.astro',
    'web/src/pages/launch.astro',
    'web/src/pages/[locale]/launch.astro',
    'web/src/pages/stonks.astro',
    'web/src/pages/[locale]/stonks.astro',
    'web/src/pages/rss.xml.ts',
    'web/src/i18n/strings.ts',
    'web/src/components/FeaturedToken.astro',
    'web/astro.config.mjs',
    'scripts/meme_daily.py',
]

# Lines that contain these protected substrings are written back unchanged
# (we re-insert them after running the substitutions on the rest).
PROTECT_SUBSTRINGS = [
    'github.com/CuloTon',  # actual GitHub org/repo
    't.me/culoton',         # actual Telegram chat
    'x.com/culoton',        # actual X handle
    'culoton-theme',        # localStorage key for theme persistence
    'culoton-sid',          # sessionStorage analytics key
    'We rebranded',         # the rebrand banner line (Layout.astro)
    'CuloTon is now',       # rebrand banner translations
    'aus CuloTon wird',     # DE rebrand banner
    'CuloTon to teraz',     # PL rebrand banner
    'CuloTon ahora es',     # ES rebrand banner
    'CuloTon тепер',        # UK rebrand banner
    'CuloTon теперь',       # RU rebrand banner
    'formerly known as',    # ticker line referencing CuloTon
    'обычно как CuloTon',
    'OLD_CA_PLACEHOLDER',
]


def transform_line(line: str) -> str:
    if any(p in line for p in PROTECT_SUBSTRINGS):
        return line
    new = line
    # Domain (use full match — also handle https:// prefix)
    new = new.replace('https://culoton.fun', 'https://brainrot-ton.fun')
    new = new.replace('culoton.fun', 'brainrot-ton.fun')
    # Token ticker
    new = new.replace('$CULOTON', '$BRT')
    new = new.replace('CULOTON Launcher', 'BRAINROT Launcher')
    new = new.replace('CuloTon Launcher', 'BRAINROT Launcher')
    # Brand mentions (word-boundary)
    new = re.sub(r'\bCuloTon\b', 'BRAINROT', new)
    # Editor name
    new = re.sub(r'\bCuloScribe\b', 'BrainScribe', new)
    # Old truncated CA → new BRAINROT CA truncation
    new = new.replace('EQAYaqIikry…b0A2Uc', 'EQDsbT3…2PIh')
    new = new.replace('EQAYaqIikry...b0A2Uc', 'EQDsbT3…2PIh')
    return new


def main():
    touched = 0
    changed_files = []
    for rel in TARGETS:
        p = ROOT / rel
        if not p.exists():
            print(f'skip (missing): {rel}')
            continue
        orig = p.read_text(encoding='utf-8')
        new = '\n'.join(transform_line(ln) for ln in orig.split('\n'))
        if new != orig:
            p.write_text(new, encoding='utf-8')
            touched += 1
            changed_files.append(rel)
            # Quick diff summary
            for k in ('CuloTon', 'CULOTON', '$CULOTON', 'culoton.fun', 'EQAYaqIikry'):
                before = orig.count(k)
                after = new.count(k)
                if before != after:
                    print(f'  {rel}: {k}  {before} -> {after}')
    print(f'\nTouched {touched} files.')
    for f in changed_files:
        print('  -', f)


if __name__ == '__main__':
    main()

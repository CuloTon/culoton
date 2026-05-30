"""One-off: delete the pruned filler article directories from the live
brainrot-ton.fun FTP. deploy_local.py only uploads, never deletes, so the
290 removed articles' HTML stays orphaned on the server until we remove it.

Reads the slug list from a file (one slug per line) and deletes, for each
slug, the directory at:
  <root>/news/<slug>          (en)
  <root>/<loc>/news/<slug>    (ru, pl, de, es, uk)

Guard: only ever deletes a directory whose basename is in the slug set.

Usage: python prune_remote_filler.py SLUGFILE REMOTE_ROOT
Env:   FTP_HOST, FTP_USER, FTP_PASSWORD
"""
from __future__ import annotations

import os
import ssl
import sys
from ftplib import FTP_TLS, error_perm

LOCALES_SUB = ("ru", "pl", "de", "es", "uk")  # en lives at root /news


def connect() -> FTP_TLS:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ftp = FTP_TLS(os.environ["FTP_HOST"], timeout=60, context=ctx)
    ftp.login(os.environ["FTP_USER"], os.environ["FTP_PASSWORD"])
    ftp.prot_p()
    ftp.set_pasv(True)
    return ftp


def rmrf(ftp: FTP_TLS, path: str, allowed: set[str]) -> bool:
    """Recursively delete a remote directory. Returns True if removed."""
    base = path.rstrip("/").split("/")[-1]
    if base not in allowed:
        print(f"  GUARD: refuse to delete {path} (not in filler set)", file=sys.stderr)
        return False
    try:
        entries = ftp.nlst(path)
    except error_perm:
        return False  # doesn't exist
    for e in entries:
        name = e.split("/")[-1]
        if name in (".", ".."):
            continue
        full = e if e.startswith("/") else f"{path}/{name}"
        # article dirs are flat (index.html); try file delete, else recurse.
        try:
            ftp.delete(full)
        except error_perm:
            try:
                ftp.rmd(full)
            except error_perm:
                rmrf_child(ftp, full)
    try:
        ftp.rmd(path)
        return True
    except error_perm as e:
        print(f"  rmd failed {path}: {e}", file=sys.stderr)
        return False


def rmrf_child(ftp: FTP_TLS, path: str) -> None:
    try:
        for e in ftp.nlst(path):
            name = e.split("/")[-1]
            if name in (".", ".."):
                continue
            full = e if e.startswith("/") else f"{path}/{name}"
            try:
                ftp.delete(full)
            except error_perm:
                rmrf_child(ftp, full)
        ftp.rmd(path)
    except error_perm:
        pass


def main() -> int:
    slugfile, remote_root = sys.argv[1], "/" + sys.argv[2].strip("/")
    slugs = [s.strip() for s in open(slugfile, encoding="utf-8") if s.strip()]
    allowed = set(slugs)
    print(f"{len(slugs)} filler slugs; root={remote_root}")

    ftp = connect()
    removed = {"en": 0, "ru": 0, "pl": 0, "de": 0, "es": 0, "uk": 0}
    for i, slug in enumerate(slugs, 1):
        targets = [("en", f"{remote_root}/news/{slug}")]
        targets += [(loc, f"{remote_root}/{loc}/news/{slug}") for loc in LOCALES_SUB]
        for loc, path in targets:
            try:
                if rmrf(ftp, path, allowed):
                    removed[loc] += 1
            except Exception as ex:
                print(f"  err {path}: {type(ex).__name__}: {ex}", file=sys.stderr)
                try:
                    ftp.quit()
                except Exception:
                    pass
                ftp = connect()
        if i % 25 == 0:
            print(f"  {i}/{len(slugs)} slugs processed; removed so far: {removed}")
    try:
        ftp.quit()
    except Exception:
        ftp.close()
    print(f"DONE. removed per locale: {removed}  total: {sum(removed.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

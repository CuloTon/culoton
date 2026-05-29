"""Robust LOCAL FTPS deploy for brainrot-ton.fun (run from a Polish IP).

Why this exists separately from deploy_ftp.py: seohost drops the FTP
control connection (WinError 10054) if it sits idle while we hash ~2000
local files, and it occasionally resets mid-upload. This script:

  1. Hashes ALL local files FIRST, with no connection open (no idle reset).
  2. Computes the changed set vs the remote manifest.
  3. Connects only then, and uploads — reconnecting on any drop.
  4. Drops the Basic-Auth gate (.htaccess/.htpasswd) and swaps
     home/index.html -> index.html, like the GH post-deploy step did.

Usage: python deploy_local.py LOCAL_DIR REMOTE_DIR
Env:   FTP_HOST, FTP_USER, FTP_PASSWORD
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import ssl
import sys
import time
from ftplib import FTP_TLS, error_perm
from pathlib import Path

MANIFEST_NAME = ".deploy-manifest.json"
# Never push these to the live root — they gate the whole site behind
# Basic Auth. They exist in dist from the preview phase; we delete them
# from the remote instead.
GATE_FILES = {".htaccess", ".htpasswd"}


def connect() -> FTP_TLS:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ftp = FTP_TLS(os.environ["FTP_HOST"], timeout=60, context=ctx)
    ftp.login(os.environ["FTP_USER"], os.environ["FTP_PASSWORD"])
    ftp.prot_p()
    ftp.set_pasv(True)
    return ftp


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class Conn:
    """FTP connection that transparently reconnects on a dropped socket."""

    def __init__(self) -> None:
        self.ftp = connect()
        self._dirs: set[str] = set()

    def reconnect(self) -> None:
        try:
            self.ftp.close()
        except Exception:
            pass
        self.ftp = connect()
        self._dirs.clear()
        print("  (reconnected)", flush=True)

    def ensure_dir(self, path: str) -> None:
        if path in self._dirs:
            return
        parts = [p for p in path.strip("/").split("/") if p]
        cur = ""
        for p in parts:
            cur = f"{cur}/{p}" if cur else f"/{p}"
            try:
                self.ftp.cwd(cur)
            except error_perm:
                self.ftp.mkd(cur)
                self.ftp.cwd(cur)
        self.ftp.cwd("/")
        self._dirs.add(path)

    def upload(self, local: Path, remote: str, attempts: int = 4) -> None:
        last = None
        for i in range(attempts):
            try:
                remote_dir = "/".join(remote.split("/")[:-1])
                self.ensure_dir(remote_dir)
                with local.open("rb") as fh:
                    self.ftp.storbinary(f"STOR {remote}", fh)
                return
            except Exception as e:
                last = e
                print(f"  retry {i+1}/{attempts} ({remote.split('/')[-1]}): {e}", flush=True)
                self.reconnect()
                time.sleep(1.5 * (i + 1))
        raise RuntimeError(f"upload failed for {remote}: {last}")

    def upload_bytes(self, payload: bytes, remote: str, attempts: int = 4) -> None:
        last = None
        for i in range(attempts):
            try:
                self.ftp.storbinary(f"STOR {remote}", io.BytesIO(payload))
                return
            except Exception as e:
                last = e
                print(f"  manifest retry {i+1}/{attempts}: {e}", flush=True)
                self.reconnect()
                time.sleep(1.5 * (i + 1))
        raise RuntimeError(f"manifest upload failed: {last}")


def download_manifest(ftp: FTP_TLS, remote_root: str) -> dict[str, str]:
    buf = io.BytesIO()
    try:
        ftp.retrbinary(f"RETR {remote_root}/{MANIFEST_NAME}", buf.write)
    except Exception:
        return {}
    try:
        data = json.loads(buf.getvalue().decode("utf-8"))
    except Exception:
        return {}
    return {k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, str)} if isinstance(data, dict) else {}


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: deploy_local.py LOCAL_DIR REMOTE_DIR", file=sys.stderr)
        return 2
    local_root = Path(sys.argv[1]).resolve()
    remote_root = "/" + sys.argv[2].strip("/")
    if not local_root.is_dir():
        print(f"local dir not found: {local_root}", file=sys.stderr)
        return 2

    # 1) Hash everything locally first — no connection held open.
    files = sorted(p for p in local_root.rglob("*") if p.is_file())
    print(f"hashing {len(files)} local files (offline) ...", flush=True)
    local_sha: dict[str, str] = {}
    for f in files:
        rel = f.relative_to(local_root).as_posix()
        local_sha[rel] = file_sha256(f)

    # 2) Short connection: pull previous manifest, then compute the diff.
    print("connecting to fetch manifest ...", flush=True)
    tmp = connect()
    prev = download_manifest(tmp, remote_root)
    try:
        tmp.quit()
    except Exception:
        tmp.close()
    print(f"previous manifest: {len(prev)} entries", flush=True)

    to_upload = [
        rel for rel, sha in local_sha.items()
        if Path(rel).name not in GATE_FILES and prev.get(rel) != sha
    ]
    print(f"{len(to_upload)} changed files to upload ({len(local_sha) - len(to_upload)} unchanged/skipped).", flush=True)

    # 3) Fresh connection, upload changed files (reconnect on any drop).
    c = Conn()
    t0 = time.time()
    for i, rel in enumerate(to_upload, 1):
        c.upload(local_root / rel, f"{remote_root}/{rel}")
        if i % 50 == 0 or i == len(to_upload):
            print(f"  {i}/{len(to_upload)} uploaded ({time.time()-t0:.0f}s)", flush=True)

    # 4) Post-deploy: drop the Basic-Auth gate and make root = home page.
    for g in GATE_FILES:
        try:
            c.ftp.delete(f"{remote_root}/{g}")
            print(f"deleted {g} (gate dropped)", flush=True)
        except Exception as e:
            print(f"  skip delete {g}: {e}", flush=True)
    try:
        buf = io.BytesIO()
        c.ftp.retrbinary(f"RETR {remote_root}/home/index.html", buf.write)
        c.ftp.storbinary(f"STOR {remote_root}/index.html", io.BytesIO(buf.getvalue()))
        print(f"index.html <- home/index.html ({len(buf.getvalue())} bytes)", flush=True)
    except Exception as e:
        print(f"  home->index swap skipped: {e}", flush=True)

    # 5) Persist manifest (only gate-excluded local files we actually track).
    manifest = {rel: sha for rel, sha in local_sha.items() if Path(rel).name not in GATE_FILES}
    payload = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    c.upload_bytes(payload, f"{remote_root}/{MANIFEST_NAME}")
    print(f"manifest written ({len(manifest)} entries).", flush=True)

    try:
        c.ftp.quit()
    except Exception:
        c.ftp.close()
    print(f"DONE: {len(to_upload)} uploaded in {time.time()-t0:.0f}s.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Like deploy_ftp.py but reconnects every N files to dodge seohost idle/session timeouts."""
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
RECONNECT_EVERY = 80  # reconnect after this many uploads


def connect(host: str, user: str, password: str) -> FTP_TLS:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ftp = FTP_TLS(host, timeout=60, context=ctx)
    ftp.login(user, password)
    ftp.prot_p()
    ftp.set_pasv(True)
    return ftp


def ensure_dir(ftp: FTP_TLS, path: str) -> None:
    parts = [p for p in path.strip("/").split("/") if p]
    cur = ""
    for p in parts:
        cur = f"{cur}/{p}" if cur else f"/{p}"
        try:
            ftp.cwd(cur)
        except error_perm:
            ftp.mkd(cur)
            ftp.cwd(cur)
    ftp.cwd("/")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def list_remote_dir(ftp: FTP_TLS, path: str) -> dict[str, int]:
    sizes: dict[str, int] = {}
    try:
        for name, facts in ftp.mlsd(path, facts=["type", "size"]):
            if facts.get("type") == "file":
                try:
                    sizes[name] = int(facts.get("size", "-1"))
                except ValueError:
                    sizes[name] = -1
    except Exception:
        return {}
    return sizes


def upload_with_reconnect(host, user, pw, local: Path, remote: str, attempts: int = 5):
    last = None
    for i in range(attempts):
        try:
            ftp = connect(host, user, pw)
            with local.open("rb") as fh:
                ftp.storbinary(f"STOR {remote}", fh)
            ftp.quit()
            return
        except Exception as e:
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"upload failed for {remote}: {last}")


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: deploy_ftp_reconnect.py LOCAL_DIR REMOTE_DIR", file=sys.stderr)
        return 2

    local_root = Path(sys.argv[1]).resolve()
    remote_root = "/" + sys.argv[2].strip("/")

    if not local_root.is_dir():
        print(f"local dir not found: {local_root}", file=sys.stderr)
        return 2

    host = os.environ["FTP_HOST"]
    user = os.environ["FTP_USER"]
    pw = os.environ["FTP_PASSWORD"]

    print(f"connecting to {host} as {user} ...", flush=True)
    ftp = connect(host, user, pw)
    print(f"connected, pwd={ftp.pwd()}", flush=True)

    ensure_dir(ftp, remote_root)

    files = sorted(p for p in local_root.rglob("*") if p.is_file())
    total = len(files)
    print(f"local files: {total}", flush=True)

    new_manifest: dict[str, str] = {}
    ensured_dirs: set[str] = set()
    remote_dir_listings: dict[str, dict[str, int]] = {}
    uploaded = 0
    skipped = 0
    processed = 0
    since_reconnect = 0
    t_start = time.time()

    for f in files:
        rel = f.relative_to(local_root).as_posix()
        sha = file_sha256(f)
        new_manifest[rel] = sha

        remote_path = f"{remote_root}/{rel}"
        parts = remote_path.split("/")
        remote_dir = "/".join(parts[:-1])
        name = parts[-1]
        if remote_dir not in ensured_dirs:
            try:
                ensure_dir(ftp, remote_dir)
            except Exception:
                # reconnect & retry
                try: ftp.quit()
                except Exception: pass
                ftp = connect(host, user, pw)
                ensure_dir(ftp, remote_dir)
            ensured_dirs.add(remote_dir)
            remote_dir_listings[remote_dir] = list_remote_dir(ftp, remote_dir)

        local_size = f.stat().st_size
        remote_size = remote_dir_listings.get(remote_dir, {}).get(name)
        if remote_size == local_size:
            skipped += 1
        else:
            # try via current connection; if fails, reconnect once
            try:
                with f.open("rb") as fh:
                    ftp.storbinary(f"STOR {remote_path}", fh)
            except Exception as e:
                print(f"  conn error, reconnecting: {e}", flush=True)
                try: ftp.quit()
                except Exception: pass
                ftp = connect(host, user, pw)
                with f.open("rb") as fh:
                    ftp.storbinary(f"STOR {remote_path}", fh)
            uploaded += 1
            since_reconnect += 1

        processed += 1

        # proactive reconnect to dodge idle/session timeouts
        if since_reconnect >= RECONNECT_EVERY:
            try: ftp.quit()
            except Exception: pass
            ftp = connect(host, user, pw)
            since_reconnect = 0

        if processed % 100 == 0 or processed == total:
            elapsed = time.time() - t_start
            print(
                f"  {processed}/{total}  up={uploaded} skip={skipped}  ({elapsed:.0f}s)",
                flush=True,
            )

    # write manifest
    payload = json.dumps(new_manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    try:
        ftp.storbinary(f"STOR {remote_root}/{MANIFEST_NAME}", io.BytesIO(payload))
        print(f"manifest written ({len(new_manifest)} entries)", flush=True)
    except Exception as e:
        print(f"manifest write failed: {e}", flush=True)

    try: ftp.quit()
    except Exception: pass
    elapsed = time.time() - t_start
    print(f"DONE: {uploaded} up, {skipped} skip, in {elapsed:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

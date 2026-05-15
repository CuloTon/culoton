"""Mirror a local directory to a remote FTPS host.

Used by GitHub Actions instead of off-the-shelf FTP actions, because
SamKirkland/FTP-Deploy-Action and lftp both fail against seohost.pl
from Azure runner IPs (passive data socket / connection issues).

Strategy: keep a JSON manifest of {rel_path: sha256} on the remote
host. On each run we download the previous manifest, hash local files,
and only push the ones whose content changed. With ~2000 site pages
this turns a ~60 min FTPS sync into seconds when nothing changed —
each per-directory MLSD round-trip was the bottleneck, not the data.

Usage: python deploy_ftp.py LOCAL_DIR REMOTE_DIR

Env:
  FTP_HOST, FTP_USER, FTP_PASSWORD — credentials
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
    """Return {filename: size} for files in remote dir. Empty dict on any failure."""
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


def download_manifest(ftp: FTP_TLS, remote_root: str) -> dict[str, str]:
    """Return previous manifest from the remote, or {} if none/unreadable."""
    buf = io.BytesIO()
    try:
        ftp.retrbinary(f"RETR {remote_root}/{MANIFEST_NAME}", buf.write)
    except error_perm:
        return {}
    except Exception as e:
        print(f"  manifest fetch failed ({e}); treating as empty.", flush=True)
        return {}
    try:
        data = json.loads(buf.getvalue().decode("utf-8"))
    except Exception as e:
        print(f"  manifest parse failed ({e}); treating as empty.", flush=True)
        return {}
    if not isinstance(data, dict):
        return {}
    return {k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, str)}


def upload_bytes(ftp: FTP_TLS, payload: bytes, remote_path: str, attempts: int = 3) -> None:
    last_err: Exception | None = None
    for i in range(attempts):
        try:
            ftp.storbinary(f"STOR {remote_path}", io.BytesIO(payload))
            return
        except Exception as e:
            last_err = e
            print(f"  manifest retry {i+1}/{attempts}: {e}", flush=True)
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"upload failed for {remote_path}: {last_err}")


def upload_file(ftp: FTP_TLS, local: Path, remote: str, attempts: int = 3) -> None:
    last_err: Exception | None = None
    for i in range(attempts):
        try:
            with local.open("rb") as fh:
                ftp.storbinary(f"STOR {remote}", fh)
            return
        except Exception as e:
            last_err = e
            print(f"  retry {i+1}/{attempts}: {e}", flush=True)
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"upload failed for {remote}: {last_err}")


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: deploy_ftp.py LOCAL_DIR REMOTE_DIR", file=sys.stderr)
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

    print("fetching previous manifest ...", flush=True)
    prev = download_manifest(ftp, remote_root)
    has_manifest = bool(prev)
    print(
        f"previous manifest: {len(prev)} entries"
        f"{' — using sha-only fast path' if has_manifest else ' (empty — falling back to remote size check for the first run)'}",
        flush=True,
    )

    files = sorted(p for p in local_root.rglob("*") if p.is_file())
    total = len(files)
    print(f"hashing {total} local files ...", flush=True)

    new_manifest: dict[str, str] = {}
    ensured_dirs: set[str] = set()
    remote_dir_listings: dict[str, dict[str, int]] = {}
    uploaded = 0
    skipped = 0
    processed = 0
    t_start = time.time()

    for f in files:
        rel = f.relative_to(local_root).as_posix()
        sha = file_sha256(f)
        new_manifest[rel] = sha

        if has_manifest and prev.get(rel) == sha:
            skipped += 1
        else:
            remote_path = f"{remote_root}/{rel}"
            parts = remote_path.split("/")
            remote_dir = "/".join(parts[:-1])
            name = parts[-1]
            if remote_dir not in ensured_dirs:
                ensure_dir(ftp, remote_dir)
                ensured_dirs.add(remote_dir)
                if not has_manifest:
                    remote_dir_listings[remote_dir] = list_remote_dir(ftp, remote_dir)
            # First-run fallback: if manifest is missing, accept the remote
            # file when its size matches the local size — same heuristic as
            # the old deploy script. Avoids re-uploading the whole site once.
            local_size = f.stat().st_size
            remote_size = remote_dir_listings.get(remote_dir, {}).get(name)
            if not has_manifest and remote_size == local_size:
                skipped += 1
            else:
                upload_file(ftp, f, remote_path)
                uploaded += 1

        processed += 1
        if processed % 200 == 0 or processed == total:
            elapsed = time.time() - t_start
            print(
                f"  {processed}/{total}  uploaded={uploaded} skipped={skipped}  "
                f"({elapsed:.0f}s)",
                flush=True,
            )

    payload = json.dumps(new_manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    print(f"writing new manifest ({len(new_manifest)} entries, {len(payload)} bytes) ...", flush=True)
    upload_bytes(ftp, payload, f"{remote_root}/{MANIFEST_NAME}")

    ftp.quit()
    elapsed = time.time() - t_start
    print(
        f"done: {uploaded} uploaded, {skipped} skipped (sha match), "
        f"in {elapsed:.0f}s",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

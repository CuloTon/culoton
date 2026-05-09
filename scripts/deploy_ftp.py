"""Mirror a local directory to a remote FTPS host.

Used by GitHub Actions instead of off-the-shelf FTP actions, because
SamKirkland/FTP-Deploy-Action and lftp both fail against seohost.pl
from Azure runner IPs (passive data socket / connection issues).

Usage: python deploy_ftp.py LOCAL_DIR REMOTE_DIR

Env:
  FTP_HOST, FTP_USER, FTP_PASSWORD — credentials
"""
from __future__ import annotations

import os
import ssl
import sys
import time
from ftplib import FTP_TLS, error_perm
from pathlib import Path


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
        # MLSD not supported or directory empty/missing; treat as empty
        return {}
    return sizes


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

    files = sorted(p for p in local_root.rglob("*") if p.is_file())
    total = len(files)
    print(f"syncing {total} files to {remote_root}/ (size-based skip)", flush=True)

    remote_dir_listings: dict[str, dict[str, int]] = {}
    ensured_dirs: set[str] = set()
    uploaded = 0
    skipped = 0
    processed = 0
    t_start = time.time()

    for f in files:
        rel = f.relative_to(local_root).as_posix()
        remote_path = f"{remote_root}/{rel}"
        parts = remote_path.split("/")
        remote_dir = "/".join(parts[:-1])
        name = parts[-1]

        if remote_dir not in ensured_dirs:
            ensure_dir(ftp, remote_dir)
            ensured_dirs.add(remote_dir)
            remote_dir_listings[remote_dir] = list_remote_dir(ftp, remote_dir)

        local_size = f.stat().st_size
        remote_size = remote_dir_listings[remote_dir].get(name)

        if remote_size == local_size:
            skipped += 1
        else:
            upload_file(ftp, f, remote_path)
            uploaded += 1

        processed += 1
        if processed % 50 == 0 or processed == total:
            elapsed = time.time() - t_start
            print(
                f"  {processed}/{total}  uploaded={uploaded} skipped={skipped}  "
                f"({elapsed:.0f}s)",
                flush=True,
            )

    ftp.quit()
    elapsed = time.time() - t_start
    print(
        f"done: {uploaded} uploaded, {skipped} skipped (identical size), "
        f"in {elapsed:.0f}s",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

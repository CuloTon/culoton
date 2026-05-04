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
    print(f"uploading {len(files)} files to {remote_root}/", flush=True)

    uploaded = 0
    for f in files:
        rel = f.relative_to(local_root).as_posix()
        remote_path = f"{remote_root}/{rel}"
        remote_dir = "/".join(remote_path.split("/")[:-1])
        ensure_dir(ftp, remote_dir)
        upload_file(ftp, f, remote_path)
        uploaded += 1
        if uploaded % 5 == 0 or uploaded == len(files):
            print(f"  {uploaded}/{len(files)} {rel}", flush=True)

    ftp.quit()
    print(f"done: {uploaded} files uploaded", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

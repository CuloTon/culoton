"""Shared $CULO market data helpers.

Used by both telegram_notify.py and x_notify.py so price/FDV/volume
formatting and GeckoTerminal access stay in one place.
"""

from __future__ import annotations

import json
import sys
import urllib.request

CULO_CONTRACT = "EQD5dCm196cT60OTcCz_MI_f_QtpZYGU5mazX-4rjAOHiKrJ"
GECKO_NET = "ton"
GECKO_API = "https://api.geckoterminal.com/api/v2"
HTTP_TIMEOUT = 20


def http_get_json(url: str) -> dict | None:
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "CuloTon-Bot/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"  GET {url} failed: {e}", file=sys.stderr)
        return None


def fmt_money(amount) -> str:
    if amount is None:
        return "—"
    try:
        n = float(amount)
    except (TypeError, ValueError):
        return "—"
    if n < 0.01:
        return f"${n:.8f}".rstrip("0").rstrip(".")
    if n < 1:
        return f"${n:.4f}".rstrip("0").rstrip(".")
    if n < 1000:
        return f"${n:,.2f}"
    if n < 1_000_000:
        return f"${n/1000:.1f}K"
    if n < 1_000_000_000:
        return f"${n/1_000_000:.2f}M"
    return f"${n/1_000_000_000:.2f}B"


def fmt_change(pct) -> str:
    if pct is None:
        return "—"
    try:
        p = float(pct)
    except (TypeError, ValueError):
        return "—"
    sign = "+" if p >= 0 else ""
    return f"{sign}{p:.2f}%"


def fetch_culo_data() -> dict | None:
    """Fetch live $CULO market data from GeckoTerminal.

    Returns dict with: price, valuation (FDV/MCap), change_h24, vol_h24,
    pool_addr, dex. Returns None on hard failure. Numeric fields may
    be None when GeckoTerminal returns no data.
    """
    token_data = http_get_json(f"{GECKO_API}/networks/{GECKO_NET}/tokens/{CULO_CONTRACT}")
    pool_data = http_get_json(f"{GECKO_API}/networks/{GECKO_NET}/tokens/{CULO_CONTRACT}/pools")
    if not token_data or not pool_data:
        return None
    attrs = (token_data.get("data") or {}).get("attributes") or {}
    try:
        price = float(attrs.get("price_usd") or 0) or None
    except (TypeError, ValueError):
        price = None
    # Memecoins on DEX rarely have market_cap_usd populated; FDV is the
    # standard fallback for valuation.
    mcap = attrs.get("market_cap_usd")
    fdv = attrs.get("fdv_usd")
    valuation = None
    for cand in (mcap, fdv):
        if cand not in (None, ""):
            try:
                valuation = float(cand)
                break
            except (TypeError, ValueError):
                pass
    change_h24 = None
    vol_h24 = None
    pool_addr = None
    dex = None
    pools = pool_data.get("data") or []
    if pools:
        def vol_key(p):
            try:
                return float(((p.get("attributes") or {}).get("volume_usd") or {}).get("h24") or 0)
            except Exception:
                return 0
        pools = sorted(pools, key=vol_key, reverse=True)
        top = pools[0].get("attributes") or {}
        try:
            change_h24 = float((top.get("price_change_percentage") or {}).get("h24") or 0)
        except Exception:
            change_h24 = None
        try:
            vol_h24 = float((top.get("volume_usd") or {}).get("h24") or 0)
        except Exception:
            vol_h24 = None
        pool_addr = top.get("address")
        dex = ((pools[0].get("relationships") or {}).get("dex") or {}).get("data", {}).get("id")
    return {
        "price": price,
        "valuation": valuation,
        "change_h24": change_h24,
        "vol_h24": vol_h24,
        "pool_addr": pool_addr,
        "dex": dex,
    }

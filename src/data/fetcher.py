"""
data/fetcher.py — NSE session-based option chain fetcher with demo fallback.
Returns (df, is_live) tuple. is_live=False means demo data is being used.
"""

import time
import requests
import pandas as pd
from datetime import datetime

from src.data.generators import (
    generate_option_chain,
    generate_expiry_dates,
    _get_spot,
)


_NSE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer":         "https://www.nseindia.com/option-chain",
    "Connection":      "keep-alive",
    "DNT":             "1",
    "Sec-Fetch-Dest":  "empty",
    "Sec-Fetch-Mode":  "cors",
    "Sec-Fetch-Site":  "same-origin",
}

_NSE_API = "https://www.nseindia.com/api/option-chain-indices"


class NSEFetcher:
    """NSE live data fetcher with session management."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(_NSE_HEADERS)
        self._ready = False

    def _init_session(self) -> bool:
        if self._ready:
            return True
        try:
            r = self.session.get(
                "https://www.nseindia.com/option-chain", timeout=12
            )
            if r.status_code == 200:
                self._ready = True
                time.sleep(0.8)
                return True
        except Exception:
            pass
        return False

    def get_expiry_dates(self, index: str) -> list:
        try:
            if self._init_session():
                r = self.session.get(
                    _NSE_API, params={"symbol": index}, timeout=12
                )
                if r.status_code == 200:
                    data = r.json()
                    expiries = data.get("records", {}).get("expiryDates", [])
                    if expiries:
                        return expiries[:5]
        except Exception:
            pass
        return generate_expiry_dates(index, 5)

    def fetch_chain(self, index: str, expiry: str = "") -> tuple:
        """
        Returns (df_chain, spot, is_live).
        Attempts live NSE fetch; falls back to demo data.
        """
        try:
            if self._init_session():
                params = {"symbol": index}
                if expiry:
                    params["date"] = expiry
                r = self.session.get(_NSE_API, params=params, timeout=12)
                if r.status_code == 200:
                    data    = r.json()
                    records = data.get("records", {}).get("data", [])
                    spot    = data.get("records", {}).get("underlyingValue", 0)
                    if records and spot:
                        df = _process_nse_records(records, spot, expiry)
                        if not df.empty:
                            return df, float(spot), True
        except Exception:
            pass

        # ── Demo fallback ──────────────────────────────────────────────────
        spot = _get_spot(index)
        if not expiry:
            expiry = generate_expiry_dates(index, 1)[0]
        df = generate_option_chain(index, spot, expiry)
        return df, spot, False


def _process_nse_records(records: list, spot: float, expiry: str) -> pd.DataFrame:
    """Convert raw NSE JSON records to our standard DataFrame format."""
    from src.analytics.greeks import all_greeks
    from src.config import RISK_FREE_RATE

    rows = []
    for rec in records:
        if "CE" not in rec or "PE" not in rec:
            continue
        strike = rec.get("strikePrice", 0)
        ce = rec.get("CE", {})
        pe = rec.get("PE", {})

        call_iv = ce.get("impliedVolatility", 0) / 100 or 0.15
        put_iv  = pe.get("impliedVolatility",  0) / 100 or 0.15

        try:
            from src.data.generators import _time_to_expiry
            T = _time_to_expiry(expiry)
        except Exception:
            T = 0.02

        cg = all_greeks(spot, strike, T, RISK_FREE_RATE, call_iv, "call")
        pg = all_greeks(spot, strike, T, RISK_FREE_RATE, put_iv,  "put")

        rows.append({
            "strike":      strike,
            "call_oi":     ce.get("openInterest",      0),
            "call_chg_oi": ce.get("changeinOpenInterest", 0),
            "call_volume": ce.get("totalTradedVolume", 0),
            "call_iv":     round(call_iv * 100, 2),
            "call_delta":  round(cg["delta"],  4),
            "call_gamma":  round(cg["gamma"],  6),
            "call_theta":  round(cg["theta"],  2),
            "call_vega":   round(cg["vega"],   2),
            "call_ltp":    ce.get("lastPrice", 0),
            "put_oi":      pe.get("openInterest",      0),
            "put_chg_oi":  pe.get("changeinOpenInterest", 0),
            "put_volume":  pe.get("totalTradedVolume", 0),
            "put_iv":      round(put_iv * 100, 2),
            "put_delta":   round(pg["delta"],  4),
            "put_gamma":   round(pg["gamma"],  6),
            "put_theta":   round(pg["theta"],  2),
            "put_vega":    round(pg["vega"],   2),
            "put_ltp":     pe.get("lastPrice", 0),
            "pcr":         round(pe.get("openInterest", 0) / (ce.get("openInterest", 1) or 1), 3),
            "is_atm":      abs(strike - spot) < 0.6 * (round(spot / 50) * 50 - round(spot / 50 - 1) * 50),
            "is_itm_call": strike < spot,
            "is_itm_put":  strike > spot,
        })

    df = pd.DataFrame(rows)
    return df.sort_values("strike").reset_index(drop=True) if not df.empty else df

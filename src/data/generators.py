"""
data/generators.py — Realistic Indian options market data simulation engine
Produces option chains, OHLCV, PCR history, IV history, and smart money signals.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, List, Dict

from src.config import INDICES, RISK_FREE_RATE
from src.analytics.greeks import all_greeks


# ── Seed for reproducibility within a session ─────────────────────────────────

_RNG = np.random.default_rng(int(datetime.now().strftime("%Y%m%d%H")))


def _get_spot(index: str) -> float:
    """Return a jittered spot price for the current session."""
    base = INDICES[index]["base_price"]
    # Intraday random walk ±0.6%
    pct = _RNG.uniform(-0.006, 0.006)
    return round(base * (1 + pct), 2)


def _time_to_expiry(expiry_date: str) -> float:
    """Convert 'DD-MMM-YYYY' to fractional years."""
    try:
        exp_dt = datetime.strptime(expiry_date, "%d-%b-%Y")
    except ValueError:
        exp_dt = datetime.now() + timedelta(days=7)
    delta = (exp_dt - datetime.now()).total_seconds()
    return max(delta / (365.25 * 24 * 3600), 1 / 365)


def generate_expiry_dates(index: str = "NIFTY", n: int = 5) -> List[str]:
    """Generate next N weekly/monthly expiry Thursdays."""
    today = datetime.now()
    expiries = []
    d = today
    while len(expiries) < n:
        d += timedelta(days=1)
        if d.weekday() == 3:  # Thursday
            expiries.append(d.strftime("%d-%b-%Y").upper())
    return expiries


def generate_ohlcv(spot: float, n_days: int = 30) -> pd.DataFrame:
    """Generate n_days of OHLCV data ending at today."""
    dates = [datetime.now().date() - timedelta(days=n_days - i) for i in range(n_days)]
    prices = [spot]
    for _ in range(n_days - 1):
        prices.insert(0, prices[0] * (1 + _RNG.normal(0, 0.008)))

    rows = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        open_  = close * (1 + _RNG.uniform(-0.005, 0.005))
        high   = max(open_, close) * (1 + abs(_RNG.normal(0, 0.003)))
        low    = min(open_, close) * (1 - abs(_RNG.normal(0, 0.003)))
        volume = int(_RNG.integers(50_000, 500_000))
        rows.append({"date": date, "open": open_, "high": high, "low": low, "close": close, "volume": volume})

    df = pd.DataFrame(rows)
    df["ema9"]   = df["close"].ewm(span=9,   adjust=False).mean()
    df["ema20"]  = df["close"].ewm(span=20,  adjust=False).mean()
    df["vwap"]   = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()
    return df


def generate_option_chain(index: str, spot: float, expiry: str) -> pd.DataFrame:
    """
    Generate a realistic option chain DataFrame with Greeks.
    OI is peaked near ATM with exponential decay on both sides.
    IV smile: higher for OTM options (put skew).
    """
    cfg = INDICES[index]
    step = cfg["strike_step"]
    lot  = cfg["lot_size"]
    T    = _time_to_expiry(expiry)
    r    = RISK_FREE_RATE

    atm = round(spot / step) * step
    strikes = [atm + (i - 12) * step for i in range(25)]  # 25 strikes, ATM in center

    rows = []
    for strike in strikes:
        dist_steps = abs(strike - atm) / step   # 0 = ATM

        # ── IV Smile ──────────────────────────────────────────────────────────
        base_iv = _RNG.uniform(0.13, 0.18)
        skew    = 0.015 * max(0, (atm - strike) / step)   # put skew
        smile   = 0.012 * dist_steps ** 1.4
        call_iv = max(0.06, base_iv + smile)
        put_iv  = max(0.06, base_iv + smile + skew)

        # ── OI distribution: log-normal peaked at ATM ─────────────────────────
        oi_center = 80_000 * lot
        decay     = np.exp(-0.25 * dist_steps)
        call_oi   = max(500, int(_RNG.lognormal(np.log(oi_center * decay + 100), 0.4)))
        put_oi    = max(500, int(_RNG.lognormal(np.log(oi_center * decay * 0.95 + 100), 0.4)))

        # bias: more put OI below ATM, more call OI above ATM
        if strike < atm:
            put_oi  = int(put_oi  * 1.2)
        elif strike > atm:
            call_oi = int(call_oi * 1.15)

        # ── OI change (today's change) ─────────────────────────────────────
        call_chg_oi = int(_RNG.normal(0, call_oi * 0.05))
        put_chg_oi  = int(_RNG.normal(0, put_oi  * 0.05))

        # ── Volume ────────────────────────────────────────────────────────────
        vol_factor  = max(0.05, decay * _RNG.uniform(0.3, 0.8))
        call_volume = int(call_oi * vol_factor)
        put_volume  = int(put_oi  * vol_factor)

        # ── Greeks ────────────────────────────────────────────────────────────
        cg = all_greeks(spot, strike, T, r, call_iv, "call")
        pg = all_greeks(spot, strike, T, r, put_iv,  "put")

        rows.append({
            # Strike
            "strike":        strike,
            # Call side
            "call_oi":       call_oi,
            "call_chg_oi":   call_chg_oi,
            "call_volume":   call_volume,
            "call_iv":       round(call_iv * 100, 2),       # as %
            "call_delta":    round(cg["delta"],  4),
            "call_gamma":    round(cg["gamma"],  6),
            "call_theta":    round(cg["theta"],  2),
            "call_vega":     round(cg["vega"],   2),
            "call_ltp":      round(cg["price"],  2),
            # Put side
            "put_oi":        put_oi,
            "put_chg_oi":    put_chg_oi,
            "put_volume":    put_volume,
            "put_iv":        round(put_iv * 100,  2),
            "put_delta":     round(pg["delta"],   4),
            "put_gamma":     round(pg["gamma"],   6),
            "put_theta":     round(pg["theta"],   2),
            "put_vega":      round(pg["vega"],    2),
            "put_ltp":       round(pg["price"],   2),
            # Derived
            "pcr":           round(put_oi / call_oi, 3) if call_oi else 0,
            "is_atm":        strike == atm,
            "is_itm_call":   strike < atm,
            "is_itm_put":    strike > atm,
        })

    return pd.DataFrame(rows)


def generate_historical_pcr(n_days: int = 30) -> pd.DataFrame:
    """Generate 30-day historical PCR series."""
    dates = [datetime.now().date() - timedelta(days=n_days - i - 1) for i in range(n_days)]
    pcr_vals = []
    pcr = 1.0
    for _ in range(n_days):
        pcr = max(0.4, min(2.0, pcr + _RNG.normal(0, 0.05)))
        pcr_vals.append(round(pcr, 3))
    return pd.DataFrame({"date": dates, "pcr": pcr_vals})


def generate_historical_iv(base_iv: float = 15.0, n_days: int = 365) -> pd.DataFrame:
    """Generate 1-year historical IV for IV Rank / Percentile calculation."""
    dates = [datetime.now().date() - timedelta(days=n_days - i - 1) for i in range(n_days)]
    ivs = []
    iv = base_iv
    for _ in range(n_days):
        iv = max(8.0, min(50.0, iv + _RNG.normal(0, 0.5)))
        ivs.append(round(iv, 2))
    return pd.DataFrame({"date": dates, "iv": ivs})


def generate_max_pain_history(spot: float, n_days: int = 10) -> pd.DataFrame:
    """Generate recent max pain history."""
    dates = [datetime.now().date() - timedelta(days=n_days - i - 1) for i in range(n_days)]
    step  = INDICES.get("NIFTY", {}).get("strike_step", 50)
    pains = []
    pain  = round(spot / step) * step
    for _ in range(n_days):
        pain = pain + _RNG.choice([-step, 0, step])
        pains.append(pain)
    return pd.DataFrame({"date": dates, "max_pain": pains})


def generate_smart_money_alerts(index: str, df_chain: pd.DataFrame) -> List[Dict]:
    """
    Detect unusual OI / volume patterns and generate smart money alerts.
    Returns list of alert dicts.
    """
    alerts = []
    if df_chain.empty:
        return alerts

    total_call_oi = df_chain["call_oi"].sum()
    total_put_oi  = df_chain["put_oi"].sum()

    # Top 3 call OI strikes — potential resistance / call writing
    top_calls = df_chain.nlargest(3, "call_oi")
    for _, row in top_calls.iterrows():
        pct = row["call_oi"] / total_call_oi * 100
        if pct > 12:
            alerts.append({
                "type":    "Heavy Call Writing",
                "icon":    "🔻",
                "strike":  row["strike"],
                "message": f"Heavy Call Writing at {row['strike']:.0f} — {pct:.1f}% of total call OI",
                "severity": "bearish",
            })

    # Top 3 put OI strikes — potential support / put writing
    top_puts = df_chain.nlargest(3, "put_oi")
    for _, row in top_puts.iterrows():
        pct = row["put_oi"] / total_put_oi * 100
        if pct > 12:
            alerts.append({
                "type":    "Heavy Put Writing",
                "icon":    "🚀",
                "strike":  row["strike"],
                "message": f"Heavy Put Writing at {row['strike']:.0f} — {pct:.1f}% of total put OI",
                "severity": "bullish",
            })

    # Unusual volume (volume > 40% of OI)
    df_chain["call_vol_ratio"] = df_chain["call_volume"] / (df_chain["call_oi"] + 1)
    unusual = df_chain[df_chain["call_vol_ratio"] > 0.4].nlargest(2, "call_vol_ratio")
    for _, row in unusual.iterrows():
        alerts.append({
            "type":    "Unusual Volume",
            "icon":    "⚡",
            "strike":  row["strike"],
            "message": f"Unusual Call Volume at {row['strike']:.0f} — Vol/OI ratio {row['call_vol_ratio']:.2f}",
            "severity": "info",
        })

    # OI explosion (positive change > 15% of existing)
    df_chain["call_oi_pct"] = df_chain["call_chg_oi"] / (df_chain["call_oi"] + 1)
    explosions = df_chain[df_chain["call_oi_pct"] > 0.15].nlargest(2, "call_oi_pct")
    for _, row in explosions.iterrows():
        alerts.append({
            "type":    "OI Explosion",
            "icon":    "💥",
            "strike":  row["strike"],
            "message": f"OI Explosion in Calls at {row['strike']:.0f} — +{row['call_oi_pct']*100:.1f}% OI change",
            "severity": "warning",
        })

    return alerts[:8]  # max 8 alerts


def generate_iv_surface(index: str, spot: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate IV surface data: strikes × expiries → IV.
    Returns (strikes_2d, ttes_2d, iv_surface) for 3D plot.
    """
    cfg  = INDICES[index]
    step = cfg["strike_step"]
    atm  = round(spot / step) * step

    strikes  = np.array([atm + (i - 6) * step for i in range(13)])
    ttes     = np.array([7, 14, 21, 30, 45, 60, 90]) / 365  # in years
    base_iv  = 0.15

    iv_surface = np.zeros((len(strikes), len(ttes)))
    for i, s in enumerate(strikes):
        dist = abs(s - atm) / step
        for j, t in enumerate(ttes):
            smile     = 0.012 * dist ** 1.4
            term_str  = 0.005 * np.sqrt(t * 365 / 30)  # term structure
            skew      = 0.01 * max(0, (atm - s) / step)
            iv_surface[i, j] = base_iv + smile + term_str + skew + _RNG.normal(0, 0.003)

    strikes_2d, ttes_2d = np.meshgrid(strikes, ttes, indexing="ij")
    return strikes_2d, ttes_2d * 365, iv_surface  # ttes in days for display


def spot_summary(index: str, spot: float, ohlcv: pd.DataFrame) -> Dict:
    """Compute summary metrics for the dashboard header."""
    if ohlcv.empty:
        return {}
    prev_close = ohlcv.iloc[-2]["close"] if len(ohlcv) >= 2 else spot
    today_row  = ohlcv.iloc[-1]
    change     = spot - prev_close
    change_pct = change / prev_close * 100
    vwap       = today_row["vwap"]
    volume     = int(ohlcv["volume"].iloc[-5:].mean())

    return {
        "spot":       spot,
        "change":     round(change, 2),
        "change_pct": round(change_pct, 2),
        "open":       round(today_row["open"], 2),
        "high":       round(today_row["high"], 2),
        "low":        round(today_row["low"],  2),
        "prev_close": round(prev_close, 2),
        "vwap":       round(vwap, 2),
        "volume":     volume,
    }

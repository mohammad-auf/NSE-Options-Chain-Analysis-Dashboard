"""
analytics/options.py — PCR, Max Pain, Support/Resistance, OI Activity classification,
                        IV Rank/Percentile, and market breadth metrics.
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Dict

from src.config import PCR_BULLISH, PCR_BEARISH


# ── Put-Call Ratio ─────────────────────────────────────────────────────────────

def calculate_pcr(df: pd.DataFrame) -> Tuple[float, str, str]:
    """
    Compute overall PCR and interpretation.
    Returns (pcr_value, interpretation_label, css_class)
    """
    total_call = df["call_oi"].sum()
    total_put  = df["put_oi"].sum()
    if total_call == 0:
        return 0.0, "N/A", "neutral"

    pcr = total_put / total_call

    if pcr > PCR_BULLISH:
        return round(pcr, 3), "Bullish", "bullish"
    elif pcr < PCR_BEARISH:
        return round(pcr, 3), "Bearish", "bearish"
    else:
        return round(pcr, 3), "Neutral", "neutral"


def strike_wise_pcr(df: pd.DataFrame) -> pd.DataFrame:
    """Compute PCR per strike."""
    out = df[["strike", "call_oi", "put_oi"]].copy()
    out["pcr"] = (out["put_oi"] / (out["call_oi"] + 1)).round(3)
    out["pcr_signal"] = out["pcr"].apply(
        lambda x: "Bullish" if x > PCR_BULLISH else ("Bearish" if x < PCR_BEARISH else "Neutral")
    )
    return out


# ── Max Pain ──────────────────────────────────────────────────────────────────

def calculate_max_pain(df: pd.DataFrame) -> Tuple[float, pd.DataFrame]:
    """
    True max pain: for each potential expiry price (every strike),
    compute the total dollar loss to option buyers.
    Max pain = strike where total loss is minimum.
    Returns (max_pain_strike, pain_df)
    """
    strikes = df["strike"].values
    pain_series = []

    for exp_price in strikes:
        call_pain = ((exp_price - strikes) * df["call_oi"].values).clip(min=0).sum()
        put_pain  = ((strikes - exp_price) * df["put_oi"].values).clip(min=0).sum()
        pain_series.append({"strike": exp_price, "total_pain": call_pain + put_pain})

    pain_df = pd.DataFrame(pain_series)
    max_pain = pain_df.loc[pain_df["total_pain"].idxmin(), "strike"]
    return float(max_pain), pain_df


# ── Support & Resistance ──────────────────────────────────────────────────────

def find_support_resistance(df: pd.DataFrame, spot: float) -> List[Dict]:
    """
    Identify top support and resistance levels from OI data.
    Support  = high Put OI strikes below spot.
    Resistance = high Call OI strikes above spot.
    Returns list of level dicts sorted by strength.
    """
    below = df[df["strike"] <= spot].copy()
    above = df[df["strike"] >= spot].copy()

    total_put  = df["put_oi"].sum() + 1
    total_call = df["call_oi"].sum() + 1

    levels = []

    # Top 3 support levels
    for _, row in below.nlargest(3, "put_oi").iterrows():
        strength = min(100, int(row["put_oi"] / total_put * 100 * 5))
        levels.append({
            "type":     "support",
            "strike":   row["strike"],
            "oi":       row["put_oi"],
            "strength": strength,
            "pct_from_spot": round((spot - row["strike"]) / spot * 100, 2),
        })

    # Top 3 resistance levels
    for _, row in above.nlargest(3, "call_oi").iterrows():
        strength = min(100, int(row["call_oi"] / total_call * 100 * 5))
        levels.append({
            "type":     "resistance",
            "strike":   row["strike"],
            "oi":       row["call_oi"],
            "strength": strength,
            "pct_from_spot": round((row["strike"] - spot) / spot * 100, 2),
        })

    return sorted(levels, key=lambda x: -x["strength"])


# ── OI Activity Classification ────────────────────────────────────────────────

def classify_oi_activity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify each strike into OI activity category based on
    price direction vs OI change direction.
    
    Logic (simplified using OI change and LTP proxy):
    +Price +OI → Long Buildup
    -Price +OI → Short Buildup
    +Price -OI → Short Covering
    -Price -OI → Long Unwinding
    
    Since we don't have prev_ltp in demo mode, we use call_chg_oi as proxy.
    """
    out = df[["strike", "call_oi", "call_chg_oi", "call_ltp",
              "put_oi",  "put_chg_oi",  "put_ltp"]].copy()

    def _classify(chg_oi, ltp_proxy):
        # Use sign of chg_oi and ltp as proxy for price direction
        if chg_oi > 0 and ltp_proxy > 0:
            return "Long Buildup"
        elif chg_oi > 0 and ltp_proxy <= 0:
            return "Short Buildup"
        elif chg_oi < 0 and ltp_proxy > 0:
            return "Short Covering"
        else:
            return "Long Unwinding"

    out["call_activity"] = out.apply(
        lambda r: _classify(r["call_chg_oi"], r["call_ltp"]), axis=1
    )
    out["put_activity"] = out.apply(
        lambda r: _classify(r["put_chg_oi"], r["put_ltp"]), axis=1
    )
    return out


def oi_activity_summary(df_activity: pd.DataFrame) -> Dict[str, int]:
    """Count of each OI activity type across all strikes (calls + puts combined)."""
    all_activities = pd.concat([
        df_activity["call_activity"],
        df_activity["put_activity"],
    ])
    return all_activities.value_counts().to_dict()


# ── IV Rank & Percentile ──────────────────────────────────────────────────────

def iv_rank(current_iv: float, iv_history: pd.DataFrame) -> Tuple[float, float]:
    """
    IV Rank: (current - 52w_low) / (52w_high - 52w_low) * 100
    IV Percentile: % of days below current IV in last 252 days
    Returns (iv_rank_pct, iv_percentile_pct)
    """
    ivs = iv_history["iv"].values[-252:]  # last 252 trading days
    if len(ivs) == 0:
        return 50.0, 50.0

    low_52  = ivs.min()
    high_52 = ivs.max()
    rank    = (current_iv - low_52) / (high_52 - low_52) * 100 if high_52 > low_52 else 50.0
    pctile  = (ivs < current_iv).mean() * 100

    return round(float(rank), 1), round(float(pctile), 1)


def realized_volatility(ohlcv: pd.DataFrame, window: int = 20) -> float:
    """
    HV (Historical / Realized Volatility) using log-return std, annualized.
    Returns as percentage.
    """
    if len(ohlcv) < window + 1:
        return 15.0
    log_returns = np.log(ohlcv["close"] / ohlcv["close"].shift(1)).dropna()
    hv = log_returns.iloc[-window:].std() * np.sqrt(252) * 100
    return round(float(hv), 2)


# ── Volatility Cone ───────────────────────────────────────────────────────────

def volatility_cone(ohlcv: pd.DataFrame) -> pd.DataFrame:
    """
    Compute realized volatility at multiple windows (5, 10, 20, 30, 60, 90).
    Returns DataFrame with windows and percentile bands (10th, 25th, 50th, 75th, 90th).
    """
    windows = [5, 10, 20, 30, 60, 90]
    close = ohlcv["close"].values
    rows  = []

    for w in windows:
        if len(close) < w + 20:
            continue
        hvs = []
        for end in range(w + 1, len(close) + 1):
            segment = close[max(0, end - w - 1): end]
            lr = np.log(segment[1:] / segment[:-1])
            hvs.append(lr.std() * np.sqrt(252) * 100)

        hvs = np.array(hvs)
        rows.append({
            "window":  w,
            "p10":     np.percentile(hvs, 10),
            "p25":     np.percentile(hvs, 25),
            "p50":     np.percentile(hvs, 50),
            "p75":     np.percentile(hvs, 75),
            "p90":     np.percentile(hvs, 90),
            "current": hvs[-1],
        })

    return pd.DataFrame(rows)

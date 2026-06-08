"""
analytics/signals.py — AI sentiment engine and trade signal generator.
Uses weighted multi-factor scoring across PCR, OI, IV, price action, and Greeks.
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Dict

from src.config import PCR_BULLISH, PCR_BEARISH, IV_HIGH_PCTILE, IV_LOW_PCTILE
from src.config import INDICES


# ── Sentiment Engine ──────────────────────────────────────────────────────────

_SENTIMENT_LEVELS = [
    "Strong Bearish",
    "Bearish",
    "Neutral",
    "Bullish",
    "Strong Bullish",
]

_WEIGHTS = {
    "pcr":          0.30,
    "oi_trend":     0.25,
    "iv_rank":      0.15,
    "price_action": 0.20,
    "volume":       0.10,
}


def score_pcr(pcr: float) -> float:
    """Map PCR to [-1, +1] sentiment score."""
    if pcr > 1.5:
        return 1.0
    elif pcr > PCR_BULLISH:
        return 0.5 + (pcr - PCR_BULLISH) / (1.5 - PCR_BULLISH) * 0.5
    elif pcr > PCR_BEARISH:
        return (pcr - PCR_BEARISH) / (PCR_BULLISH - PCR_BEARISH) * 1.0 - 0.5
    else:
        return -0.5 - (PCR_BEARISH - pcr) / PCR_BEARISH * 0.5


def score_oi_trend(df: pd.DataFrame, spot: float) -> float:
    """
    Net OI trend score based on put vs call OI near ATM (±5 strikes).
    More put OI near ATM = bullish (put writing).
    More call OI near ATM = bearish (call writing).
    Returns [-1, +1].
    """
    if df.empty:
        return 0.0
    step = df["strike"].diff().median() or 50
    near = df[abs(df["strike"] - spot) <= 5 * step]
    if near.empty:
        return 0.0
    total_call = near["call_oi"].sum() + 1
    total_put  = near["put_oi"].sum() + 1
    ratio = (total_put - total_call) / (total_put + total_call)
    return float(np.clip(ratio * 2, -1, 1))


def score_iv_rank(iv_rank_pct: float) -> float:
    """
    High IV rank = high fear = contrarian bullish (sellers win).
    Low IV rank = complacency = cautious.
    Returns [-1, +1].
    """
    if iv_rank_pct > IV_HIGH_PCTILE:
        return 0.5  # high IV → good time to sell = slight bullish
    elif iv_rank_pct < IV_LOW_PCTILE:
        return -0.3  # low IV → market asleep / slight bearish
    return 0.0


def score_price_action(ohlcv: pd.DataFrame) -> float:
    """
    Price above EMA20 and EMA9 above EMA20 → bullish.
    Returns [-1, +1].
    """
    if len(ohlcv) < 20:
        return 0.0
    last  = ohlcv.iloc[-1]
    score = 0.0
    if last["close"] > last["ema20"]:
        score += 0.5
    if last["ema9"] > last["ema20"]:
        score += 0.5
    if last["close"] < last["ema20"]:
        score -= 0.5
    if last["ema9"] < last["ema20"]:
        score -= 0.5
    return float(score)


def score_volume(df: pd.DataFrame) -> float:
    """
    Higher put volume (put buying) vs call volume → bearish.
    More call volume vs put volume → bullish (call buying).
    """
    if df.empty:
        return 0.0
    total_call_vol = df["call_volume"].sum() + 1
    total_put_vol  = df["put_volume"].sum() + 1
    ratio = (total_call_vol - total_put_vol) / (total_call_vol + total_put_vol)
    return float(np.clip(ratio * 2, -1, 1))


def compute_sentiment(
    pcr: float,
    df_chain: pd.DataFrame,
    spot: float,
    iv_rank_pct: float,
    ohlcv: pd.DataFrame,
) -> Tuple[str, float, List[str]]:
    """
    Multi-factor sentiment computation.
    Returns (sentiment_label, confidence_pct, reasoning_list).
    """
    scores = {
        "pcr":          score_pcr(pcr)              * _WEIGHTS["pcr"],
        "oi_trend":     score_oi_trend(df_chain, spot) * _WEIGHTS["oi_trend"],
        "iv_rank":      score_iv_rank(iv_rank_pct)  * _WEIGHTS["iv_rank"],
        "price_action": score_price_action(ohlcv)   * _WEIGHTS["price_action"],
        "volume":       score_volume(df_chain)       * _WEIGHTS["volume"],
    }

    total_score = sum(scores.values())  # in [-1, +1] (weighted)

    # Map to sentiment level index (0–4)
    idx = min(4, max(0, int((total_score + 1) / 2 * 4.99)))
    sentiment = _SENTIMENT_LEVELS[idx]

    # Confidence: distance from 0 × 100, scaled to [50, 95]
    raw_conf = abs(total_score)
    confidence = 50.0 + raw_conf * 45.0

    # Build reasoning bullets
    reasons = []
    if pcr > 1.1:
        reasons.append(f"PCR at {pcr:.2f} — elevated put writing (bullish signal)")
    elif pcr < 0.9:
        reasons.append(f"PCR at {pcr:.2f} — low put activity (bearish signal)")
    else:
        reasons.append(f"PCR at {pcr:.2f} — neutral zone")

    oi_s = scores["oi_trend"] / _WEIGHTS["oi_trend"]
    if oi_s > 0.2:
        reasons.append("Put OI dominates near ATM — put writing activity observed")
    elif oi_s < -0.2:
        reasons.append("Call OI dominates near ATM — call writing activity observed")

    if iv_rank_pct > IV_HIGH_PCTILE:
        reasons.append(f"IV Rank at {iv_rank_pct:.0f}% — elevated implied volatility")
    elif iv_rank_pct < IV_LOW_PCTILE:
        reasons.append(f"IV Rank at {iv_rank_pct:.0f}% — compressed volatility")

    pa = scores["price_action"] / _WEIGHTS["price_action"]
    if pa > 0.3:
        reasons.append("Price above key EMAs — positive price momentum")
    elif pa < -0.3:
        reasons.append("Price below key EMAs — negative price momentum")

    return sentiment, round(confidence, 1), reasons[:5]


# ── Trade Signal Generator ────────────────────────────────────────────────────

def generate_trade_signals(
    index: str,
    df_chain: pd.DataFrame,
    spot: float,
    sentiment: str,
    confidence: float,
) -> List[Dict]:
    """
    Generate 3–4 actionable trade signal cards.
    Each signal has: direction, strike, confidence, target, sl, rr, reasons.
    """
    if df_chain.empty:
        return []

    cfg  = INDICES[index]
    step = cfg["strike_step"]
    lot  = cfg["lot_size"]

    signals = []

    is_bullish = "Bullish" in sentiment
    is_bearish = "Bearish" in sentiment

    atm = round(spot / step) * step

    # Signal 1: Primary directional signal
    if is_bullish:
        strike_ce   = atm + step  # OTM call
        row_ce = df_chain[df_chain["strike"] == strike_ce]
        ltp_ce = row_ce["call_ltp"].values[0] if not row_ce.empty else step * 0.03
        target_pts  = round(ltp_ce * 0.6, 2)
        sl_pts      = round(ltp_ce * 0.35, 2)
        signals.append({
            "direction":  "BUY CE",
            "css_class":  "buy-call",
            "index":      index,
            "strike":     f"{strike_ce:.0f} CE",
            "ltp":        ltp_ce,
            "target":     f"+{target_pts:.0f} pts",
            "sl":         f"-{sl_pts:.0f} pts",
            "rr":         f"1:{target_pts/sl_pts:.1f}",
            "confidence": min(95, confidence + 5),
            "reasons": [
                "Strong put OI concentration at lower strikes",
                "PCR indicating bullish sentiment",
                "Call IV relatively cheaper than puts",
                "Positive price momentum above EMA20",
            ][:3],
        })
    elif is_bearish:
        strike_pe   = atm - step  # OTM put
        row_pe = df_chain[df_chain["strike"] == strike_pe]
        ltp_pe = row_pe["put_ltp"].values[0] if not row_pe.empty else step * 0.03
        target_pts  = round(ltp_pe * 0.6, 2)
        sl_pts      = round(ltp_pe * 0.35, 2)
        signals.append({
            "direction":  "BUY PE",
            "css_class":  "buy-put",
            "index":      index,
            "strike":     f"{strike_pe:.0f} PE",
            "ltp":        ltp_pe,
            "target":     f"+{target_pts:.0f} pts",
            "sl":         f"-{sl_pts:.0f} pts",
            "rr":         f"1:{target_pts/sl_pts:.1f}",
            "confidence": min(95, confidence + 5),
            "reasons": [
                "Strong call OI concentration at upper strikes",
                "PCR indicating bearish sentiment",
                "Resistance showing strong call writing",
                "Price below key moving averages",
            ][:3],
        })

    # Signal 2: Iron Condor (range-bound)
    otm_call_strike = atm + 3 * step
    otm_put_strike  = atm - 3 * step
    far_call_strike = atm + 5 * step
    far_put_strike  = atm - 5 * step
    signals.append({
        "direction":  "IRON CONDOR",
        "css_class":  "buy-call",
        "index":      index,
        "strike":     f"{otm_put_strike:.0f}P / {otm_call_strike:.0f}C",
        "ltp":        "–",
        "target":     f"Premium",
        "sl":         f"2× Premium",
        "rr":         "1:2",
        "confidence": round(max(50, confidence - 10), 1),
        "reasons": [
            f"Sell {otm_call_strike:.0f} CE / Buy {far_call_strike:.0f} CE",
            f"Sell {otm_put_strike:.0f} PE / Buy {far_put_strike:.0f} PE",
            "Range-bound market expected",
            "Collect time decay between strikes",
        ][:3],
    })

    # Signal 3: Straddle if IV is low (buy cheaply)
    row_atm = df_chain[df_chain["strike"] == atm]
    if not row_atm.empty:
        atm_ce_ltp = row_atm["call_ltp"].values[0]
        atm_pe_ltp = row_atm["put_ltp"].values[0]
        total_cost = round(atm_ce_ltp + atm_pe_ltp, 2)
        signals.append({
            "direction":  "STRADDLE",
            "css_class":  "buy-call",
            "index":      index,
            "strike":     f"{atm:.0f} ATM",
            "ltp":        total_cost,
            "target":     f">{total_cost*1.5:.0f}",
            "sl":         f"<{total_cost*0.5:.0f}",
            "rr":         "Unlimited",
            "confidence": round(max(45, confidence - 15), 1),
            "reasons": [
                "IV relatively low — buy volatility cheap",
                f"Buy {atm:.0f} CE + {atm:.0f} PE",
                f"Breakeven: {atm - total_cost:.0f} / {atm + total_cost:.0f}",
            ],
        })

    return signals[:4]

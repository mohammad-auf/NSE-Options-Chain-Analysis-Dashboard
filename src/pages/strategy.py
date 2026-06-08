"""
pages/strategy.py — Options Strategy Builder with interactive payoff diagrams.
Supports: Long Call, Long Put, Bull Call Spread, Bear Put Spread,
          Iron Condor, Iron Fly, Straddle, Strangle.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

from src.config import COLORS, PLOTLY_TEMPLATE, STRATEGIES, INDICES, plotly_layout
from src.styles import section_header
from src.analytics.greeks import bs_price


def _payoff(strategy: str, spot_range: np.ndarray, spot: float, step: int,
            params: dict) -> np.ndarray:
    """Compute P&L at expiry for each underlying price in spot_range."""
    S = spot_range

    if strategy == "Long Call":
        K, prem = params["K1"], params["prem1"]
        return np.maximum(S - K, 0) - prem

    elif strategy == "Long Put":
        K, prem = params["K1"], params["prem1"]
        return np.maximum(K - S, 0) - prem

    elif strategy == "Bull Call Spread":
        K1, p1 = params["K1"], params["prem1"]
        K2, p2 = params["K2"], params["prem2"]
        return np.maximum(S - K1, 0) - p1 - np.maximum(S - K2, 0) + p2

    elif strategy == "Bear Put Spread":
        K1, p1 = params["K1"], params["prem1"]
        K2, p2 = params["K2"], params["prem2"]
        # Buy K2 put (higher), sell K1 put (lower)
        return np.maximum(K2 - S, 0) - p2 - np.maximum(K1 - S, 0) + p1

    elif strategy == "Straddle":
        K, pc, pp = params["K1"], params["prem1"], params["prem2"]
        return np.maximum(S - K, 0) + np.maximum(K - S, 0) - pc - pp

    elif strategy == "Strangle":
        Kc, pc = params["K1"], params["prem1"]
        Kp, pp = params["K2"], params["prem2"]
        return np.maximum(S - Kc, 0) + np.maximum(Kp - S, 0) - pc - pp

    elif strategy == "Iron Condor":
        Kp1, pp1 = params["K1"], params["prem1"]   # buy put (lower)
        Kp2, pp2 = params["K2"], params["prem2"]   # sell put
        Kc1, pc1 = params["K3"], params["prem3"]   # sell call
        Kc2, pc2 = params["K4"], params["prem4"]   # buy call (higher)
        # Net credit: pp2 + pc1 - pp1 - pc2
        put_spread  = np.maximum(Kp2 - S, 0) - np.maximum(Kp1 - S, 0)
        call_spread = np.maximum(S - Kc1, 0) - np.maximum(S - Kc2, 0)
        net_credit  = pp2 + pc1 - pp1 - pc2
        return net_credit - put_spread - call_spread

    elif strategy == "Iron Fly":
        Kp,  pp  = params["K1"], params["prem1"]   # buy OTM put
        Katm, pc = params["K2"], params["prem2"]   # sell ATM call+put (combined)
        Kc,  pc2 = params["K3"], params["prem3"]   # buy OTM call
        net_credit = pc - pp - pc2
        put_spread  = np.maximum(Katm - S, 0) - np.maximum(Kp - S, 0)
        call_spread = np.maximum(S - Katm, 0) - np.maximum(S - Kc, 0)
        return net_credit - put_spread - call_spread

    return np.zeros_like(S)


def _strategy_metrics(pnl: np.ndarray, spot_range: np.ndarray) -> dict:
    """Compute max profit, max loss, breakevens, pop."""
    max_profit  = float(pnl.max())
    max_loss    = float(pnl.min())

    # Breakeven: where PnL crosses 0
    breakevens = []
    for i in range(len(pnl) - 1):
        if pnl[i] * pnl[i + 1] < 0:
            x0, x1 = spot_range[i], spot_range[i + 1]
            y0, y1 = pnl[i], pnl[i + 1]
            be = x0 - y0 * (x1 - x0) / (y1 - y0)
            breakevens.append(round(float(be), 2))

    pop = float((pnl >= 0).mean() * 100)

    return {
        "max_profit": max_profit,
        "max_loss":   max_loss,
        "breakevens": breakevens,
        "pop":        pop,
    }


def render(index: str, spot: float, df_chain: pd.DataFrame):
    """Render the Strategy Builder page."""

    st.markdown(section_header("STRATEGY BUILDER", "Interactive Payoff Analyzer"), unsafe_allow_html=True)

    cfg  = INDICES[index]
    step = cfg["strike_step"]
    atm  = round(spot / step) * step
    T    = 0.04  # ~15 days to expiry (typical)
    r    = 0.065

    # ── Strategy selector ─────────────────────────────────────────────────────
    col_strat, col_leg = st.columns([1, 2])
    with col_strat:
        strategy = st.selectbox("📐 Select Strategy", STRATEGIES)

    # ── Build leg selectors ───────────────────────────────────────────────────
    params = {}
    available_strikes = sorted(df_chain["strike"].values.tolist())

    def _get_ltp(strike: float, opt: str) -> float:
        row = df_chain[df_chain["strike"] == strike]
        if row.empty:
            return bs_price(spot, strike, T, r, 0.15, opt)
        return float(row[f"{opt}_ltp"].values[0]) or bs_price(spot, strike, T, r, 0.15, opt)

    def _strike_selector(label: str, default: float, key: str) -> float:
        closest = min(available_strikes, key=lambda x: abs(x - default))
        idx     = available_strikes.index(closest)
        return st.selectbox(label, available_strikes, index=idx, key=key)

    with col_leg:
        if strategy == "Long Call":
            K1 = _strike_selector("Call Strike (Buy)", atm + step, "k1")
            p1 = _get_ltp(K1, "call")
            params = {"K1": K1, "prem1": p1}
            st.caption(f"Premium: ₹{p1:.2f}  |  Cost: ₹{p1 * cfg['lot_size']:,.0f}")

        elif strategy == "Long Put":
            K1 = _strike_selector("Put Strike (Buy)", atm - step, "k1")
            p1 = _get_ltp(K1, "put")
            params = {"K1": K1, "prem1": p1}
            st.caption(f"Premium: ₹{p1:.2f}  |  Cost: ₹{p1 * cfg['lot_size']:,.0f}")

        elif strategy == "Bull Call Spread":
            c1, c2 = st.columns(2)
            with c1: K1 = _strike_selector("Buy Call Strike", atm,        "k1")
            with c2: K2 = _strike_selector("Sell Call Strike", atm + step * 2, "k2")
            p1, p2 = _get_ltp(K1, "call"), _get_ltp(K2, "call")
            params = {"K1": K1, "prem1": p1, "K2": K2, "prem2": p2}
            st.caption(f"Net Debit: ₹{p1 - p2:.2f}  |  Max Profit: {K2 - K1 - p1 + p2:.2f}")

        elif strategy == "Bear Put Spread":
            c1, c2 = st.columns(2)
            with c1: K2 = _strike_selector("Buy Put Strike (High)", atm,        "k2")
            with c2: K1 = _strike_selector("Sell Put Strike (Low)", atm - step * 2, "k1")
            p1, p2 = _get_ltp(K1, "put"), _get_ltp(K2, "put")
            params = {"K1": K1, "prem1": p1, "K2": K2, "prem2": p2}
            st.caption(f"Net Debit: ₹{p2 - p1:.2f}  |  Max Profit: {K2 - K1 - p2 + p1:.2f}")

        elif strategy == "Straddle":
            K1 = _strike_selector("ATM Strike", atm, "k1")
            p1 = _get_ltp(K1, "call")
            p2 = _get_ltp(K1, "put")
            params = {"K1": K1, "prem1": p1, "prem2": p2}
            st.caption(f"Total Premium: ₹{p1+p2:.2f}  |  Breakeven: ±{p1+p2:.2f} pts")

        elif strategy == "Strangle":
            c1, c2 = st.columns(2)
            with c1: Kc = _strike_selector("OTM Call Strike", atm + step * 2, "k1")
            with c2: Kp = _strike_selector("OTM Put Strike",  atm - step * 2, "k2")
            pc = _get_ltp(Kc, "call")
            pp = _get_ltp(Kp, "put")
            params = {"K1": Kc, "prem1": pc, "K2": Kp, "prem2": pp}
            st.caption(f"Total Premium: ₹{pc+pp:.2f}")

        elif strategy == "Iron Condor":
            c1, c2, c3, c4 = st.columns(4)
            with c1: K1 = _strike_selector("Buy Put (low)",   atm - step * 4, "k1")
            with c2: K2 = _strike_selector("Sell Put",        atm - step * 2, "k2")
            with c3: K3 = _strike_selector("Sell Call",       atm + step * 2, "k3")
            with c4: K4 = _strike_selector("Buy Call (high)", atm + step * 4, "k4")
            pp1, pp2 = _get_ltp(K1, "put"), _get_ltp(K2, "put")
            pc1, pc2 = _get_ltp(K3, "call"), _get_ltp(K4, "call")
            params = {"K1": K1, "prem1": pp1, "K2": K2, "prem2": pp2,
                      "K3": K3, "prem3": pc1, "K4": K4, "prem4": pc2}
            net_cr = pp2 + pc1 - pp1 - pc2
            st.caption(f"Net Credit: ₹{net_cr:.2f}  |  Max Profit: ₹{net_cr:.2f}")

        elif strategy == "Iron Fly":
            c1, c2, c3 = st.columns(3)
            with c1: K1 = _strike_selector("Buy OTM Put",  atm - step * 3, "k1")
            with c2: K2 = _strike_selector("Sell ATM",     atm,             "k2")
            with c3: K3 = _strike_selector("Buy OTM Call", atm + step * 3, "k3")
            pp  = _get_ltp(K1, "put")
            atm_credit = _get_ltp(K2, "call") + _get_ltp(K2, "put")
            pc2 = _get_ltp(K3, "call")
            params = {"K1": K1, "prem1": pp, "K2": K2, "prem2": atm_credit, "K3": K3, "prem3": pc2}
            st.caption(f"Net Credit: ₹{atm_credit - pp - pc2:.2f}")

    # ── Compute payoff ────────────────────────────────────────────────────────
    if params:
        n_pts     = 300
        spot_range = np.linspace(spot * 0.85, spot * 1.15, n_pts)
        pnl        = _payoff(strategy, spot_range, spot, step, params)
        metrics    = _strategy_metrics(pnl, spot_range)

        # ── Metrics row ───────────────────────────────────────────────────────
        m1, m2, m3, m4, m5 = st.columns(5)
        mp  = metrics["max_profit"]
        ml  = metrics["max_loss"]
        bes = metrics["breakevens"]
        pop = metrics["pop"]
        rr  = abs(mp / ml) if ml != 0 else float("inf")

        be_str = " / ".join(f"{b:,.2f}" for b in bes[:2]) if bes else "N/A"

        for col, lbl, val, color in [
            (m1, "MAX PROFIT",  f"₹{mp:+,.1f}" if mp < 1e8 else "Unlimited",   COLORS["bullish"]),
            (m2, "MAX LOSS",    f"₹{ml:+,.1f}",                                  COLORS["bearish"]),
            (m3, "BREAKEVEN",   be_str,                                           COLORS["neutral"]),
            (m4, "RISK : REWARD", f"1 : {rr:.2f}" if rr < 999 else "Unlimited", COLORS["info"]),
            (m5, "PROB OF PROFIT", f"{pop:.1f}%",                                COLORS["purple"]),
        ]:
            with col:
                st.markdown(f"""
                <div class="strategy-metric">
                    <div class="s-label">{lbl}</div>
                    <div class="s-value" style="color:{color}">{val}</div>
                </div>
                """, unsafe_allow_html=True)

        # ── Payoff chart ──────────────────────────────────────────────────────
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        pnl_colors = [COLORS["bullish"] if p >= 0 else COLORS["bearish"] for p in pnl]

        fig = go.Figure()
        # Profit zone fill
        fig.add_trace(go.Scatter(
            x=spot_range, y=np.maximum(pnl, 0),
            mode="none", fill="tozeroy",
            fillcolor="rgba(0,230,118,0.08)",
            showlegend=False,
        ))
        # Loss zone fill
        fig.add_trace(go.Scatter(
            x=spot_range, y=np.minimum(pnl, 0),
            mode="none", fill="tozeroy",
            fillcolor="rgba(255,68,68,0.08)",
            showlegend=False,
        ))
        # P&L line
        fig.add_trace(go.Scatter(
            x=spot_range, y=pnl,
            mode="lines",
            name="P&L at Expiry",
            line=dict(color=COLORS["info"], width=2.5),
            hovertemplate="Spot: %{x:,.2f}<br>P&L: ₹%{y:+,.2f}<extra></extra>",
        ))
        # Breakeven verticals
        for be in bes:
            fig.add_vline(x=be, line_color="rgba(255,214,0,0.5)", line_dash="dash",
                          annotation_text=f"BE: {be:,.0f}", annotation_font_color="#FFD600")
        # Current spot
        fig.add_vline(x=spot, line_color=COLORS["info"], line_dash="dot", line_width=1.5,
                      annotation_text=f"Spot: {spot:,.2f}", annotation_font_color=COLORS["info"])
        # Zero line
        fig.add_hline(y=0, line_color="rgba(255,255,255,0.2)", line_width=1)

        fig.update_layout(
            **plotly_layout(
                height=400,
                title=f"{strategy} — Payoff at Expiry ({INDICES[index]['display']})",
                xaxis_title="Underlying Price at Expiry",
                yaxis_title="Profit / Loss (₹)",
            )
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # ── Strategy description ───────────────────────────────────────────────
        descriptions = {
            "Long Call":       "Bullish bet. Profit when underlying rises above breakeven. Limited loss (premium paid), unlimited profit.",
            "Long Put":        "Bearish bet. Profit when underlying falls below breakeven. Limited loss (premium paid), capped profit.",
            "Bull Call Spread": "Moderately bullish. Buy lower call, sell higher call. Reduces cost, caps profit at spread width.",
            "Bear Put Spread":  "Moderately bearish. Buy higher put, sell lower put. Reduces cost, profit capped.",
            "Straddle":        "Volatility bet. Buy ATM call + put. Profit from large move in either direction. Time decay is enemy.",
            "Strangle":        "Volatility bet. Cheaper than straddle. Buy OTM call + OTM put. Requires larger underlying move.",
            "Iron Condor":     "Range-bound strategy. Sell OTM call + put spreads. Profit from time decay when market stays within range.",
            "Iron Fly":        "High probability range strategy. Sell ATM call + put, hedge with OTM options. Max profit at ATM at expiry.",
        }
        st.info(f"📖 **{strategy}:** {descriptions.get(strategy, '')}")

"""
pages/dashboard.py — Main dashboard: KPI cards, market overview, S/R, sentiment summary
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime

from src.config import COLORS, PLOTLY_TEMPLATE, INDICES, plotly_layout
from src.styles import kpi_card, section_header, sentiment_html
from src.analytics.options import calculate_pcr, calculate_max_pain, find_support_resistance, iv_rank, realized_volatility
from src.analytics.signals import compute_sentiment


def _fmt(val, decimals=2, prefix="", suffix=""):
    try:
        return f"{prefix}{val:,.{decimals}f}{suffix}"
    except Exception:
        return str(val)


def _sparkline(values, color="#00D4FF"):
    """Mini sparkline figure."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=values, mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy",
        fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.08)",
    ))
    fig.update_layout(
        height=60, margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    return fig


def render(index: str, spot: float, df_chain: pd.DataFrame,
           ohlcv: pd.DataFrame, is_live: bool, iv_history: pd.DataFrame):
    """Render the Dashboard page."""

    # ── Summary metrics ───────────────────────────────────────────────────────
    prev_close = ohlcv.iloc[-2]["close"] if len(ohlcv) >= 2 else spot
    change     = spot - prev_close
    change_pct = change / prev_close * 100 if prev_close else 0
    today      = ohlcv.iloc[-1] if not ohlcv.empty else None

    open_  = today["open"]  if today is not None else spot
    high   = today["high"]  if today is not None else spot
    low    = today["low"]   if today is not None else spot
    vwap   = today["vwap"]  if today is not None else spot
    volume = today["volume"] if today is not None else 0

    pcr_val, pcr_label, pcr_class = calculate_pcr(df_chain)
    max_pain_strike, _ = calculate_max_pain(df_chain)

    current_iv  = df_chain["call_iv"].median() if not df_chain.empty else 15.0
    iv_rank_pct, iv_pctile = iv_rank(current_iv, iv_history)
    hv          = realized_volatility(ohlcv)

    sentiment, conf, reasons = compute_sentiment(pcr_val, df_chain, spot, iv_rank_pct, ohlcv)

    # ── Color coding ──────────────────────────────────────────────────────────
    bull_color = COLORS["bullish"]
    bear_color = COLORS["bearish"]
    chg_color  = bull_color if change >= 0 else bear_color
    chg_sign   = "+" if change >= 0 else ""

    # ── Live / Demo badge ─────────────────────────────────────────────────────
    badge_html = """<span class="live-tag"><span class="live-dot"></span>LIVE</span>""" if is_live else \
                 """<span class="demo-tag">⚙ DEMO</span>"""

    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:24px">
        <div>
            <div class="dashboard-title">📊 {INDICES[index]['display']} Intelligence</div>
            <div class="dashboard-subtitle">Options Analytics Terminal</div>
        </div>
        <div style="display:flex;align-items:center;gap:12px">
            {badge_html}
            <div style="font-size:11px;color:#4A5568;font-family:'JetBrains Mono',monospace">
                {datetime.now().strftime('%d %b %Y  %H:%M:%S')}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI CARDS row 1 (5 cards) ─────────────────────────────────────────────
    st.markdown(section_header("MARKET OVERVIEW", "Real-Time"), unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    cards = [
        (c1, "SPOT PRICE",    _fmt(spot, 2),      "",                                  "💹", "info"),
        (c2, "DAY CHANGE",    f"{chg_sign}{_fmt(change, 2)}", f"{chg_sign}{change_pct:.2f}%", "📈" if change >= 0 else "📉", "bullish" if change >= 0 else "bearish"),
        (c3, "OPEN",          _fmt(open_, 2),     "",                                  "🔓", "info"),
        (c4, "HIGH",          _fmt(high, 2),      "",                                  "⬆️", "bullish"),
        (c5, "LOW",           _fmt(low,  2),      "",                                  "⬇️", "bearish"),
    ]
    for col, lbl, val, delta, icon, cls in cards:
        with col:
            delta_color = bull_color if "+" in str(delta) else (bear_color if "-" in str(delta) else "")
            st.markdown(kpi_card(lbl, val, delta, delta_color, icon, cls), unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── KPI CARDS row 2 (5 cards) ─────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    pcr_color  = bull_color if pcr_class == "bullish" else (bear_color if pcr_class == "bearish" else COLORS["neutral"])
    cards2 = [
        (c1, "VWAP",       _fmt(vwap,             2), "", "📊", "info"),
        (c2, "VOLUME",     f"{volume:,}",             "", "📦", "info"),
        (c3, "PCR",        _fmt(pcr_val,          3), pcr_label, "⚖️", pcr_class),
        (c4, "MAX PAIN",   _fmt(max_pain_strike,  0), f"Dist: {abs(spot - max_pain_strike):.0f}", "🎯", "neutral"),
        (c5, "IV RANK",    f"{iv_rank_pct:.1f}%",     f"Pctile: {iv_pctile:.0f}%", "🌡️", "warning" if iv_rank_pct > 70 else "info"),
    ]
    for col, lbl, val, delta, icon, cls in cards2:
        with col:
            delta_color = ""
            if pcr_class == "bullish" and lbl == "PCR":
                delta_color = bull_color
            elif pcr_class == "bearish" and lbl == "PCR":
                delta_color = bear_color
            st.markdown(kpi_card(lbl, val, delta, delta_color, icon, cls), unsafe_allow_html=True)

    # ── SENTIMENT + SUPPORT/RESISTANCE ────────────────────────────────────────
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    left_col, right_col = st.columns([3, 2])

    with left_col:
        st.markdown(section_header("AI MARKET SENTIMENT"), unsafe_allow_html=True)
        st.markdown(sentiment_html(sentiment, conf, reasons), unsafe_allow_html=True)

        # Price sparkline
        st.markdown(section_header("PRICE TREND", "30 Days"), unsafe_allow_html=True)
        if not ohlcv.empty:
            close_vals = ohlcv["close"].values
            fig_spark  = go.Figure()
            fig_spark.add_trace(go.Scatter(
                x=ohlcv["date"].astype(str),
                y=close_vals,
                mode="lines",
                name="Close",
                line=dict(color="#00D4FF", width=2),
                fill="tozeroy",
                fillcolor="rgba(0,212,255,0.06)",
            ))
            fig_spark.add_trace(go.Scatter(
                x=ohlcv["date"].astype(str),
                y=ohlcv["ema20"].values,
                mode="lines",
                name="EMA 20",
                line=dict(color="#FFD600", width=1.5, dash="dot"),
            ))
            fig_spark.update_layout(
                **plotly_layout(
                    height=200,
                    margin=dict(l=40, r=10, t=10, b=30),
                    showlegend=True,
                    xaxis=dict(showticklabels=False),
                )
            )
            st.plotly_chart(fig_spark, use_container_width=True, config={"displayModeBar": False})

    with right_col:
        # Support & Resistance
        st.markdown(section_header("SUPPORT & RESISTANCE"), unsafe_allow_html=True)
        levels = find_support_resistance(df_chain, spot)
        for lv in levels[:6]:
            typ     = lv["type"]
            color   = COLORS["bullish"] if typ == "support" else COLORS["bearish"]
            label   = "SUPPORT" if typ == "support" else "RESIST."
            str_pct = lv["strength"]
            pct_str = f"{lv['pct_from_spot']:.2f}%"
            bar_w   = str_pct
            st.markdown(f"""
            <div class="sr-level {typ}">
                <div class="sr-label {typ}">{label}</div>
                <div class="sr-price">{lv['strike']:,.0f}</div>
                <div>
                    <div class="sr-strength-bar">
                        <div class="sr-strength-fill {typ}" style="width:{bar_w}%"></div>
                    </div>
                    <div class="sr-pct">{pct_str} away</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # IV summary
        st.markdown(section_header("VOLATILITY SNAPSHOT"), unsafe_allow_html=True)
        v1, v2 = st.columns(2)
        with v1:
            st.metric("IV (ATM)", f"{current_iv:.1f}%", delta=f"HV: {hv:.1f}%")
        with v2:
            st.metric("IV Rank", f"{iv_rank_pct:.0f}%", delta=f"{iv_pctile:.0f}th pctile")

    # ── OI OVERVIEW MINI CHART ────────────────────────────────────────────────
    st.markdown(section_header("OPEN INTEREST SNAPSHOT", "Top 12 Strikes"), unsafe_allow_html=True)

    if not df_chain.empty:
        top_df = df_chain.nlargest(12, "call_oi").sort_values("strike")
        fig_oi = go.Figure()
        fig_oi.add_trace(go.Bar(
            x=top_df["strike"].astype(str),
            y=top_df["call_oi"],
            name="Call OI",
            marker=dict(color=COLORS["bullish"], opacity=0.85),
        ))
        fig_oi.add_trace(go.Bar(
            x=top_df["strike"].astype(str),
            y=top_df["put_oi"],
            name="Put OI",
            marker=dict(color=COLORS["bearish"], opacity=0.85),
        ))
        fig_oi.update_layout(
            **plotly_layout(
                height=260,
                margin=dict(l=50, r=10, t=10, b=50),
                barmode="group",
                xaxis_title="Strike",
                yaxis_title="Open Interest",
            )
        )
        st.plotly_chart(fig_oi, use_container_width=True, config={"displayModeBar": False})

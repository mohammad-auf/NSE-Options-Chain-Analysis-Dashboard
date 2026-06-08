"""
pages/ai_signals.py — AI sentiment engine display, trade signal cards, smart money alerts.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from src.config import COLORS, PLOTLY_TEMPLATE, INDICES
from src.styles import section_header, sentiment_html
from src.analytics.options import calculate_pcr, iv_rank
from src.analytics.signals import compute_sentiment, generate_trade_signals, score_pcr, score_oi_trend, score_price_action, score_volume, score_iv_rank
from src.data.generators import generate_smart_money_alerts


_SIGNAL_TYPE_COLORS = {
    "BUY CE":      (COLORS["bullish"], "buy-call"),
    "BUY PE":      (COLORS["bearish"], "buy-put"),
    "IRON CONDOR": (COLORS["info"],    "buy-call"),
    "STRADDLE":    (COLORS["purple"],  "buy-call"),
}


def _factor_bar(label: str, score: float, color: str):
    """Render a horizontal factor score bar."""
    pct = int((score + 1) / 2 * 100)  # map [-1,1] to [0,100]
    bar_color = COLORS["bullish"] if score > 0.1 else (COLORS["bearish"] if score < -0.1 else COLORS["neutral"])
    return f"""
    <div style="margin-bottom:10px">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px">
            <span style="font-size:12px;color:#8892A4;font-weight:500">{label}</span>
            <span style="font-size:12px;color:{bar_color};font-weight:700;font-family:'JetBrains Mono',monospace">
                {"+" if score > 0 else ""}{score:.2f}
            </span>
        </div>
        <div style="height:6px;border-radius:3px;background:rgba(255,255,255,0.06);overflow:hidden">
            <div style="height:100%;width:{pct}%;background:{bar_color};border-radius:3px;
                        transition:width 0.8s ease"></div>
        </div>
    </div>
    """


def render(index: str, spot: float, df_chain: pd.DataFrame,
           ohlcv: pd.DataFrame, iv_history: pd.DataFrame):
    """Render the AI Signals page."""

    st.markdown(section_header("AI INTELLIGENCE CENTER", "Multi-Factor Analysis"), unsafe_allow_html=True)

    if df_chain.empty:
        st.warning("No data available for AI analysis.")
        return

    # Compute all scores
    pcr_val, pcr_label, pcr_class = calculate_pcr(df_chain)
    current_iv = df_chain["call_iv"].median()
    iv_rank_pct, _ = iv_rank(current_iv, iv_history)
    sentiment, conf, reasons = compute_sentiment(pcr_val, df_chain, spot, iv_rank_pct, ohlcv)

    # ── SENTIMENT BANNER ──────────────────────────────────────────────────────
    st.markdown(sentiment_html(sentiment, conf, reasons), unsafe_allow_html=True)

    # ── FACTOR BREAKDOWN ──────────────────────────────────────────────────────
    col_factors, col_signals = st.columns([1, 2])

    with col_factors:
        st.markdown(section_header("FACTOR BREAKDOWN"), unsafe_allow_html=True)
        factors = {
            "PCR Analysis":      score_pcr(pcr_val),
            "OI Trend (ATM)":    score_oi_trend(df_chain, spot),
            "IV Rank Signal":    score_iv_rank(iv_rank_pct),
            "Price Action":      score_price_action(ohlcv),
            "Volume Bias":       score_volume(df_chain),
        }
        factor_html = "".join(_factor_bar(lbl, s, COLORS["info"]) for lbl, s in factors.items())
        st.markdown(f"""
        <div style="background:rgba(12,20,40,0.9);border:1px solid rgba(0,212,255,0.1);
                    border-radius:12px;padding:20px">
            {factor_html}
        </div>
        """, unsafe_allow_html=True)

        # Quick stats
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown(section_header("KEY METRICS"), unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        with m1:
            st.metric("PCR",     f"{pcr_val:.3f}", delta=pcr_label)
            st.metric("IV Rank", f"{iv_rank_pct:.0f}%")
        with m2:
            st.metric("ATM IV",  f"{current_iv:.1f}%")
            st.metric("Spot",    f"{spot:,.2f}")

    # ── TRADE SIGNALS ─────────────────────────────────────────────────────────
    with col_signals:
        st.markdown(section_header("AI TRADE SIGNALS", "Actionable Ideas"), unsafe_allow_html=True)
        signals = generate_trade_signals(index, df_chain, spot, sentiment, conf)

        for sig in signals:
            direction  = sig["direction"]
            css_class  = sig["css_class"]
            conf_val   = sig["confidence"]
            color, _   = _SIGNAL_TYPE_COLORS.get(direction, (COLORS["info"], "buy-call"))
            conf_pct   = int(conf_val)

            meta_items = ""
            for label, value in [("LTP", sig["ltp"]), ("Target", sig["target"]),
                                  ("Stop Loss", sig["sl"]), ("R:R", sig["rr"])]:
                meta_items += f"""
                <div class="signal-meta-item">
                    <div class="label">{label}</div>
                    <div class="value">{value if isinstance(value, str) else f'{value:.2f}'}</div>
                </div>"""

            reasons_html = "".join(
                f"<li style='color:#8892A4;font-size:11px;margin:3px 0'>• {r}</li>"
                for r in sig.get("reasons", [])
            )

            st.markdown(f"""
            <div class="signal-card {css_class}">
                <div class="signal-direction {css_class}">{direction}</div>
                <div style="display:flex;align-items:baseline;gap:10px">
                    <div class="signal-strike">{sig['index']} {sig['strike']}</div>
                    <div style="font-size:11px;color:#4A5568">options</div>
                </div>
                <div class="signal-meta">{meta_items}</div>
                <ul style="list-style:none;padding:0;margin:8px 0 10px">{reasons_html}</ul>
                <div style="display:flex;align-items:center;justify-content:space-between">
                    <span style="font-size:11px;color:#4A5568">Confidence</span>
                    <span style="font-size:13px;font-weight:700;color:{color};font-family:'JetBrains Mono',monospace">{conf_pct}%</span>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width:{conf_pct}%;background:{color}"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── SMART MONEY ALERTS ────────────────────────────────────────────────────
    st.markdown(section_header("SMART MONEY TRACKER", "Institutional Activity"), unsafe_allow_html=True)

    alerts = generate_smart_money_alerts(index, df_chain)

    if alerts:
        sev_colors = {
            "bullish": COLORS["bullish"],
            "bearish": COLORS["bearish"],
            "info":    COLORS["info"],
            "warning": COLORS["warning"],
        }
        for alert in alerts:
            sev_color = sev_colors.get(alert.get("severity", "info"), COLORS["info"])
            st.markdown(f"""
            <div class="smart-money-alert" style="border-left-color:{sev_color}">
                <div class="alert-icon">{alert['icon']}</div>
                <div class="alert-text">
                    <strong>{alert['type']}</strong> — {alert['message']}
                </div>
                <div class="alert-time">Now</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No unusual activity detected at this time.")

    # ── OI CONCENTRATION RADAR ────────────────────────────────────────────────
    st.markdown(section_header("SENTIMENT RADAR"), unsafe_allow_html=True)

    from src.analytics.signals import _WEIGHTS
    factor_values = [abs(v) for v in factors.values()]
    factor_labels  = list(factors.keys())

    fig_radar = go.Figure(go.Scatterpolar(
        r=factor_values + [factor_values[0]],
        theta=factor_labels + [factor_labels[0]],
        fill="toself",
        fillcolor="rgba(0,212,255,0.08)",
        line=dict(color=COLORS["info"], width=2),
        marker=dict(size=8, color=COLORS["info"]),
        name="Signal Strength",
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="rgba(7,13,30,0.8)",
            radialaxis=dict(
                visible=True, range=[0, 1],
                tickfont=dict(color="#4A5568"),
                gridcolor="rgba(255,255,255,0.05)",
                color="#4A5568",
            ),
            angularaxis=dict(
                tickfont=dict(color="#8892A4"),
                gridcolor="rgba(255,255,255,0.05)",
                linecolor="rgba(255,255,255,0.08)",
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        height=350,
        showlegend=False,
        margin=dict(l=40, r=40, t=30, b=30),
    )
    st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

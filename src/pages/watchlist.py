"""
pages/watchlist.py — Customizable index watchlist with live metrics.
"""

import streamlit as st
import pandas as pd
import numpy as np

from src.config import COLORS, INDICES
from src.styles import section_header
from src.analytics.options import calculate_pcr, iv_rank
from src.data.generators import generate_option_chain, generate_expiry_dates, _get_spot, generate_historical_iv


def render():
    """Render the Watchlist page."""
    st.markdown(section_header("WATCHLIST", "Index Monitor"), unsafe_allow_html=True)

    # Initialize watchlist in session state
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = list(INDICES.keys())

    # ── Controls ──────────────────────────────────────────────────────────────
    col_add, col_refresh = st.columns([3, 1])
    with col_add:
        all_indices = list(INDICES.keys())
        to_add = st.multiselect(
            "Add/Remove Indices",
            all_indices,
            default=st.session_state.watchlist,
            key="wl_selector",
        )
        st.session_state.watchlist = to_add

    with col_refresh:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("🔄 Refresh", key="wl_refresh"):
            st.cache_data.clear()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    if not st.session_state.watchlist:
        st.warning("No indices in watchlist. Add one above.")
        return

    # ── Watchlist table header ────────────────────────────────────────────────
    st.markdown("""
    <div class="watchlist-header">
        <div>INDEX</div>
        <div>SPOT / CHANGE</div>
        <div>PCR</div>
        <div>ATM IV</div>
        <div>IV RANK</div>
        <div>SENTIMENT</div>
    </div>
    """, unsafe_allow_html=True)

    sentiment_color_map = {
        "Strong Bullish": COLORS["bullish"],
        "Bullish":        COLORS["bullish"],
        "Neutral":        COLORS["neutral"],
        "Bearish":        COLORS["bearish"],
        "Strong Bearish": COLORS["bearish"],
    }

    rows_data = []

    for idx_key in st.session_state.watchlist:
        cfg      = INDICES[idx_key]
        spot     = _get_spot(idx_key)
        prev     = spot * (1 + np.random.uniform(-0.008, 0.008))
        change   = spot - prev
        chg_pct  = change / prev * 100
        expiry   = generate_expiry_dates(idx_key, 1)[0]
        df_chain = generate_option_chain(idx_key, spot, expiry)
        pcr_val, pcr_lbl, pcr_class = calculate_pcr(df_chain)
        atm_iv   = df_chain["call_iv"].median() if not df_chain.empty else 15.0
        iv_hist  = generate_historical_iv(atm_iv)
        ivr, _   = iv_rank(atm_iv, iv_hist)

        # Simple sentiment from PCR
        if pcr_val > 1.2:
            sent = "Bullish"
        elif pcr_val < 0.8:
            sent = "Bearish"
        else:
            sent = "Neutral"

        chg_color = COLORS["bullish"] if change >= 0 else COLORS["bearish"]
        chg_sign  = "+" if change >= 0 else ""
        sent_color = sentiment_color_map.get(sent, COLORS["info"])
        ivr_color  = COLORS["bearish"] if ivr > 70 else (COLORS["bullish"] if ivr < 30 else COLORS["neutral"])
        pcr_color  = COLORS["bullish"] if pcr_class == "bullish" else (COLORS["bearish"] if pcr_class == "bearish" else COLORS["neutral"])

        st.markdown(f"""
        <div class="watchlist-row">
            <div>
                <div style="font-size:14px;font-weight:700;color:{cfg['color']};font-family:'JetBrains Mono',monospace">{idx_key}</div>
                <div style="font-size:11px;color:#4A5568">{cfg['display']}</div>
            </div>
            <div>
                <div style="font-size:16px;font-weight:700;color:#E8EAF0;font-family:'JetBrains Mono',monospace">{spot:,.2f}</div>
                <div style="font-size:12px;color:{chg_color};font-weight:600;font-family:'JetBrains Mono',monospace">
                    {chg_sign}{change:.2f} ({chg_sign}{chg_pct:.2f}%)
                </div>
            </div>
            <div style="font-size:15px;font-weight:700;color:{pcr_color};font-family:'JetBrains Mono',monospace">
                {pcr_val:.2f}
            </div>
            <div style="font-size:15px;font-weight:700;color:#E8EAF0;font-family:'JetBrains Mono',monospace">
                {atm_iv:.1f}%
            </div>
            <div style="font-size:15px;font-weight:700;color:{ivr_color};font-family:'JetBrains Mono',monospace">
                {ivr:.0f}%
            </div>
            <div style="font-size:13px;font-weight:700;color:{sent_color}">{sent}</div>
        </div>
        """, unsafe_allow_html=True)

        rows_data.append({
            "Index":    idx_key,
            "Spot":     spot,
            "Change":   f"{chg_sign}{change:.2f}",
            "Change%":  f"{chg_sign}{chg_pct:.2f}%",
            "PCR":      pcr_val,
            "ATM IV":   atm_iv,
            "IV Rank":  ivr,
            "Sentiment": sent,
        })

    # ── Export ────────────────────────────────────────────────────────────────
    if rows_data:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        export_df = pd.DataFrame(rows_data)
        csv = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Export Watchlist CSV",
            csv,
            "watchlist.csv",
            "text/csv",
            key="wl_export",
        )

    # ── Mini charts ───────────────────────────────────────────────────────────
    st.markdown(section_header("QUICK COMPARE"), unsafe_allow_html=True)
    st.caption("Spot price relative performance (normalized to 100)")

    from src.data.generators import generate_ohlcv
    import plotly.graph_objects as go
    from src.config import PLOTLY_TEMPLATE, plotly_layout

    fig_cmp = go.Figure()
    for idx_key in st.session_state.watchlist[:5]:  # max 5
        spot   = _get_spot(idx_key)
        ohlcv  = generate_ohlcv(spot, n_days=30)
        rel    = ohlcv["close"] / ohlcv["close"].iloc[0] * 100
        cfg    = INDICES[idx_key]
        fig_cmp.add_trace(go.Scatter(
            x=ohlcv["date"].astype(str),
            y=rel,
            mode="lines",
            name=idx_key,
            line=dict(color=cfg["color"], width=2),
        ))
    fig_cmp.add_hline(y=100, line_color="rgba(255,255,255,0.15)", line_dash="dot", line_width=1)
    fig_cmp.update_layout(
        **plotly_layout(
            height=300,
            xaxis=dict(showticklabels=False),
            yaxis_title="Relative Performance (base=100)",
        )
    )
    st.plotly_chart(fig_cmp, use_container_width=True, config={"displayModeBar": False})

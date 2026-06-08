"""
pages/option_chain.py — Interactive option chain with heatmap coloring, ATM highlight, filters.
Uses st.dataframe with styled pandas (AgGrid optional).
"""

import streamlit as st
import pandas as pd
import numpy as np

from src.config import COLORS, INDICES
from src.styles import section_header
from src.analytics.options import calculate_pcr, calculate_max_pain


def _color_oi(val, max_val, base_rgb=(0, 230, 118)):
    """Return rgba background for OI heatmap."""
    if max_val == 0:
        return ""
    intensity = min(val / max_val, 1.0)
    alpha = 0.1 + intensity * 0.35
    r, g, b = base_rgb
    return f"background-color: rgba({r},{g},{b},{alpha:.2f})"


def _style_chain(df: pd.DataFrame, atm_strike: float):
    """Apply conditional styling to option chain DataFrame."""
    styles = pd.DataFrame("", index=df.index, columns=df.columns)
    max_call_oi = df["Call OI"].max()
    max_put_oi  = df["Put OI"].max()

    for i, row in df.iterrows():
        strike = row["Strike"]
        # ATM row
        if strike == atm_strike:
            styles.loc[i, :] = "background-color: rgba(255,214,0,0.08); border-top: 1px solid rgba(255,214,0,0.3); border-bottom: 1px solid rgba(255,214,0,0.3);"

        # Call OI heatmap
        styles.loc[i, "Call OI"] = _color_oi(row["Call OI"], max_call_oi, (0, 230, 118))
        # Put OI heatmap
        styles.loc[i, "Put OI"]  = _color_oi(row["Put OI"],  max_put_oi,  (255, 68, 68))

        # ITM call coloring
        if row.get("_is_itm_call", False):
            for c in ["Call OI", "Call ΔOI", "Call Vol", "Call IV", "Call Δ", "Call LTP"]:
                if c in styles.columns:
                    existing = styles.loc[i, c]
                    if "background-color" not in existing:
                        styles.loc[i, c] = "background-color: rgba(0,230,118,0.04);"

        # ITM put coloring
        if row.get("_is_itm_put", False):
            for c in ["Put OI", "Put ΔOI", "Put Vol", "Put IV", "Put Δ", "Put LTP"]:
                if c in styles.columns:
                    existing = styles.loc[i, c]
                    if "background-color" not in existing:
                        styles.loc[i, c] = "background-color: rgba(255,68,68,0.04);"

        # Delta coloring
        if "Call Δ" in df.columns:
            d = row["Call Δ"]
            if d > 0.6:
                styles.loc[i, "Call Δ"] = "color: #00E676; font-weight:600"
            elif d < 0.3:
                styles.loc[i, "Call Δ"] = "color: #FF9800;"

    return styles


def render(index: str, spot: float, df_chain: pd.DataFrame):
    """Render the Option Chain page."""

    st.markdown(section_header("OPTION CHAIN", f"{INDICES[index]['display']} — Live"), unsafe_allow_html=True)

    if df_chain.empty:
        st.error("No option chain data available.")
        return

    # ── Controls ──────────────────────────────────────────────────────────────
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([2, 1, 1, 1])

    with ctrl_col1:
        search_strike = st.number_input(
            "🔍 Jump to Strike",
            min_value=int(df_chain["strike"].min()),
            max_value=int(df_chain["strike"].max()),
            value=int(round(spot / INDICES[index]["strike_step"]) * INDICES[index]["strike_step"]),
            step=INDICES[index]["strike_step"],
        )
    with ctrl_col2:
        filter_mode = st.selectbox("Filter", ["All Strikes", "ITM Only", "OTM Only", "Near ATM (±5)"])
    with ctrl_col3:
        sort_col = st.selectbox("Sort By", ["Strike", "Call OI", "Put OI", "Call Vol", "Put Vol"])
    with ctrl_col4:
        sort_asc = st.checkbox("Ascending", value=True)

    # ── ATM ───────────────────────────────────────────────────────────────────
    step = INDICES[index]["strike_step"]
    atm  = round(spot / step) * step

    # ── Filter ────────────────────────────────────────────────────────────────
    df_disp = df_chain.copy()
    if filter_mode == "ITM Only":
        df_disp = df_disp[(df_disp["is_itm_call"]) | (df_disp["is_itm_put"])]
    elif filter_mode == "OTM Only":
        df_disp = df_disp[(~df_disp["is_itm_call"]) & (~df_disp["is_itm_put"])]
    elif filter_mode == "Near ATM (±5)":
        df_disp = df_disp[abs(df_disp["strike"] - atm) <= 5 * step]

    # ── Build display DataFrame ───────────────────────────────────────────────
    disp_cols = {
        "Call OI":   df_disp["call_oi"],
        "Call ΔOI":  df_disp["call_chg_oi"],
        "Call Vol":  df_disp["call_volume"],
        "Call IV":   df_disp["call_iv"].map(lambda x: f"{x:.1f}%"),
        "Call Δ":    df_disp["call_delta"],
        "Call Γ":    df_disp["call_gamma"].map(lambda x: f"{x:.5f}"),
        "Call Θ":    df_disp["call_theta"].map(lambda x: f"{x:.2f}"),
        "Call LTP":  df_disp["call_ltp"],
        "Strike":    df_disp["strike"].astype(int),
        "Put LTP":   df_disp["put_ltp"],
        "Put Θ":     df_disp["put_theta"].map(lambda x: f"{x:.2f}"),
        "Put Γ":     df_disp["put_gamma"].map(lambda x: f"{x:.5f}"),
        "Put Δ":     df_disp["put_delta"].map(lambda x: f"{x:.4f}"),
        "Put IV":    df_disp["put_iv"].map(lambda x: f"{x:.1f}%"),
        "Put Vol":   df_disp["put_volume"],
        "Put ΔOI":   df_disp["put_chg_oi"],
        "Put OI":    df_disp["put_oi"],
        # Hidden flags for styling
        "_is_itm_call": df_disp["is_itm_call"],
        "_is_itm_put":  df_disp["is_itm_put"],
    }
    display_df = pd.DataFrame(disp_cols).reset_index(drop=True)

    # Sort
    sort_map = {
        "Strike": "Strike", "Call OI": "Call OI",
        "Put OI": "Put OI", "Call Vol": "Call Vol", "Put Vol": "Put Vol",
    }
    display_df = display_df.sort_values(sort_map[sort_col], ascending=sort_asc)

    # Scroll to search_strike if applicable
    if search_strike in df_disp["strike"].values:
        st.info(f"📍 Strike {search_strike} — {'ATM ⭐' if search_strike == atm else 'OTM' if search_strike > spot else 'ITM'}")

    # ── Render hidden cols ────────────────────────────────────────────────────
    visible_df = display_df.drop(columns=["_is_itm_call", "_is_itm_put"])

    # ATM highlight banner
    atm_in_view = atm in df_disp["strike"].values
    if atm_in_view:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;padding:8px 16px;
                    background:rgba(255,214,0,0.06);border:1px solid rgba(255,214,0,0.2);
                    border-radius:8px;margin-bottom:12px">
            <span style="color:#FFD600;font-weight:700;font-size:13px">⭐ ATM Strike</span>
            <span style="color:#E8EAF0;font-family:'JetBrains Mono',monospace;font-weight:700">{atm:,}</span>
            <span style="color:#4A5568;font-size:12px">|</span>
            <span style="color:#4A5568;font-size:12px">Spot: {spot:,.2f}</span>
        </div>
        """, unsafe_allow_html=True)

    # Styling
    styled = display_df.style.apply(
        lambda _: _style_chain(display_df, atm), axis=None
    ).hide(subset=["_is_itm_call", "_is_itm_put"], axis="columns").format({
        "Call OI":  "{:,.0f}",
        "Call ΔOI": "{:+,.0f}",
        "Call Vol": "{:,.0f}",
        "Call Δ":   "{:.4f}",
        "Call LTP": "{:.2f}",
        "Strike":   "{:,.0f}",
        "Put LTP":  "{:.2f}",
        "Put Δ":    "{}",
        "Put Vol":  "{:,.0f}",
        "Put ΔOI":  "{:+,.0f}",
        "Put OI":   "{:,.0f}",
    })

    st.dataframe(styled, use_container_width=True, height=520)

    # ── PCR summary bar ───────────────────────────────────────────────────────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    pcr_val, pcr_label, pcr_class = calculate_pcr(df_chain)
    max_pain_strike, _ = calculate_max_pain(df_chain)
    pcr_color = COLORS["bullish"] if pcr_class == "bullish" else (COLORS["bearish"] if pcr_class == "bearish" else COLORS["neutral"])

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Total Call OI",  f"{df_chain['call_oi'].sum():,.0f}")
    with m2:
        st.metric("Total Put OI",   f"{df_chain['put_oi'].sum():,.0f}")
    with m3:
        st.metric("PCR (Overall)",  f"{pcr_val:.3f}", delta=pcr_label)
    with m4:
        st.metric("Max Pain",       f"{max_pain_strike:,.0f}", delta=f"Δ {abs(spot-max_pain_strike):.0f} pts")
    with m5:
        st.metric("ATM IV (avg)",   f"{df_chain[df_chain['is_atm']]['call_iv'].mean():.1f}%")

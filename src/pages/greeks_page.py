"""
pages/greeks_page.py — Delta/Gamma/Theta/Vega exposure charts, Gamma Wall, Greeks table.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from src.config import COLORS, PLOTLY_TEMPLATE, INDICES, plotly_layout
from src.styles import section_header
from src.analytics.greeks import gamma_exposure


def render(index: str, spot: float, df_chain: pd.DataFrame):
    """Render the Greeks Dashboard page."""

    st.markdown(section_header("GREEKS DASHBOARD", INDICES[index]["display"]), unsafe_allow_html=True)

    if df_chain.empty:
        st.error("No data available.")
        return

    step = INDICES[index]["strike_step"]
    lot  = INDICES[index]["lot_size"]
    atm  = round(spot / step) * step

    tab1, tab2, tab3, tab4 = st.tabs(["⚡ GEX (Gamma)", "📐 Delta", "⏳ Theta / Vega", "📋 Greeks Table"])

    # ── TAB 1: GAMMA EXPOSURE ────────────────────────────────────────────────
    with tab1:
        st.markdown(section_header("GAMMA EXPOSURE (GEX)"), unsafe_allow_html=True)

        gex_vals = gamma_exposure(
            df_chain["strike"].values,
            df_chain["call_oi"].values,
            df_chain["put_oi"].values,
            df_chain["call_gamma"].values,
            df_chain["put_gamma"].values,
            lot,
        )

        gex_colors = [COLORS["bullish"] if g > 0 else COLORS["bearish"] for g in gex_vals]

        fig_gex = go.Figure()
        fig_gex.add_trace(go.Bar(
            x=df_chain["strike"].values,
            y=gex_vals,
            marker_color=gex_colors,
            opacity=0.85,
            name="GEX",
            hovertemplate="Strike: %{x}<br>GEX: %{y:,.0f}<extra></extra>",
        ))
        fig_gex.add_vline(x=atm, line_color="rgba(255,214,0,0.6)", line_dash="dash",
                          line_width=2, annotation_text="ATM", annotation_font_color="#FFD600")
        fig_gex.add_hline(y=0, line_color="rgba(255,255,255,0.15)", line_width=1)
        fig_gex.update_layout(
            **plotly_layout(
                height=380,
                title="Net Gamma Exposure by Strike (Green = Dealer Long Gamma)",
                xaxis_title="Strike",
                yaxis_title="GEX (contracts × gamma × lot)",
            )
        )
        st.plotly_chart(fig_gex, use_container_width=True, config={"displayModeBar": False})

        # Gamma Wall — strike with highest absolute GEX
        max_gex_idx = int(np.argmax(np.abs(gex_vals)))
        gamma_wall  = df_chain["strike"].values[max_gex_idx]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🧱 Gamma Wall", f"{gamma_wall:,.0f}", delta=f"{abs(spot-gamma_wall):.0f} pts away")
        with col2:
            positive_gex = sum(g for g in gex_vals if g > 0)
            st.metric("⬆ Positive GEX", f"{positive_gex:,.0f}")
        with col3:
            negative_gex = sum(g for g in gex_vals if g < 0)
            st.metric("⬇ Negative GEX", f"{negative_gex:,.0f}")

        # Gamma curve across strikes
        st.markdown(section_header("GAMMA BY STRIKE"), unsafe_allow_html=True)
        fig_gamma_curve = go.Figure()
        fig_gamma_curve.add_trace(go.Scatter(
            x=df_chain["strike"].values,
            y=df_chain["call_gamma"].values,
            mode="lines+markers",
            name="Call Gamma",
            line=dict(color=COLORS["bullish"], width=2),
            marker=dict(size=5),
        ))
        fig_gamma_curve.add_trace(go.Scatter(
            x=df_chain["strike"].values,
            y=df_chain["put_gamma"].values,
            mode="lines+markers",
            name="Put Gamma",
            line=dict(color=COLORS["bearish"], width=2),
            marker=dict(size=5),
        ))
        fig_gamma_curve.update_layout(
            **plotly_layout(
                height=280,
                xaxis_title="Strike",
                yaxis_title="Gamma",
            )
        )
        st.plotly_chart(fig_gamma_curve, use_container_width=True, config={"displayModeBar": False})

    # ── TAB 2: DELTA EXPOSURE ────────────────────────────────────────────────
    with tab2:
        st.markdown(section_header("NET DELTA EXPOSURE"), unsafe_allow_html=True)

        net_delta = (
            df_chain["call_delta"] * df_chain["call_oi"] +
            df_chain["put_delta"]  * df_chain["put_oi"]
        ) * lot

        dex_colors = [COLORS["bullish"] if d > 0 else COLORS["bearish"] for d in net_delta]

        fig_dex = go.Figure()
        fig_dex.add_trace(go.Bar(
            x=df_chain["strike"].values,
            y=net_delta.values,
            marker_color=dex_colors,
            opacity=0.85,
            name="Net Delta",
        ))
        fig_dex.add_vline(x=atm, line_color="rgba(255,214,0,0.6)", line_dash="dash", line_width=2)
        fig_dex.add_hline(y=0, line_color="rgba(255,255,255,0.15)", line_width=1)
        fig_dex.update_layout(
            **plotly_layout(
                height=380,
                title="Net Delta Exposure by Strike",
                xaxis_title="Strike",
                yaxis_title="Net Delta × OI × Lot",
            )
        )
        st.plotly_chart(fig_dex, use_container_width=True, config={"displayModeBar": False})

        col1, col2 = st.columns(2)
        with col1:
            # Call Delta distribution
            fig_cd = go.Figure(go.Scatter(
                x=df_chain["strike"].values,
                y=df_chain["call_delta"].values,
                mode="lines+markers",
                line=dict(color=COLORS["bullish"], width=2),
                fill="tozeroy",
                fillcolor="rgba(0,230,118,0.06)",
                name="Call Delta",
            ))
            fig_cd.add_hline(y=0.5, line_color="rgba(255,214,0,0.4)", line_dash="dash")
            fig_cd.update_layout(
                **plotly_layout(
                    height=260,
                    title="Call Delta Curve",
                    xaxis_title="Strike",
                    yaxis_title="Delta",
                )
            )
            st.plotly_chart(fig_cd, use_container_width=True, config={"displayModeBar": False})

        with col2:
            # Put Delta distribution
            fig_pd = go.Figure(go.Scatter(
                x=df_chain["strike"].values,
                y=df_chain["put_delta"].values,
                mode="lines+markers",
                line=dict(color=COLORS["bearish"], width=2),
                fill="tozeroy",
                fillcolor="rgba(255,68,68,0.06)",
                name="Put Delta",
            ))
            fig_pd.add_hline(y=-0.5, line_color="rgba(255,214,0,0.4)", line_dash="dash")
            fig_pd.update_layout(
                **plotly_layout(
                    height=260,
                    title="Put Delta Curve",
                    xaxis_title="Strike",
                    yaxis_title="Delta",
                )
            )
            st.plotly_chart(fig_pd, use_container_width=True, config={"displayModeBar": False})

    # ── TAB 3: THETA & VEGA ───────────────────────────────────────────────────
    with tab3:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(section_header("THETA DECAY BY STRIKE"), unsafe_allow_html=True)
            fig_theta = go.Figure()
            fig_theta.add_trace(go.Scatter(
                x=df_chain["strike"].values,
                y=df_chain["call_theta"].values,
                mode="lines+markers",
                name="Call Theta",
                line=dict(color=COLORS["warning"], width=2),
                marker=dict(size=5),
            ))
            fig_theta.add_trace(go.Scatter(
                x=df_chain["strike"].values,
                y=df_chain["put_theta"].values,
                mode="lines+markers",
                name="Put Theta",
                line=dict(color="#FF9800", width=2, dash="dot"),
                marker=dict(size=5),
            ))
            fig_theta.update_layout(
                **plotly_layout(
                    height=300,
                    xaxis_title="Strike",
                    yaxis_title="Theta (per day)",
                )
            )
            st.plotly_chart(fig_theta, use_container_width=True, config={"displayModeBar": False})

            # Theta stats
            atm_call_theta = df_chain.loc[df_chain["strike"] == atm, "call_theta"].values
            atm_put_theta  = df_chain.loc[df_chain["strike"] == atm, "put_theta"].values
            if len(atm_call_theta):
                st.metric("ATM Call Theta/day", f"{atm_call_theta[0]:.2f}")
            if len(atm_put_theta):
                st.metric("ATM Put Theta/day",  f"{atm_put_theta[0]:.2f}")

        with col2:
            st.markdown(section_header("VEGA BY STRIKE"), unsafe_allow_html=True)
            fig_vega = go.Figure()
            fig_vega.add_trace(go.Scatter(
                x=df_chain["strike"].values,
                y=df_chain["call_vega"].values,
                mode="lines+markers",
                name="Call Vega",
                line=dict(color=COLORS["purple"], width=2),
                fill="tozeroy",
                fillcolor="rgba(124,58,237,0.06)",
            ))
            fig_vega.add_trace(go.Scatter(
                x=df_chain["strike"].values,
                y=df_chain["put_vega"].values,
                mode="lines+markers",
                name="Put Vega",
                line=dict(color=COLORS["purple"], width=2, dash="dot"),
            ))
            fig_vega.update_layout(
                **plotly_layout(
                    height=300,
                    xaxis_title="Strike",
                    yaxis_title="Vega (per 1% IV change)",
                )
            )
            st.plotly_chart(fig_vega, use_container_width=True, config={"displayModeBar": False})

            atm_vega = df_chain.loc[df_chain["strike"] == atm, "call_vega"].values
            if len(atm_vega):
                st.metric("ATM Call Vega (per 1% IV)", f"{atm_vega[0]:.2f}")

    # ── TAB 4: GREEKS TABLE ───────────────────────────────────────────────────
    with tab4:
        st.markdown(section_header("FULL GREEKS REFERENCE TABLE"), unsafe_allow_html=True)

        greeks_df = df_chain[[
            "strike", "call_delta", "call_gamma", "call_theta", "call_vega",
            "call_iv", "call_ltp",
            "put_delta", "put_gamma", "put_theta", "put_vega",
            "put_iv", "put_ltp",
        ]].copy()
        greeks_df.columns = [
            "Strike",
            "C-Delta", "C-Gamma", "C-Theta", "C-Vega", "C-IV%", "C-LTP",
            "P-Delta", "P-Gamma", "P-Theta", "P-Vega", "P-IV%", "P-LTP",
        ]

        def _hl_atm(row):
            if row["Strike"] == atm:
                return ["background-color:rgba(255,214,0,0.08)"] * len(row)
            return [""] * len(row)

        styled_g = greeks_df.style.apply(_hl_atm, axis=1).format({
            "Strike":  "{:,.0f}",
            "C-Delta": "{:.4f}", "C-Gamma": "{:.6f}", "C-Theta": "{:.3f}",
            "C-Vega":  "{:.3f}", "C-IV%":   "{:.1f}%", "C-LTP": "{:.2f}",
            "P-Delta": "{:.4f}", "P-Gamma": "{:.6f}", "P-Theta": "{:.3f}",
            "P-Vega":  "{:.3f}", "P-IV%":   "{:.1f}%", "P-LTP": "{:.2f}",
        })
        st.dataframe(styled_g, use_container_width=True, height=500)

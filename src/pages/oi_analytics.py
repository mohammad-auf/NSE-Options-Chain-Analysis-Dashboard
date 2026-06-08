"""
pages/oi_analytics.py — OI heatmap, shift analysis, build-up classification, PCR gauge, Max Pain chart.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from src.config import COLORS, PLOTLY_TEMPLATE, INDICES, plotly_layout
from src.styles import section_header
from src.analytics.options import (
    calculate_pcr, calculate_max_pain, classify_oi_activity,
    oi_activity_summary, strike_wise_pcr,
)


_ACTIVITY_COLORS = {
    "Long Buildup":   COLORS["bullish"],
    "Short Buildup":  COLORS["bearish"],
    "Short Covering": COLORS["info"],
    "Long Unwinding": COLORS["warning"],
}

_ACTIVITY_EMOJI = {
    "Long Buildup":   "🟢",
    "Short Buildup":  "🔴",
    "Short Covering": "🔵",
    "Long Unwinding": "🟠",
}

_ACTIVITY_CSS = {
    "Long Buildup":   "long-buildup",
    "Short Buildup":  "short-buildup",
    "Short Covering": "short-covering",
    "Long Unwinding": "long-unwinding",
}


def render(index: str, spot: float, df_chain: pd.DataFrame,
           pcr_history: pd.DataFrame, max_pain_history: pd.DataFrame):
    """Render the OI Analytics page."""

    st.markdown(section_header("OI ANALYTICS ENGINE", INDICES[index]["display"]), unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 OI Overview", "🔥 OI Heatmap", "🧩 OI Activity",
        "🎯 Max Pain",    "⚖️ PCR Analysis",
    ])

    # ── TAB 1: OI OVERVIEW ───────────────────────────────────────────────────
    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(section_header("CALL vs PUT OI — Top Strikes"), unsafe_allow_html=True)
            top_calls = df_chain.nlargest(15, "call_oi").sort_values("strike")
            top_puts  = df_chain.nlargest(15, "put_oi").sort_values("strike")

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=top_calls["strike"].astype(str),
                y=top_calls["call_oi"],
                name="Call OI",
                marker=dict(color=COLORS["bullish"], opacity=0.85,
                            line=dict(color=COLORS["bullish"], width=1)),
            ))
            fig.add_trace(go.Bar(
                x=top_puts["strike"].astype(str),
                y=top_puts["put_oi"],
                name="Put OI",
                marker=dict(color=COLORS["bearish"], opacity=0.85,
                            line=dict(color=COLORS["bearish"], width=1)),
            ))
            fig.add_vline(x=str(round(spot / INDICES[index]["strike_step"]) * INDICES[index]["strike_step"]),
                          line_color="rgba(255,214,0,0.5)", line_dash="dash", line_width=2)
            fig.update_layout(
                **plotly_layout(
                    height=380,
                    barmode="group",
                    xaxis_title="Strike",
                    yaxis_title="Open Interest",
                )
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with col2:
            st.markdown(section_header("OI VOLUME COMPARISON"), unsafe_allow_html=True)
            total_call_oi  = df_chain["call_oi"].sum()
            total_put_oi   = df_chain["put_oi"].sum()
            total_call_vol = df_chain["call_volume"].sum()
            total_put_vol  = df_chain["put_volume"].sum()

            fig_pie = go.Figure()
            fig_pie.add_trace(go.Bar(
                x=["Call OI", "Put OI", "Call Vol", "Put Vol"],
                y=[total_call_oi, total_put_oi, total_call_vol, total_put_vol],
                marker_color=[COLORS["bullish"], COLORS["bearish"], "#00BFFF", "#FF6B6B"],
                opacity=0.85,
            ))
            fig_pie.update_layout(
                **plotly_layout(
                    height=380,
                    yaxis_title="Contracts",
                )
            )
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

        # Total OI summary
        pcr_val, pcr_lbl, _ = calculate_pcr(df_chain)
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Total Call OI",  f"{total_call_oi:,.0f}")
        with m2: st.metric("Total Put OI",   f"{total_put_oi:,.0f}")
        with m3: st.metric("Overall PCR",    f"{pcr_val:.3f}", delta=pcr_lbl)
        with m4: st.metric("Total Volume",   f"{total_call_vol + total_put_vol:,.0f}")

    # ── TAB 2: OI HEATMAP ────────────────────────────────────────────────────
    with tab2:
        st.markdown(section_header("OI CONCENTRATION HEATMAP"), unsafe_allow_html=True)

        heatmap_type = st.radio("Show", ["Call OI", "Put OI", "Net OI (Put - Call)"], horizontal=True)

        df_sorted = df_chain.sort_values("strike")
        strikes   = df_sorted["strike"].values

        if heatmap_type == "Call OI":
            z_vals = df_sorted["call_oi"].values
            cscale = [[0, "#0C1428"], [0.5, "#007700"], [1.0, "#00E676"]]
            title  = "Call OI Heatmap"
        elif heatmap_type == "Put OI":
            z_vals = df_sorted["put_oi"].values
            cscale = [[0, "#0C1428"], [0.5, "#770000"], [1.0, "#FF4444"]]
            title  = "Put OI Heatmap"
        else:
            z_vals = df_sorted["put_oi"].values - df_sorted["call_oi"].values
            cscale = [[0, "#FF4444"], [0.5, "#0C1428"], [1.0, "#00E676"]]
            title  = "Net OI (Put − Call) Heatmap"

        fig_hm = go.Figure(go.Bar(
            x=strikes,
            y=z_vals,
            marker=dict(
                color=z_vals,
                colorscale=cscale,
                showscale=True,
                colorbar=dict(
                    title="OI",
                    tickfont=dict(color="#8892A4"),
                    titlefont=dict(color="#8892A4"),
                ),
            ),
        ))
        # ATM line
        atm = round(spot / INDICES[index]["strike_step"]) * INDICES[index]["strike_step"]
        fig_hm.add_vline(x=atm, line_color="rgba(255,214,0,0.7)", line_dash="dash",
                         line_width=2, annotation_text="ATM",
                         annotation_font_color="#FFD600")
        fig_hm.update_layout(
            **plotly_layout(
                height=400,
                title=title,
                xaxis_title="Strike",
                yaxis_title="Open Interest",
            )
        )
        st.plotly_chart(fig_hm, use_container_width=True, config={"displayModeBar": False})

        # OI Change heatmap
        st.markdown(section_header("OI CHANGE (TODAY)"), unsafe_allow_html=True)
        fig_chg = go.Figure()
        colors_chg = [COLORS["bullish"] if v > 0 else COLORS["bearish"]
                      for v in df_sorted["call_chg_oi"].values]
        fig_chg.add_trace(go.Bar(
            x=df_sorted["strike"].values,
            y=df_sorted["call_chg_oi"].values,
            name="Call ΔOI",
            marker_color=colors_chg,
            opacity=0.85,
        ))
        fig_chg.add_trace(go.Bar(
            x=df_sorted["strike"].values,
            y=df_sorted["put_chg_oi"].values,
            name="Put ΔOI",
            marker_color=[COLORS["bearish"] if v > 0 else COLORS["bullish"]
                          for v in df_sorted["put_chg_oi"].values],
            opacity=0.7,
        ))
        fig_chg.update_layout(
            **plotly_layout(
                height=300,
                barmode="group",
                xaxis_title="Strike",
                yaxis_title="OI Change",
            )
        )
        st.plotly_chart(fig_chg, use_container_width=True, config={"displayModeBar": False})

    # ── TAB 3: OI ACTIVITY ───────────────────────────────────────────────────
    with tab3:
        st.markdown(section_header("OI ACTIVITY CLASSIFICATION"), unsafe_allow_html=True)

        df_act   = classify_oi_activity(df_chain)
        act_summ = oi_activity_summary(df_act)

        # Summary cards
        c1, c2, c3, c4 = st.columns(4)
        cols = [c1, c2, c3, c4]
        for i, (act, cnt) in enumerate(act_summ.items()):
            css_cls = _ACTIVITY_CSS.get(act, "info")
            emoji   = _ACTIVITY_EMOJI.get(act, "📊")
            with cols[i % 4]:
                st.markdown(f"""
                <div style="background:rgba(12,20,40,0.9);border:1px solid rgba(255,255,255,0.06);
                            border-radius:10px;padding:16px;text-align:center;margin-bottom:8px">
                    <div style="font-size:11px;color:#4A5568;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">{emoji} {act}</div>
                    <div style="font-size:28px;font-weight:800;color:{_ACTIVITY_COLORS.get(act,'#00D4FF')};font-family:'JetBrains Mono',monospace">{cnt}</div>
                    <div class="oi-badge {css_cls}" style="margin-top:8px;display:inline-flex">{act}</div>
                </div>
                """, unsafe_allow_html=True)

        # Per-strike activity table
        st.markdown(section_header("STRIKE-WISE ACTIVITY"), unsafe_allow_html=True)
        display_act = df_act[["strike", "call_oi", "call_chg_oi", "call_activity", "put_oi", "put_chg_oi", "put_activity"]].copy()
        display_act.columns = ["Strike", "Call OI", "Call ΔOI", "Call Activity", "Put OI", "Put ΔOI", "Put Activity"]

        def _color_activity(val):
            cmap = {
                "Long Buildup":   "color:#00E676;font-weight:600",
                "Short Buildup":  "color:#FF4444;font-weight:600",
                "Short Covering": "color:#00D4FF;font-weight:600",
                "Long Unwinding": "color:#FF9800;font-weight:600",
            }
            return cmap.get(val, "")

        styled_act = display_act.style.applymap(
            _color_activity, subset=["Call Activity", "Put Activity"]
        ).format({"Strike": "{:,.0f}", "Call OI": "{:,.0f}", "Call ΔOI": "{:+,.0f}",
                  "Put OI": "{:,.0f}", "Put ΔOI": "{:+,.0f}"})

        st.dataframe(styled_act, use_container_width=True, height=380)

        # Treemap
        st.markdown(section_header("OI ACTIVITY TREEMAP"), unsafe_allow_html=True)
        fig_tree = go.Figure(go.Treemap(
            labels=df_act.apply(lambda r: f"{r['strike']:.0f}", axis=1).tolist() * 2,
            parents=df_act["call_activity"].tolist() + df_act["put_activity"].tolist(),
            values=df_act["call_oi"].tolist() + df_act["put_oi"].tolist(),
            marker=dict(
                colors=[_ACTIVITY_COLORS.get(a, "#00D4FF") for a in df_act["call_activity"]] +
                       [_ACTIVITY_COLORS.get(a, "#00D4FF") for a in df_act["put_activity"]],
                line=dict(width=1, color="#020614"),
            ),
            textfont=dict(color="#E8EAF0", size=11),
        ))
        fig_tree.update_layout(**plotly_layout(height=350))
        st.plotly_chart(fig_tree, use_container_width=True, config={"displayModeBar": False})

    # ── TAB 4: MAX PAIN ───────────────────────────────────────────────────────
    with tab4:
        st.markdown(section_header("MAX PAIN ANALYSIS"), unsafe_allow_html=True)

        max_pain_val, pain_df = calculate_max_pain(df_chain)
        dist_from_spot = abs(spot - max_pain_val)

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Max Pain Strike", f"{max_pain_val:,.0f}")
        with m2:
            st.metric("Current Spot",    f"{spot:,.2f}")
        with m3:
            direction = "above spot" if max_pain_val > spot else "below spot"
            st.metric("Distance", f"{dist_from_spot:.0f} pts", delta=direction)

        # Pain curve
        fig_pain = go.Figure()
        fig_pain.add_trace(go.Scatter(
            x=pain_df["strike"],
            y=pain_df["total_pain"],
            mode="lines+markers",
            name="Total Pain",
            line=dict(color=COLORS["warning"], width=2.5),
            marker=dict(size=5, color=COLORS["warning"]),
            fill="tozeroy",
            fillcolor="rgba(255,152,0,0.06)",
        ))
        fig_pain.add_vline(x=max_pain_val, line_color=COLORS["warning"],
                           line_dash="dash", line_width=2,
                           annotation_text=f"Max Pain: {max_pain_val:.0f}",
                           annotation_font_color=COLORS["warning"])
        fig_pain.add_vline(x=spot, line_color=COLORS["info"],
                           line_dash="dot", line_width=2,
                           annotation_text=f"Spot: {spot:.2f}",
                           annotation_font_color=COLORS["info"])
        fig_pain.update_layout(
            **plotly_layout(
                height=380,
                title="Option Pain Distribution (Lower = Max Pain)",
                xaxis_title="Strike Price",
                yaxis_title="Total Pain (Option Buyer Losses)",
            )
        )
        st.plotly_chart(fig_pain, use_container_width=True, config={"displayModeBar": False})

        # Historical max pain trend
        if not max_pain_history.empty:
            st.markdown(section_header("HISTORICAL MAX PAIN TREND"), unsafe_allow_html=True)
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Scatter(
                x=max_pain_history["date"].astype(str),
                y=max_pain_history["max_pain"],
                mode="lines+markers",
                name="Max Pain",
                line=dict(color=COLORS["warning"], width=2),
                marker=dict(size=6),
            ))
            fig_hist.update_layout(
                **plotly_layout(
                    height=250,
                    xaxis_title="Date",
                    yaxis_title="Max Pain Strike",
                )
            )
            st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

    # ── TAB 5: PCR ANALYSIS ───────────────────────────────────────────────────
    with tab5:
        st.markdown(section_header("PCR ANALYSIS"), unsafe_allow_html=True)

        pcr_val, pcr_lbl, pcr_class = calculate_pcr(df_chain)

        col_g, col_d = st.columns([1, 2])

        with col_g:
            # Gauge chart
            gauge_color = COLORS["bullish"] if pcr_class == "bullish" else (COLORS["bearish"] if pcr_class == "bearish" else COLORS["neutral"])
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=pcr_val,
                title={"text": "Put-Call Ratio", "font": {"color": "#E8EAF0", "size": 14}},
                number={"font": {"color": gauge_color, "size": 40, "family": "JetBrains Mono"},
                        "suffix": ""},
                delta={"reference": 1.0, "font": {"size": 12}},
                gauge={
                    "axis": {"range": [0, 2.5], "tickcolor": "#4A5568",
                             "tickfont": {"color": "#4A5568"}},
                    "bar": {"color": gauge_color, "thickness": 0.3},
                    "bgcolor": "rgba(12,20,40,0.8)",
                    "bordercolor": "rgba(0,212,255,0.1)",
                    "steps": [
                        {"range": [0,   0.8], "color": "rgba(255,68,68,0.12)"},
                        {"range": [0.8, 1.2], "color": "rgba(255,214,0,0.08)"},
                        {"range": [1.2, 2.5], "color": "rgba(0,230,118,0.12)"},
                    ],
                    "threshold": {
                        "line": {"color": "#FFD600", "width": 2},
                        "thickness": 0.85,
                        "value": 1.0,
                    },
                },
            ))
            fig_gauge.update_layout(
                height=300,
                paper_bgcolor="rgba(0,0,0,0)",
                font={"color": "#8892A4"},
                margin=dict(l=20, r=20, t=40, b=20),
            )
            st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})
            st.markdown(f"""
            <div style="text-align:center;padding:12px">
                <span style="font-size:16px;font-weight:700;color:{gauge_color}">{pcr_lbl.upper()}</span>
                <div style="font-size:12px;color:#4A5568;margin-top:4px">
                    &lt;0.8 Bearish · 0.8–1.2 Neutral · &gt;1.2 Bullish
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_d:
            # Historical PCR
            st.markdown(section_header("HISTORICAL PCR (30 Days)"), unsafe_allow_html=True)
            if not pcr_history.empty:
                fig_pcr = go.Figure()
                pcr_colors = [COLORS["bullish"] if v > 1.2 else (COLORS["bearish"] if v < 0.8 else COLORS["neutral"])
                              for v in pcr_history["pcr"]]
                fig_pcr.add_trace(go.Scatter(
                    x=pcr_history["date"].astype(str),
                    y=pcr_history["pcr"],
                    mode="lines",
                    name="PCR",
                    line=dict(color=COLORS["info"], width=2),
                    fill="tozeroy",
                    fillcolor="rgba(0,212,255,0.06)",
                ))
                fig_pcr.add_hline(y=1.2, line_color="rgba(0,230,118,0.4)",  line_dash="dash", line_width=1)
                fig_pcr.add_hline(y=0.8, line_color="rgba(255,68,68,0.4)",  line_dash="dash", line_width=1)
                fig_pcr.add_hline(y=1.0, line_color="rgba(255,214,0,0.3)", line_dash="dot",  line_width=1)
                fig_pcr.update_layout(
                    **plotly_layout(
                        height=280,
                        xaxis_title="Date",
                        yaxis_title="PCR",
                        yaxis=dict(range=[0.3, 2.2]),
                    )
                )
                st.plotly_chart(fig_pcr, use_container_width=True, config={"displayModeBar": False})

        # Strike-wise PCR
        st.markdown(section_header("STRIKE-WISE PCR"), unsafe_allow_html=True)
        sw_pcr = strike_wise_pcr(df_chain).sort_values("strike")
        fig_sw = go.Figure()
        sw_colors = [COLORS["bullish"] if v > 1.2 else (COLORS["bearish"] if v < 0.8 else COLORS["neutral"])
                     for v in sw_pcr["pcr"]]
        fig_sw.add_trace(go.Bar(
            x=sw_pcr["strike"].astype(str),
            y=sw_pcr["pcr"],
            marker_color=sw_colors,
            opacity=0.85,
            name="PCR",
        ))
        fig_sw.add_hline(y=1.0, line_color="rgba(255,214,0,0.4)", line_dash="dash", line_width=1.5)
        fig_sw.update_layout(
            **plotly_layout(
                height=280,
                xaxis_title="Strike",
                yaxis_title="PCR",
            )
        )
        st.plotly_chart(fig_sw, use_container_width=True, config={"displayModeBar": False})

"""
pages/volatility.py — IV analytics: IV Smile, IV Surface (3D), IV Rank gauge,
                       Volatility Cone, IV vs HV comparison, IV trend.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from src.config import COLORS, PLOTLY_TEMPLATE, INDICES, plotly_layout
from src.styles import section_header
from src.analytics.options import iv_rank, realized_volatility, volatility_cone
from src.data.generators import generate_iv_surface


def render(index: str, spot: float, df_chain: pd.DataFrame,
           ohlcv: pd.DataFrame, iv_history: pd.DataFrame):
    """Render the Volatility Dashboard page."""

    st.markdown(section_header("VOLATILITY DASHBOARD", INDICES[index]["display"]), unsafe_allow_html=True)

    if df_chain.empty:
        st.error("No data available.")
        return

    step = INDICES[index]["strike_step"]
    atm  = round(spot / step) * step

    # Compute key IV metrics
    atm_row   = df_chain[df_chain["strike"] == atm]
    atm_iv    = atm_row["call_iv"].values[0] if not atm_row.empty else df_chain["call_iv"].median()
    hv        = realized_volatility(ohlcv)
    ivr, ivp  = iv_rank(atm_iv, iv_history)

    # ── Summary row ───────────────────────────────────────────────────────────
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: st.metric("ATM IV",           f"{atm_iv:.1f}%")
    with m2: st.metric("Historical Vol",   f"{hv:.1f}%",   delta=f"IV Premium: {atm_iv - hv:.1f}%")
    with m3: st.metric("IV Rank",          f"{ivr:.1f}%",  delta="High" if ivr > 70 else ("Low" if ivr < 30 else "Normal"))
    with m4: st.metric("IV Percentile",    f"{ivp:.1f}%")
    with m5: st.metric("IV/HV Ratio",      f"{atm_iv / (hv or 1):.2f}x",
                         delta="Expensive" if atm_iv > hv * 1.2 else ("Cheap" if atm_iv < hv * 0.8 else "Fair"))

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "😊 IV Smile", "🌐 IV Surface", "📈 IV Trend",
        "🌀 Vol Cone",  "🌡️ IV Rank",
    ])

    # ── TAB 1: IV SMILE ───────────────────────────────────────────────────────
    with tab1:
        st.markdown(section_header("IMPLIED VOLATILITY SMILE"), unsafe_allow_html=True)
        df_sorted = df_chain.sort_values("strike")

        fig_smile = go.Figure()
        fig_smile.add_trace(go.Scatter(
            x=df_sorted["strike"],
            y=df_sorted["call_iv"],
            mode="lines+markers",
            name="Call IV",
            line=dict(color=COLORS["bullish"], width=2.5),
            marker=dict(size=7, symbol="circle",
                        line=dict(color=COLORS["bullish"], width=1)),
            hovertemplate="Strike: %{x}<br>Call IV: %{y:.2f}%<extra></extra>",
        ))
        fig_smile.add_trace(go.Scatter(
            x=df_sorted["strike"],
            y=df_sorted["put_iv"],
            mode="lines+markers",
            name="Put IV",
            line=dict(color=COLORS["bearish"], width=2.5),
            marker=dict(size=7, symbol="diamond",
                        line=dict(color=COLORS["bearish"], width=1)),
            hovertemplate="Strike: %{x}<br>Put IV: %{y:.2f}%<extra></extra>",
        ))
        # Fill between
        fig_smile.add_trace(go.Scatter(
            x=df_sorted["strike"].tolist() + df_sorted["strike"].tolist()[::-1],
            y=df_sorted["call_iv"].tolist() + df_sorted["put_iv"].tolist()[::-1],
            fill="toself",
            fillcolor="rgba(0,212,255,0.04)",
            line=dict(color="rgba(0,0,0,0)"),
            showlegend=False,
            name="IV Spread",
        ))
        fig_smile.add_vline(x=atm, line_color="rgba(255,214,0,0.5)", line_dash="dash",
                            annotation_text="ATM", annotation_font_color="#FFD600")
        fig_smile.update_layout(
            **plotly_layout(
                height=400,
                xaxis_title="Strike",
                yaxis_title="Implied Volatility (%)",
            )
        )
        st.plotly_chart(fig_smile, use_container_width=True, config={"displayModeBar": False})

        # Skew analysis
        col1, col2, col3 = st.columns(3)
        min_iv_strike = df_sorted.loc[df_sorted["call_iv"].idxmin(), "strike"]
        call_skew = df_sorted["call_iv"].max() - df_sorted["call_iv"].min()
        put_skew  = df_sorted["put_iv"].max()  - df_sorted["put_iv"].min()
        with col1: st.metric("Min IV Strike",   f"{min_iv_strike:,.0f}")
        with col2: st.metric("Call IV Range",   f"{call_skew:.2f}%")
        with col3: st.metric("Put Skew",        f"{put_skew:.2f}%", delta="Put premium" if put_skew > call_skew else "")

    # ── TAB 2: IV SURFACE ─────────────────────────────────────────────────────
    with tab2:
        st.markdown(section_header("IV SURFACE (3D)"), unsafe_allow_html=True)
        st.caption("Strike × Days to Expiry × Implied Volatility — simulated multi-expiry surface")

        strikes_2d, days_2d, iv_surf = generate_iv_surface(index, spot)

        fig_surf = go.Figure(go.Surface(
            x=strikes_2d,
            y=days_2d,
            z=iv_surf * 100,  # as %
            colorscale=[
                [0.0,  "#020614"],
                [0.3,  "#7C3AED"],
                [0.6,  "#00D4FF"],
                [0.85, "#00E676"],
                [1.0,  "#FFD600"],
            ],
            opacity=0.88,
            showscale=True,
            colorbar=dict(
                title="IV %",
                tickfont=dict(color="#8892A4"),
                titlefont=dict(color="#8892A4"),
            ),
            hovertemplate="Strike: %{x}<br>DTE: %{y:.0f}<br>IV: %{z:.2f}%<extra></extra>",
        ))
        fig_surf.update_layout(
            height=500,
            scene=dict(
                xaxis=dict(title="Strike", backgroundcolor="rgba(7,13,30,0.8)", gridcolor="rgba(255,255,255,0.05)", color="#8892A4"),
                yaxis=dict(title="DTE (days)", backgroundcolor="rgba(7,13,30,0.8)", gridcolor="rgba(255,255,255,0.05)", color="#8892A4"),
                zaxis=dict(title="IV %", backgroundcolor="rgba(7,13,30,0.8)", gridcolor="rgba(255,255,255,0.05)", color="#8892A4"),
                bgcolor="rgba(7,13,30,0.9)",
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8892A4", family="Inter"),
            margin=dict(l=0, r=0, t=20, b=0),
        )
        st.plotly_chart(fig_surf, use_container_width=True)

    # ── TAB 3: IV TREND ───────────────────────────────────────────────────────
    with tab3:
        st.markdown(section_header("IV TREND vs HISTORICAL VOLATILITY"), unsafe_allow_html=True)

        fig_trend = go.Figure()
        # IV history
        fig_trend.add_trace(go.Scatter(
            x=iv_history["date"].astype(str),
            y=iv_history["iv"],
            mode="lines",
            name="Implied Volatility",
            line=dict(color=COLORS["info"], width=2),
            fill="tozeroy",
            fillcolor="rgba(0,212,255,0.05)",
        ))
        # HV band (rolling 20-day HV from ohlcv)
        if not ohlcv.empty:
            ohlcv["log_ret"]  = np.log(ohlcv["close"] / ohlcv["close"].shift(1))
            ohlcv["hv_20"]    = ohlcv["log_ret"].rolling(20).std() * np.sqrt(252) * 100
            fig_trend.add_trace(go.Scatter(
                x=ohlcv["date"].astype(str),
                y=ohlcv["hv_20"],
                mode="lines",
                name="Realized Vol (20d)",
                line=dict(color=COLORS["warning"], width=2, dash="dot"),
            ))

        fig_trend.add_hline(y=atm_iv, line_color="rgba(0,230,118,0.4)", line_dash="dash",
                            annotation_text=f"Current IV: {atm_iv:.1f}%",
                            annotation_font_color=COLORS["bullish"])
        fig_trend.update_layout(
            **plotly_layout(
                height=380,
                xaxis_title="Date",
                yaxis_title="Volatility (%)",
            )
        )
        st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})

    # ── TAB 4: VOLATILITY CONE ────────────────────────────────────────────────
    with tab4:
        st.markdown(section_header("VOLATILITY CONE"), unsafe_allow_html=True)
        st.caption("Historical realized volatility percentile bands vs current IV")

        cone_df = volatility_cone(ohlcv)
        if not cone_df.empty:
            fig_cone = go.Figure()
            # 10-90 band
            fig_cone.add_trace(go.Scatter(
                x=cone_df["window"].tolist() + cone_df["window"].tolist()[::-1],
                y=cone_df["p90"].tolist() + cone_df["p10"].tolist()[::-1],
                fill="toself",
                fillcolor="rgba(0,212,255,0.05)",
                line=dict(color="rgba(0,0,0,0)"),
                name="10th–90th pctile",
                showlegend=True,
            ))
            # 25-75 band
            fig_cone.add_trace(go.Scatter(
                x=cone_df["window"].tolist() + cone_df["window"].tolist()[::-1],
                y=cone_df["p75"].tolist() + cone_df["p25"].tolist()[::-1],
                fill="toself",
                fillcolor="rgba(0,212,255,0.10)",
                line=dict(color="rgba(0,0,0,0)"),
                name="25th–75th pctile",
                showlegend=True,
            ))
            # Median
            fig_cone.add_trace(go.Scatter(
                x=cone_df["window"],
                y=cone_df["p50"],
                mode="lines",
                name="Median HV",
                line=dict(color=COLORS["info"], width=2),
            ))
            # Current HV
            fig_cone.add_trace(go.Scatter(
                x=cone_df["window"],
                y=cone_df["current"],
                mode="lines+markers",
                name="Current HV",
                line=dict(color=COLORS["warning"], width=2.5),
                marker=dict(size=8, symbol="star"),
            ))
            # ATM IV flat line
            fig_cone.add_trace(go.Scatter(
                x=cone_df["window"],
                y=[atm_iv] * len(cone_df),
                mode="lines",
                name=f"ATM IV ({atm_iv:.1f}%)",
                line=dict(color=COLORS["bullish"], width=2, dash="dash"),
            ))
            fig_cone.update_layout(
                **plotly_layout(
                    height=380,
                    xaxis=dict(title="Lookback Window (days)", tickvals=cone_df["window"].tolist()),
                    yaxis_title="Realized Volatility (%)",
                )
            )
            st.plotly_chart(fig_cone, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Insufficient historical data for volatility cone.")

    # ── TAB 5: IV RANK DASHBOARD ──────────────────────────────────────────────
    with tab5:
        st.markdown(section_header("IV RANK & PERCENTILE"), unsafe_allow_html=True)

        col_g, col_t = st.columns([1, 1])

        with col_g:
            # IV Rank gauge
            rank_color = COLORS["bearish"] if ivr > 70 else (COLORS["bullish"] if ivr < 30 else COLORS["neutral"])
            fig_ivr = go.Figure(go.Indicator(
                mode="gauge+number",
                value=ivr,
                title={"text": "IV Rank", "font": {"color": "#E8EAF0", "size": 14}},
                number={"suffix": "%", "font": {"color": rank_color, "size": 40, "family": "JetBrains Mono"}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#4A5568", "tickfont": {"color": "#4A5568"}},
                    "bar":  {"color": rank_color, "thickness": 0.3},
                    "bgcolor": "rgba(12,20,40,0.8)",
                    "steps": [
                        {"range": [0,  30], "color": "rgba(0,230,118,0.12)"},
                        {"range": [30, 70], "color": "rgba(255,214,0,0.08)"},
                        {"range": [70, 100],"color": "rgba(255,68,68,0.12)"},
                    ],
                },
            ))
            fig_ivr.update_layout(
                height=280, paper_bgcolor="rgba(0,0,0,0)",
                font={"color": "#8892A4"},
                margin=dict(l=20, r=20, t=40, b=20),
            )
            st.plotly_chart(fig_ivr, use_container_width=True, config={"displayModeBar": False})

            state = "HIGH — Consider selling options" if ivr > 70 else \
                    ("LOW — Consider buying options" if ivr < 30 else "NORMAL range")
            state_color = COLORS["bearish"] if ivr > 70 else (COLORS["bullish"] if ivr < 30 else COLORS["neutral"])
            st.markdown(f"""
            <div style="text-align:center;padding:12px;background:rgba(12,20,40,0.7);
                        border-radius:8px;border:1px solid rgba(255,255,255,0.06)">
                <div style="font-size:13px;font-weight:700;color:{state_color}">{state}</div>
                <div style="font-size:11px;color:#4A5568;margin-top:4px">
                    52W Low: {iv_history['iv'].min():.1f}% · High: {iv_history['iv'].max():.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_t:
            # IV distribution histogram
            st.markdown(section_header("IV DISTRIBUTION (1Y)"), unsafe_allow_html=True)
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(
                x=iv_history["iv"],
                nbinsx=30,
                marker_color=COLORS["info"],
                opacity=0.7,
                name="IV Distribution",
            ))
            fig_hist.add_vline(x=atm_iv, line_color=COLORS["bullish"], line_width=2,
                               annotation_text=f"Current: {atm_iv:.1f}%",
                               annotation_font_color=COLORS["bullish"])
            fig_hist.update_layout(
                **plotly_layout(
                    height=280,
                    xaxis_title="IV (%)",
                    yaxis_title="Frequency",
                )
            )
            st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

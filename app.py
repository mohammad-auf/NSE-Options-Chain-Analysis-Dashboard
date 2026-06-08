"""
app.py — Indian Stock Index Options Intelligence Dashboard
Main entry point. Run with: streamlit run app.py
"""

import sys
import os
import time
from datetime import datetime

import streamlit as st
import pandas as pd

# ── Path setup (allow src imports) ────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

# ── Page config (MUST be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Options Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Indian Stock Index Options Intelligence Dashboard — Institutional-grade trading terminal",
    },
)

# ── Imports ───────────────────────────────────────────────────────────────────
from src.styles import inject_css
from src.config import INDICES, DEFAULT_INDEX
from src.data.fetcher import NSEFetcher
from src.data.generators import (
    generate_expiry_dates,
    generate_ohlcv,
    generate_historical_pcr,
    generate_historical_iv,
    generate_max_pain_history,
    spot_summary,
    _get_spot,
)

# Page modules
from src.pages import dashboard, option_chain, oi_analytics, greeks_page, volatility, ai_signals, strategy, watchlist, settings as settings_page

# ── CSS Injection ─────────────────────────────────────────────────────────────
inject_css()

# ── Session State Init ────────────────────────────────────────────────────────
_SS_DEFAULTS = {
    "selected_index":   DEFAULT_INDEX,
    "selected_expiry":  "",
    "auto_refresh":     True,
    "refresh_interval": 30,
    "data_source":      "auto",
    "default_index":    DEFAULT_INDEX,
    "show_demo_banner": True,
    "strike_count":     20,
    "watchlist":        list(INDICES.keys()),
    "_fetcher":         None,
    "_last_fetch":      0,
    "_df_chain":        pd.DataFrame(),
    "_spot":            0.0,
    "_is_live":         False,
    "_expiry_dates":    [],
}
for k, v in _SS_DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Market Status ─────────────────────────────────────────────────────────────
def _market_status() -> tuple:
    """Return (is_open: bool, status_label: str)."""
    now = datetime.now()
    # Weekdays only
    if now.weekday() >= 5:
        return False, "Closed"
    h, m = now.hour, now.minute
    mins = h * 60 + m
    open_m  = 9 * 60 + 15
    close_m = 15 * 60 + 30
    if open_m <= mins < close_m:
        return True, "Open"
    elif mins < open_m:
        return False, "Pre-Open"
    else:
        return False, "Closed"


# ── Cached data loader ────────────────────────────────────────────────────────
@st.cache_data(ttl=25, show_spinner=False)
def _load_data(index: str, expiry: str, _force: int = 0):
    """Load option chain data. Cached for 25 seconds."""
    if st.session_state.get("_fetcher") is None:
        st.session_state["_fetcher"] = NSEFetcher()
    fetcher = st.session_state["_fetcher"]

    df_chain, spot, is_live = fetcher.fetch_chain(index, expiry)
    ohlcv    = generate_ohlcv(spot, n_days=30)
    pcr_hist = generate_historical_pcr(30)
    iv_hist  = generate_historical_iv(df_chain["call_iv"].median() if not df_chain.empty else 15.0)
    mp_hist  = generate_max_pain_history(spot)
    return df_chain, spot, is_live, ohlcv, pcr_hist, iv_hist, mp_hist


@st.cache_data(ttl=120, show_spinner=False)
def _load_expiry_dates(index: str):
    if st.session_state.get("_fetcher") is None:
        st.session_state["_fetcher"] = NSEFetcher()
    fetcher  = st.session_state["_fetcher"]
    expiries = fetcher.get_expiry_dates(index)
    return expiries if expiries else generate_expiry_dates(index, 5)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown("""
    <div style="padding:16px 8px 20px 8px;border-bottom:1px solid rgba(0,212,255,0.08);margin-bottom:8px">
        <div style="font-size:18px;font-weight:800;color:#E8EAF0;letter-spacing:-0.5px">
            📊 Options<span style="color:#00D4FF">IQ</span>
        </div>
        <div style="font-size:10px;color:#4A5568;letter-spacing:2px;text-transform:uppercase;margin-top:3px">
            Intelligence Dashboard
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation — use option_menu if available, else selectbox fallback
    try:
        from streamlit_option_menu import option_menu
        selected_page = option_menu(
            menu_title=None,
            options=[
                "Dashboard", "Option Chain", "OI Analytics",
                "Greeks", "Volatility", "AI Signals",
                "Strategy Builder", "Watchlist", "Settings",
            ],
            icons=[
                "house-fill", "graph-up-arrow", "fire",
                "lightning-charge-fill", "bar-chart-fill", "robot",
                "tools", "bookmark-star-fill", "gear-fill",
            ],
            default_index=0,
            styles={
                "container":         {"padding": "4px 0", "background-color": "transparent"},
                "icon":              {"color": "#4A5568", "font-size": "15px"},
                "nav-link":          {"font-size": "13px", "text-align": "left", "margin": "2px 0",
                                      "padding": "9px 14px", "--hover-color": "rgba(0,212,255,0.08)"},
                "nav-link-selected": {"background-color": "rgba(0,212,255,0.12)",
                                      "color": "#00D4FF", "font-weight": "600",
                                      "border-left": "3px solid #00D4FF"},
            },
        )
    except ImportError:
        selected_page = st.selectbox(
            "Navigation",
            ["Dashboard", "Option Chain", "OI Analytics", "Greeks", "Volatility",
             "AI Signals", "Strategy Builder", "Watchlist", "Settings"],
        )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.divider()

    # ── Index & Expiry selectors ───────────────────────────────────────────
    st.markdown("<div style='font-size:10px;color:#4A5568;font-weight:600;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:8px'>SELECT INDEX</div>", unsafe_allow_html=True)

    idx_options  = list(INDICES.keys())
    idx_labels   = [INDICES[k]["display"] for k in idx_options]
    current_idx  = idx_options.index(st.session_state.selected_index) if st.session_state.selected_index in idx_options else 0

    sel_idx_label = st.selectbox(
        "Index", idx_labels, index=current_idx, label_visibility="collapsed"
    )
    selected_index = idx_options[idx_labels.index(sel_idx_label)]
    if selected_index != st.session_state.selected_index:
        st.session_state.selected_index = selected_index
        st.session_state._df_chain = pd.DataFrame()
        st.cache_data.clear()

    # Expiry
    st.markdown("<div style='font-size:10px;color:#4A5568;font-weight:600;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:8px;margin-top:12px'>SELECT EXPIRY</div>", unsafe_allow_html=True)
    expiry_dates = _load_expiry_dates(selected_index)
    if expiry_dates:
        sel_expiry = st.selectbox(
            "Expiry", expiry_dates, label_visibility="collapsed"
        )
    else:
        sel_expiry = generate_expiry_dates(selected_index, 1)[0]
        st.caption(sel_expiry)
    st.session_state.selected_expiry = sel_expiry

    st.divider()

    # ── Auto-refresh ───────────────────────────────────────────────────────
    auto_ref = st.toggle("⚡ Auto Refresh", value=st.session_state.auto_refresh)
    st.session_state.auto_refresh = auto_ref

    if auto_ref:
        try:
            from streamlit_autorefresh import st_autorefresh
            st_autorefresh(
                interval=st.session_state.refresh_interval * 1000,
                limit=None,
                key="main_autorefresh",
            )
        except ImportError:
            pass

    # ── Market status + refresh button ────────────────────────────────────
    is_open, mkt_label = _market_status()
    status_cls = "open" if is_open else "closed"
    st.markdown(f"""
    <div style="margin:12px 0 8px 0">
        <div class="market-status {status_cls}">{mkt_label}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 Refresh Now", key="sidebar_refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    # Last updated
    st.markdown(f"""
    <div style="font-size:10px;color:#4A5568;text-align:center;margin-top:8px;
                font-family:'JetBrains Mono',monospace">
        {datetime.now().strftime('%H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)


# ── DATA LOAD ─────────────────────────────────────────────────────────────────
with st.spinner("📡 Loading options data..."):
    df_chain, spot, is_live, ohlcv, pcr_hist, iv_hist, mp_hist = _load_data(
        st.session_state.selected_index,
        st.session_state.selected_expiry,
    )

# Show demo warning if applicable
if not is_live and st.session_state.get("show_demo_banner", True):
    st.warning(
        "⚠️ **Demo Mode** — NSE data unavailable (market closed or request blocked). "
        "Displaying realistic simulated data using Black-Scholes pricing.",
        icon="📊",
    )

# ── PAGE ROUTING ──────────────────────────────────────────────────────────────
idx = st.session_state.selected_index

if selected_page == "Dashboard":
    dashboard.render(idx, spot, df_chain, ohlcv, is_live, iv_hist)

elif selected_page == "Option Chain":
    option_chain.render(idx, spot, df_chain)

elif selected_page == "OI Analytics":
    oi_analytics.render(idx, spot, df_chain, pcr_hist, mp_hist)

elif selected_page == "Greeks":
    greeks_page.render(idx, spot, df_chain)

elif selected_page == "Volatility":
    volatility.render(idx, spot, df_chain, ohlcv, iv_hist)

elif selected_page == "AI Signals":
    ai_signals.render(idx, spot, df_chain, ohlcv, iv_hist)

elif selected_page == "Strategy Builder":
    strategy.render(idx, spot, df_chain)

elif selected_page == "Watchlist":
    watchlist.render()

elif selected_page == "Settings":
    settings_page.render()

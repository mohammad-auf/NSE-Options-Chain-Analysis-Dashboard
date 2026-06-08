"""
pages/settings.py — Dashboard preferences: refresh interval, data source, about.
"""

import streamlit as st
from src.config import COLORS, INDICES
from src.styles import section_header


def render():
    """Render the Settings page."""
    st.markdown(section_header("SETTINGS", "Dashboard Preferences"), unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔄 Data & Refresh")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        auto_refresh = st.toggle(
            "Auto Refresh",
            value=st.session_state.get("auto_refresh", True),
            key="settings_auto_refresh",
        )
        st.session_state.auto_refresh = auto_refresh

        interval = st.select_slider(
            "Refresh Interval",
            options=[15, 30, 60, 120, 300],
            value=st.session_state.get("refresh_interval", 30),
            format_func=lambda x: f"{x}s" if x < 60 else f"{x//60}m",
            disabled=not auto_refresh,
        )
        st.session_state.refresh_interval = interval

        st.divider()
        st.markdown("#### 📡 Data Source")
        data_src = st.radio(
            "Primary Data Source",
            ["Auto (Live → Demo)", "Demo Mode Only"],
            index=0 if st.session_state.get("data_source", "auto") == "auto" else 1,
        )
        st.session_state.data_source = "auto" if "Auto" in data_src else "demo"

        if st.button("🗑️ Clear Cache", key="clear_cache"):
            st.cache_data.clear()
            st.success("Cache cleared!")

    with col2:
        st.markdown("#### 📊 Default Index")
        default_idx = st.selectbox(
            "Default Index on Load",
            list(INDICES.keys()),
            format_func=lambda k: INDICES[k]["display"],
            index=list(INDICES.keys()).index(st.session_state.get("default_index", "NIFTY")),
        )
        st.session_state.default_index = default_idx

        st.divider()
        st.markdown("#### 🎨 Display Options")
        show_demo_banner = st.toggle(
            "Show Demo Mode Banner",
            value=st.session_state.get("show_demo_banner", True),
        )
        st.session_state.show_demo_banner = show_demo_banner

        strike_count = st.slider(
            "Option Chain Strike Count",
            min_value=10, max_value=25, value=st.session_state.get("strike_count", 20), step=5,
        )
        st.session_state.strike_count = strike_count

    # ── About ─────────────────────────────────────────────────────────────────
    st.divider()
    st.markdown(section_header("ABOUT"), unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(12,20,40,0.9);border:1px solid rgba(0,212,255,0.1);
                border-radius:12px;padding:24px;line-height:1.8">
        <div style="font-size:18px;font-weight:700;color:#E8EAF0;margin-bottom:6px">
            📊 Indian Stock Index Options Intelligence Dashboard
        </div>
        <div style="font-size:12px;color:#4A5568;margin-bottom:16px">
            Institutional-grade Options Analytics Terminal
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
            <div>
                <div style="font-size:11px;font-weight:600;color:#4A5568;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">Features</div>
                <ul style="list-style:none;padding:0;margin:0">
                    <li style="color:#8892A4;font-size:13px;margin:4px 0">✅ Live NSE Data (with session handling)</li>
                    <li style="color:#8892A4;font-size:13px;margin:4px 0">✅ Black-Scholes Greeks Engine</li>
                    <li style="color:#8892A4;font-size:13px;margin:4px 0">✅ Multi-factor AI Sentiment</li>
                    <li style="color:#8892A4;font-size:13px;margin:4px 0">✅ 8 Strategy Payoff Diagrams</li>
                    <li style="color:#8892A4;font-size:13px;margin:4px 0">✅ IV Surface (3D)</li>
                    <li style="color:#8892A4;font-size:13px;margin:4px 0">✅ Gamma Wall Detection</li>
                    <li style="color:#8892A4;font-size:13px;margin:4px 0">✅ Smart Money Tracker</li>
                    <li style="color:#8892A4;font-size:13px;margin:4px 0">✅ Volatility Cone</li>
                </ul>
            </div>
            <div>
                <div style="font-size:11px;font-weight:600;color:#4A5568;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">Stack</div>
                <ul style="list-style:none;padding:0;margin:0">
                    <li style="color:#8892A4;font-size:13px;margin:4px 0">🐍 Python + Streamlit</li>
                    <li style="color:#8892A4;font-size:13px;margin:4px 0">📊 Plotly (interactive charts)</li>
                    <li style="color:#8892A4;font-size:13px;margin:4px 0">🧮 SciPy (Black-Scholes)</li>
                    <li style="color:#8892A4;font-size:13px;margin:4px 0">🐼 Pandas + NumPy</li>
                    <li style="color:#8892A4;font-size:13px;margin:4px 0">🔗 NSE India API</li>
                </ul>
            </div>
        </div>
        <div style="margin-top:20px;padding:12px;background:rgba(255,152,0,0.06);
                    border:1px solid rgba(255,152,0,0.2);border-radius:8px">
            <div style="font-size:12px;color:#FF9800">
                ⚠️ <strong>Disclaimer:</strong> This dashboard is for educational and informational purposes only.
                It does not constitute financial advice. Options trading involves significant risk.
                Always consult a SEBI-registered investment advisor before making trading decisions.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

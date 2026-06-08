"""
styles.py — Premium Bloomberg/TradingView-inspired dark theme CSS
Injected via st.markdown(inject_css(), unsafe_allow_html=True)
"""

import streamlit as st

_CSS = """
<style>
/* ══════════════════════════════════════════════════════════════════════════════
   FONTS
══════════════════════════════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ══════════════════════════════════════════════════════════════════════════════
   GLOBAL RESET
══════════════════════════════════════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ══════════════════════════════════════════════════════════════════════════════
   HIDE STREAMLIT UI CHROME
══════════════════════════════════════════════════════════════════════════════ */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
.stDeployButton { visibility: hidden !important; display: none !important; }

/* ══════════════════════════════════════════════════════════════════════════════
   APP BACKGROUND
══════════════════════════════════════════════════════════════════════════════ */
.stApp {
    background: #020614 !important;
    background-image:
        radial-gradient(ellipse at 20% 10%, rgba(0, 212, 255, 0.04) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 90%, rgba(124, 58, 237, 0.04) 0%, transparent 50%) !important;
}

.main .block-container {
    padding: 1rem 1.5rem 2rem 1.5rem !important;
    max-width: 100% !important;
}

/* ══════════════════════════════════════════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060B18 0%, #0A1020 100%) !important;
    border-right: 1px solid rgba(0, 212, 255, 0.1) !important;
}

[data-testid="stSidebar"] .block-container {
    padding: 1rem 0.5rem !important;
}

[data-testid="stSidebarNav"] { display: none; }

/* ══════════════════════════════════════════════════════════════════════════════
   OPTION MENU (streamlit-option-menu)
══════════════════════════════════════════════════════════════════════════════ */
.nav-link {
    color: #8892A4 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    margin: 2px 0 !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.3px !important;
}

.nav-link:hover {
    background: rgba(0, 212, 255, 0.08) !important;
    color: #00D4FF !important;
}

.nav-link.active {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(0, 212, 255, 0.05) 100%) !important;
    color: #00D4FF !important;
    border-left: 3px solid #00D4FF !important;
    font-weight: 600 !important;
}

.nav-link .icon { font-size: 16px !important; }

/* ══════════════════════════════════════════════════════════════════════════════
   METRIC CARDS
══════════════════════════════════════════════════════════════════════════════ */
.kpi-card {
    background: linear-gradient(135deg, rgba(12, 20, 40, 0.95) 0%, rgba(7, 13, 30, 0.95) 100%);
    border: 1px solid rgba(0, 212, 255, 0.12);
    border-radius: 12px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s ease, transform 0.2s ease;
    backdrop-filter: blur(20px);
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.4), transparent);
}

.kpi-card:hover {
    border-color: rgba(0, 212, 255, 0.3);
    transform: translateY(-1px);
}

.kpi-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #4A5568;
    margin-bottom: 8px;
}

.kpi-value {
    font-size: 24px;
    font-weight: 700;
    color: #E8EAF0;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: -0.5px;
    line-height: 1;
    margin-bottom: 6px;
}

.kpi-delta {
    font-size: 12px;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}

.kpi-icon {
    position: absolute;
    top: 16px; right: 16px;
    font-size: 20px;
    opacity: 0.3;
}

.kpi-card.bullish { border-color: rgba(0, 230, 118, 0.2); }
.kpi-card.bullish::before { background: linear-gradient(90deg, transparent, rgba(0, 230, 118, 0.5), transparent); }
.kpi-card.bearish { border-color: rgba(255, 68, 68, 0.2); }
.kpi-card.bearish::before { background: linear-gradient(90deg, transparent, rgba(255, 68, 68, 0.5), transparent); }
.kpi-card.neutral { border-color: rgba(255, 214, 0, 0.2); }
.kpi-card.neutral::before { background: linear-gradient(90deg, transparent, rgba(255, 214, 0, 0.5), transparent); }
.kpi-card.info { border-color: rgba(0, 212, 255, 0.25); }
.kpi-card.info::before { background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.6), transparent); }

/* ══════════════════════════════════════════════════════════════════════════════
   SECTION HEADERS
══════════════════════════════════════════════════════════════════════════════ */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 28px 0 16px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(0, 212, 255, 0.08);
}

.section-header h2 {
    font-size: 15px;
    font-weight: 700;
    color: #E8EAF0;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 0;
}

.section-header .badge {
    font-size: 10px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 20px;
    background: rgba(0, 212, 255, 0.1);
    color: #00D4FF;
    border: 1px solid rgba(0, 212, 255, 0.2);
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* ══════════════════════════════════════════════════════════════════════════════
   SENTIMENT BANNER
══════════════════════════════════════════════════════════════════════════════ */
.sentiment-banner {
    border-radius: 12px;
    padding: 20px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}

.sentiment-banner.strong-bullish {
    background: linear-gradient(135deg, rgba(0, 230, 118, 0.15) 0%, rgba(0, 200, 83, 0.08) 100%);
    border: 1px solid rgba(0, 230, 118, 0.3);
}

.sentiment-banner.bullish {
    background: linear-gradient(135deg, rgba(0, 230, 118, 0.1) 0%, rgba(0, 200, 83, 0.04) 100%);
    border: 1px solid rgba(0, 230, 118, 0.2);
}

.sentiment-banner.neutral {
    background: linear-gradient(135deg, rgba(255, 214, 0, 0.1) 0%, rgba(255, 152, 0, 0.04) 100%);
    border: 1px solid rgba(255, 214, 0, 0.2);
}

.sentiment-banner.bearish {
    background: linear-gradient(135deg, rgba(255, 68, 68, 0.1) 0%, rgba(211, 47, 47, 0.04) 100%);
    border: 1px solid rgba(255, 68, 68, 0.2);
}

.sentiment-banner.strong-bearish {
    background: linear-gradient(135deg, rgba(255, 68, 68, 0.15) 0%, rgba(211, 47, 47, 0.08) 100%);
    border: 1px solid rgba(255, 68, 68, 0.3);
}

/* ══════════════════════════════════════════════════════════════════════════════
   SIGNAL CARDS
══════════════════════════════════════════════════════════════════════════════ */
.signal-card {
    background: linear-gradient(135deg, rgba(12, 20, 40, 0.98) 0%, rgba(7, 13, 30, 0.98) 100%);
    border: 1px solid rgba(0, 212, 255, 0.12);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}

.signal-card.buy-call {
    border-left: 4px solid #00E676;
    border-color: rgba(0, 230, 118, 0.25);
}

.signal-card.buy-put {
    border-left: 4px solid #FF4444;
    border-color: rgba(255, 68, 68, 0.25);
}

.signal-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
}

.signal-direction {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 4px;
    display: inline-block;
    margin-bottom: 10px;
}

.signal-direction.buy-call {
    background: rgba(0, 230, 118, 0.15);
    color: #00E676;
    border: 1px solid rgba(0, 230, 118, 0.3);
}

.signal-direction.buy-put {
    background: rgba(255, 68, 68, 0.15);
    color: #FF4444;
    border: 1px solid rgba(255, 68, 68, 0.3);
}

.signal-strike {
    font-size: 22px;
    font-weight: 800;
    color: #E8EAF0;
    font-family: 'JetBrains Mono', monospace;
    margin: 6px 0;
}

.signal-meta {
    display: flex;
    gap: 16px;
    margin: 12px 0;
    flex-wrap: wrap;
}

.signal-meta-item {
    text-align: center;
}

.signal-meta-item .label {
    font-size: 10px;
    color: #4A5568;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

.signal-meta-item .value {
    font-size: 14px;
    font-weight: 700;
    color: #E8EAF0;
    font-family: 'JetBrains Mono', monospace;
}

.confidence-bar {
    height: 4px;
    border-radius: 2px;
    background: rgba(255, 255, 255, 0.06);
    margin-top: 12px;
    overflow: hidden;
}

.confidence-fill {
    height: 100%;
    border-radius: 2px;
    transition: width 0.8s ease;
}

/* ══════════════════════════════════════════════════════════════════════════════
   SMART MONEY ALERT
══════════════════════════════════════════════════════════════════════════════ */
.smart-money-alert {
    background: rgba(12, 20, 40, 0.9);
    border: 1px solid rgba(124, 58, 237, 0.25);
    border-left: 3px solid #7C3AED;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 12px;
    transition: all 0.2s ease;
}

.smart-money-alert:hover {
    background: rgba(124, 58, 237, 0.06);
    border-color: rgba(124, 58, 237, 0.4);
}

.alert-icon { font-size: 18px; }
.alert-text { font-size: 13px; color: #8892A4; }
.alert-text strong { color: #E8EAF0; }
.alert-time { font-size: 11px; color: #4A5568; font-family: 'JetBrains Mono', monospace; margin-left: auto; }

/* ══════════════════════════════════════════════════════════════════════════════
   OI ACTIVITY BADGES
══════════════════════════════════════════════════════════════════════════════ */
.oi-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.oi-badge.long-buildup {
    background: rgba(0, 230, 118, 0.12);
    color: #00E676;
    border: 1px solid rgba(0, 230, 118, 0.25);
}

.oi-badge.short-buildup {
    background: rgba(255, 68, 68, 0.12);
    color: #FF4444;
    border: 1px solid rgba(255, 68, 68, 0.25);
}

.oi-badge.short-covering {
    background: rgba(0, 212, 255, 0.12);
    color: #00D4FF;
    border: 1px solid rgba(0, 212, 255, 0.25);
}

.oi-badge.long-unwinding {
    background: rgba(255, 152, 0, 0.12);
    color: #FF9800;
    border: 1px solid rgba(255, 152, 0, 0.25);
}

/* ══════════════════════════════════════════════════════════════════════════════
   HEADER BAR
══════════════════════════════════════════════════════════════════════════════ */
.top-header {
    background: linear-gradient(135deg, rgba(12, 20, 40, 0.97) 0%, rgba(6, 11, 24, 0.97) 100%);
    border: 1px solid rgba(0, 212, 255, 0.1);
    border-radius: 12px;
    padding: 14px 20px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 20px;
    backdrop-filter: blur(20px);
    position: sticky;
    top: 0;
    z-index: 100;
}

.market-status {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.market-status.open {
    background: rgba(0, 230, 118, 0.12);
    color: #00E676;
    border: 1px solid rgba(0, 230, 118, 0.25);
}

.market-status.open::before {
    content: '';
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #00E676;
    animation: pulse-green 1.5s infinite;
}

.market-status.closed {
    background: rgba(255, 68, 68, 0.1);
    color: #FF4444;
    border: 1px solid rgba(255, 68, 68, 0.2);
}

.market-status.closed::before {
    content: '';
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #FF4444;
}

@keyframes pulse-green {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(1.3); }
}

/* ══════════════════════════════════════════════════════════════════════════════
   STREAMLIT NATIVE OVERRIDES
══════════════════════════════════════════════════════════════════════════════ */
/* Metric widget */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(12, 20, 40, 0.95), rgba(7, 13, 30, 0.95));
    border: 1px solid rgba(0, 212, 255, 0.1);
    border-radius: 10px;
    padding: 14px 16px;
}

[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    color: #4A5568 !important;
}

[data-testid="stMetricValue"] {
    font-size: 20px !important;
    font-weight: 700 !important;
    color: #E8EAF0 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

[data-testid="stMetricDelta"] {
    font-size: 12px !important;
    font-weight: 600 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(7, 13, 30, 0.8) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 2px !important;
    border: 1px solid rgba(0, 212, 255, 0.08) !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: #8892A4 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    border: none !important;
    transition: all 0.2s ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(0, 212, 255, 0.06) !important;
    color: #E8EAF0 !important;
}

.stTabs [aria-selected="true"] {
    background: rgba(0, 212, 255, 0.12) !important;
    color: #00D4FF !important;
    font-weight: 600 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.12) 0%, rgba(0, 212, 255, 0.06) 100%) !important;
    color: #00D4FF !important;
    border: 1px solid rgba(0, 212, 255, 0.3) !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 8px 20px !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.3px !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.2) 0%, rgba(0, 212, 255, 0.1) 100%) !important;
    border-color: rgba(0, 212, 255, 0.5) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(0, 212, 255, 0.15) !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: rgba(12, 20, 40, 0.95) !important;
    border: 1px solid rgba(0, 212, 255, 0.2) !important;
    border-radius: 8px !important;
    color: #E8EAF0 !important;
    font-size: 13px !important;
}

/* Slider */
.stSlider > div > div {
    color: #00D4FF !important;
}

/* Checkbox */
.stCheckbox label {
    color: #8892A4 !important;
    font-size: 13px !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: rgba(12, 20, 40, 0.8) !important;
    border: 1px solid rgba(0, 212, 255, 0.1) !important;
    border-radius: 8px !important;
    color: #E8EAF0 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}

/* DataFrames */
.stDataFrame { border-radius: 10px; overflow: hidden; }
[data-testid="stDataFrameResizable"] { border-radius: 10px; }

/* Info / Warning / Error boxes */
.stInfo { background: rgba(0, 212, 255, 0.06) !important; border-color: rgba(0, 212, 255, 0.2) !important; color: #8892A4 !important; border-radius: 8px !important; }
.stWarning { background: rgba(255, 152, 0, 0.06) !important; border-color: rgba(255, 152, 0, 0.2) !important; border-radius: 8px !important; }
.stSuccess { background: rgba(0, 230, 118, 0.06) !important; border-color: rgba(0, 230, 118, 0.2) !important; border-radius: 8px !important; }
.stError { background: rgba(255, 68, 68, 0.06) !important; border-color: rgba(255, 68, 68, 0.2) !important; border-radius: 8px !important; }

/* Divider */
hr { border-color: rgba(0, 212, 255, 0.08) !important; margin: 1.5rem 0 !important; }

/* ══════════════════════════════════════════════════════════════════════════════
   SUPPORT / RESISTANCE BARS
══════════════════════════════════════════════════════════════════════════════ */
.sr-level {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 8px;
    background: rgba(12, 20, 40, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.sr-level.support {
    border-left: 3px solid #00E676;
}

.sr-level.resistance {
    border-left: 3px solid #FF4444;
}

.sr-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    width: 80px;
}

.sr-label.support { color: #00E676; }
.sr-label.resistance { color: #FF4444; }

.sr-price {
    font-size: 18px;
    font-weight: 700;
    color: #E8EAF0;
    font-family: 'JetBrains Mono', monospace;
    flex: 1;
}

.sr-strength-bar {
    height: 6px;
    border-radius: 3px;
    width: 80px;
    background: rgba(255,255,255,0.06);
    overflow: hidden;
}

.sr-strength-fill {
    height: 100%;
    border-radius: 3px;
}

.sr-strength-fill.support { background: linear-gradient(90deg, #00C853, #00E676); }
.sr-strength-fill.resistance { background: linear-gradient(90deg, #D32F2F, #FF4444); }

.sr-pct { font-size: 12px; color: #4A5568; font-family: 'JetBrains Mono', monospace; }

/* ══════════════════════════════════════════════════════════════════════════════
   STRATEGY BUILDER
══════════════════════════════════════════════════════════════════════════════ */
.strategy-metric {
    background: rgba(12, 20, 40, 0.9);
    border: 1px solid rgba(0, 212, 255, 0.1);
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}

.strategy-metric .s-label {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #4A5568;
    margin-bottom: 8px;
}

.strategy-metric .s-value {
    font-size: 18px;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    color: #E8EAF0;
}

/* ══════════════════════════════════════════════════════════════════════════════
   LIVE DATA TAG
══════════════════════════════════════════════════════════════════════════════ */
.live-tag {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #00E676;
    padding: 3px 8px;
    border-radius: 4px;
    background: rgba(0, 230, 118, 0.1);
    border: 1px solid rgba(0, 230, 118, 0.25);
}

.live-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #00E676;
    animation: pulse-green 1.5s infinite;
}

.demo-tag {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #FF9800;
    padding: 3px 8px;
    border-radius: 4px;
    background: rgba(255, 152, 0, 0.1);
    border: 1px solid rgba(255, 152, 0, 0.25);
}

/* ══════════════════════════════════════════════════════════════════════════════
   WATCHLIST TABLE
══════════════════════════════════════════════════════════════════════════════ */
.watchlist-row {
    display: grid;
    grid-template-columns: 1fr 1.5fr 1fr 1fr 1fr 1fr;
    gap: 10px;
    align-items: center;
    padding: 14px 16px;
    border-radius: 8px;
    background: rgba(12, 20, 40, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.04);
    margin-bottom: 8px;
    transition: all 0.2s ease;
}

.watchlist-row:hover {
    background: rgba(0, 212, 255, 0.04);
    border-color: rgba(0, 212, 255, 0.12);
}

.watchlist-header {
    display: grid;
    grid-template-columns: 1fr 1.5fr 1fr 1fr 1fr 1fr;
    gap: 10px;
    padding: 8px 16px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #4A5568;
    margin-bottom: 4px;
}

/* ══════════════════════════════════════════════════════════════════════════════
   SCROLLBAR
══════════════════════════════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: rgba(7, 13, 30, 0.5); }
::-webkit-scrollbar-thumb { background: rgba(0, 212, 255, 0.2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0, 212, 255, 0.35); }

/* ══════════════════════════════════════════════════════════════════════════════
   TYPOGRAPHY
══════════════════════════════════════════════════════════════════════════════ */
h1, h2, h3, h4, h5, h6 {
    color: #E8EAF0 !important;
    font-family: 'Inter', sans-serif !important;
}

p, span, div, label {
    color: #8892A4;
}

code, pre {
    font-family: 'JetBrains Mono', monospace !important;
    color: #00D4FF !important;
    background: rgba(0, 212, 255, 0.06) !important;
    border-radius: 4px !important;
}

/* ══════════════════════════════════════════════════════════════════════════════
   ANIMATIONS
══════════════════════════════════════════════════════════════════════════════ */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

.fade-in-up {
    animation: fadeInUp 0.4s ease forwards;
}

/* Dashboard logo/title */
.dashboard-title {
    font-size: 20px;
    font-weight: 800;
    color: #E8EAF0;
    letter-spacing: -0.5px;
    line-height: 1.1;
}

.dashboard-subtitle {
    font-size: 11px;
    font-weight: 500;
    color: #4A5568;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

/* Index badge on sidebar */
.index-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.5px;
    margin: 4px 0;
    background: rgba(0, 212, 255, 0.1);
    color: #00D4FF;
    border: 1px solid rgba(0, 212, 255, 0.2);
}
</style>
"""


def inject_css():
    """Inject the premium CSS into the Streamlit app."""
    st.markdown(_CSS, unsafe_allow_html=True)


def kpi_card(label: str, value: str, delta: str = "", delta_color: str = "",
             icon: str = "", card_class: str = "info") -> str:
    """Return HTML for a premium KPI card."""
    delta_style = f"color: {delta_color};" if delta_color else ""
    delta_html = f'<div class="kpi-delta" style="{delta_style}">{delta}</div>' if delta else ""
    icon_html = f'<div class="kpi-icon">{icon}</div>' if icon else ""
    return f"""
    <div class="kpi-card {card_class}">
        {icon_html}
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """


def section_header(title: str, badge: str = "") -> str:
    """Return HTML for a section header."""
    badge_html = f'<span class="badge">{badge}</span>' if badge else ""
    return f"""
    <div class="section-header">
        <h2>{title}</h2>
        {badge_html}
    </div>
    """


def sentiment_html(sentiment: str, confidence: float, reasoning: list) -> str:
    """Return HTML for sentiment banner."""
    css_class = sentiment.lower().replace(" ", "-")
    color_map = {
        "strong-bullish": "#00E676",
        "bullish": "#00C853",
        "neutral": "#FFD600",
        "bearish": "#FF6B6B",
        "strong-bearish": "#FF4444",
    }
    emoji_map = {
        "strong-bullish": "🚀",
        "bullish": "📈",
        "neutral": "↔️",
        "bearish": "📉",
        "strong-bearish": "🔻",
    }
    color = color_map.get(css_class, "#00D4FF")
    emoji = emoji_map.get(css_class, "📊")
    reasons = "".join(f"<li style='color:#8892A4;font-size:12px;margin:3px 0'>• {r}</li>" for r in reasoning)
    return f"""
    <div class="sentiment-banner {css_class}">
        <div>
            <div style="font-size:11px;font-weight:700;letter-spacing:1.5px;color:#4A5568;text-transform:uppercase;margin-bottom:6px">Market Sentiment</div>
            <div style="font-size:26px;font-weight:800;color:{color};letter-spacing:-0.5px">{emoji} {sentiment.upper()}</div>
            <ul style="list-style:none;padding:0;margin:10px 0 0 0">{reasons}</ul>
        </div>
        <div style="text-align:center;padding:16px 20px;background:rgba(0,0,0,0.2);border-radius:10px;min-width:100px">
            <div style="font-size:11px;font-weight:600;color:#4A5568;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Confidence</div>
            <div style="font-size:36px;font-weight:800;color:{color};font-family:'JetBrains Mono',monospace">{confidence:.0f}%</div>
        </div>
    </div>
    """

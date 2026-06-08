import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urlencode

# Set page config
st.set_page_config(
    page_title="Indian Options Chain Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better aesthetics
st.markdown("""
    <style>
        :root {
            --primary: #0F766E;
            --secondary: #DC2626;
            --accent: #EEFF00;
            --dark: #0F172A;
            --light: #F8FAFC;
        }
        
        .main {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F766E 100%);
            padding: 20px;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 28px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        
        [data-testid="stMetricDelta"] {
            font-size: 14px;
            font-weight: 600;
        }
        
        .metric-card {
            background: rgba(15, 23, 42, 0.8);
            border: 2px solid rgba(15, 118, 110, 0.3);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
        }
        
        .bullish {
            color: #10B981;
            border-left: 4px solid #10B981;
        }
        
        .bearish {
            color: #DC2626;
            border-left: 4px solid #DC2626;
        }
        
        .neutral {
            color: #F59E0B;
            border-left: 4px solid #F59E0B;
        }
        
        h1 {
            color: #EEFF00;
            font-weight: 800;
            letter-spacing: -1px;
            margin-bottom: 30px;
        }
        
        h2 {
            color: #EEFF00;
            font-weight: 700;
            margin-top: 30px;
            margin-bottom: 20px;
        }
        
        h3 {
            color: #0F766E;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# ==================== DATA FETCHING ====================

def _generate_demo_data(index="NIFTY"):
    """Generate realistic demo option chain data when NSE is unreachable."""
    base_prices = {
        "NIFTY": 24500, "NIFTYNXT50": 70000, "NIFTYIT": 36000,
        "NIFTYPHARMA": 22000, "NIFTYBANK": 52000,
    }
    base = base_prices.get(index, 24500)
    step = base // 500  # strike interval

    # Generate strikes around current price
    strikes = [base + (i - 10) * step for i in range(21)]
    rng = np.random.default_rng(42)

    rows = []
    for i, strike in enumerate(strikes):
        dist = abs(strike - base) / step  # distance from ATM in steps
        # OI peaks at ATM and 2-3 steps away (realistic distribution)
        call_oi = int(max(500, rng.normal(5000 - dist * 800, 600)))
        put_oi  = int(max(500, rng.normal(4800 - dist * 700, 550)))
        call_iv = round(max(8, rng.normal(14 + dist * 0.6, 1.2)), 2)
        put_iv  = round(max(8, rng.normal(15 + dist * 0.7, 1.3)), 2)
        call_ltp = round(max(0.5, (base - strike + 300) * 0.3 + rng.uniform(-5, 5)), 2) if strike <= base else round(rng.uniform(2, 80), 2)
        put_ltp  = round(max(0.5, (strike - base + 300) * 0.3 + rng.uniform(-5, 5)), 2) if strike >= base else round(rng.uniform(2, 80), 2)
        rows.append({
            'strike': strike,
            'call_oi': call_oi, 'call_iv': call_iv, 'call_ltp': call_ltp,
            'call_bid': round(call_ltp - 0.5, 2), 'call_ask': round(call_ltp + 0.5, 2),
            'call_volume': int(rng.integers(1000, 20000)),
            'put_oi': put_oi, 'put_iv': put_iv, 'put_ltp': put_ltp,
            'put_bid': round(put_ltp - 0.5, 2), 'put_ask': round(put_ltp + 0.5, 2),
            'put_volume': int(rng.integers(1000, 18000)),
        })
    df = pd.DataFrame(rows)
    return df.sort_values('strike').reset_index(drop=True)


class NSEOptionsFetcher:
    """Fetch option chain data from NSE India."""

    _HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.nseindia.com/option-chain",
        "Connection": "keep-alive",
        "DNT": "1",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    def __init__(self):
        self.base_url = "https://www.nseindia.com/api/option-chain-indices"
        self.session = requests.Session()
        self.session.headers.update(self._HEADERS)
        self._session_ready = False

    def _init_session(self):
        """Visit NSE homepage to obtain cookies required for API calls."""
        if self._session_ready:
            return True
        try:
            r = self.session.get("https://www.nseindia.com/option-chain", timeout=15)
            if r.status_code == 200:
                self._session_ready = True
                time.sleep(1)  # polite delay before hitting the API
                return True
        except Exception:
            pass
        return False

    def get_expiry_dates(self, index_name="NIFTY"):
        """Get available expiry dates."""
        try:
            self._init_session()
            response = self.session.get(
                self.base_url, params={"symbol": index_name}, timeout=15
            )
            if response.status_code == 200:
                data = response.json()
                expiries = data.get("records", {}).get("expiryDates", [])
                return expiries[:5]
        except Exception:
            pass
        # Fallback: generate nearby Thursday expiries
        today = datetime.now()
        expiries = []
        d = today
        for _ in range(5):
            days_ahead = (3 - d.weekday()) % 7
            if days_ahead == 0 and d.date() > today.date():
                days_ahead = 7
            d = d + timedelta(days=days_ahead if days_ahead else 7)
            expiries.append(d.strftime("%d-%b-%Y").upper())
        return expiries

    def fetch_option_chain(self, index="NIFTY", expiry=""):
        """Fetch option chain data from NSE, fall back to demo data."""
        try:
            if self._init_session():
                params = {"symbol": index}
                if expiry:
                    params["date"] = expiry
                response = self.session.get(self.base_url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    records = data.get("records", {}).get("data", [])
                    if records:
                        return self._process_records(records), False  # False = not demo
        except Exception:
            pass
        # Return demo data with a flag
        return _generate_demo_data(index), True

    def _process_records(self, records):
        """Process raw NSE records into a clean DataFrame."""
        rows = []
        for record in records:
            if "CE" in record and "PE" in record:
                strike = record.get("strikePrice")
                ce = record.get("CE", {})
                pe = record.get("PE", {})
                rows.append({
                    'strike': strike,
                    'call_oi': ce.get('openInterest', 0),
                    'call_iv': ce.get('impliedVolatility', 0),
                    'call_ltp': ce.get('lastPrice', 0),
                    'call_bid': ce.get('bid', 0),
                    'call_ask': ce.get('ask', 0),
                    'call_volume': ce.get('totalTradedVolume', 0),
                    'put_oi': pe.get('openInterest', 0),
                    'put_iv': pe.get('impliedVolatility', 0),
                    'put_ltp': pe.get('lastPrice', 0),
                    'put_bid': pe.get('bid', 0),
                    'put_ask': pe.get('ask', 0),
                    'put_volume': pe.get('totalTradedVolume', 0),
                })
        df = pd.DataFrame(rows)
        return df.sort_values('strike').reset_index(drop=True)

# ==================== ANALYSIS FUNCTIONS ====================

def calculate_market_sentiment(df):
    """Calculate Market Sentiment (Bullish/Bearish)"""
    if df.empty:
        return None, "No data"
    
    max_call_oi_strike = df.loc[df['call_oi'].idxmax(), 'strike']
    max_put_oi_strike = df.loc[df['put_oi'].idxmax(), 'strike']
    
    current_price = (max_call_oi_strike + max_put_oi_strike) / 2
    
    if max_call_oi_strike > max_put_oi_strike:
        sentiment = "BEARISH"
        emoji = "📉"
    elif max_call_oi_strike < max_put_oi_strike:
        sentiment = "BULLISH"
        emoji = "📈"
    else:
        sentiment = "NEUTRAL"
        emoji = "↔️"
    
    return sentiment, emoji, max_call_oi_strike, max_put_oi_strike

def calculate_support_resistance(df):
    """Calculate Support (Highest Put OI) and Resistance (Highest Call OI)"""
    max_put_strike = df.loc[df['put_oi'].idxmax(), 'strike']
    max_call_strike = df.loc[df['call_oi'].idxmax(), 'strike']
    
    support = max_put_strike
    resistance = max_call_strike
    
    return support, resistance

def calculate_price_oi_analysis(df):
    """Analyze Price and OI changes for Short Covering vs Long Unwinding"""
    if len(df) < 2:
        return pd.DataFrame()
    
    analysis = pd.DataFrame({
        'strike': df['strike'],
        'call_oi': df['call_oi'],
        'put_oi': df['put_oi'],
        'total_oi': df['call_oi'] + df['put_oi'],
        'call_iv': df['call_iv'],
        'put_iv': df['put_iv']
    })
    
    return analysis

def calculate_expected_range(df):
    """Calculate expected trading range"""
    max_put_strike = df.loc[df['put_oi'].idxmax(), 'strike']
    max_call_strike = df.loc[df['call_oi'].idxmax(), 'strike']
    
    lower_range = min(max_put_strike, max_call_strike)
    upper_range = max(max_put_strike, max_call_strike)
    
    return lower_range, upper_range

def calculate_pcr(df):
    """Calculate Put-Call Ratio"""
    total_put_oi = df['put_oi'].sum()
    total_call_oi = df['call_oi'].sum()
    
    if total_call_oi == 0:
        return 0
    
    pcr = total_put_oi / total_call_oi
    
    if pcr > 1:
        interpretation = "BULLISH (High Put OI)"
    elif pcr < 0.6:
        interpretation = "BEARISH (Low Put OI)"
    else:
        interpretation = "NEUTRAL"
    
    return pcr, interpretation

def calculate_max_pain(df):
    """Calculate Max Pain (Strike where most options expire worthless)"""
    if df.empty:
        return None
    
    # Simple approximation: Strike with highest total OI is often close to max pain
    df['total_oi'] = df['call_oi'] + df['put_oi']
    max_pain_strike = df.loc[df['total_oi'].idxmax(), 'strike']
    
    return max_pain_strike

# ==================== DASHBOARD LAYOUT ====================

def main():
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 📊 Indian Stock Index Options Dashboard")
        st.markdown("*Real-time Option Chain Analysis with Market Sentiment*")
    
    with col2:
        last_update = datetime.now().strftime("%H:%M:%S")
        st.metric("Last Update", last_update)
    
    # Sidebar for controls
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        index_choice = st.selectbox(
            "Select Index",
            ["NIFTY", "NIFTYNXT50", "NIFTYIT", "NIFTYPHARMA", "NIFTYBANK"],
            help="Select the index for options analysis"
        )
        
        auto_refresh = st.checkbox("Auto Refresh", value=False)
        refresh_interval = st.slider(
            "Refresh Interval (seconds)",
            min_value=30,
            max_value=300,
            value=60,
            step=30,
            disabled=not auto_refresh
        )
        
        st.divider()
        st.markdown("### About This Dashboard")
        st.info("""
        This dashboard analyzes:
        1. **Market Sentiment** - Bullish/Bearish indicators
        2. **Support & Resistance** - Key price levels
        3. **Short Covering** - Trader positioning
        4. **Trading Range** - Expected boundaries
        5. **Implied Volatility** - Expected movement
        6. **Put-Call Ratio** - Overall sentiment
        7. **Max Pain** - Expiry pressure point
        """)
    
    # Fetch data
    fetcher = NSEOptionsFetcher()

    try:
        with st.spinner(f"📡 Fetching {index_choice} option chain data..."):
            df, is_demo = fetcher.fetch_option_chain(index_choice)

        if is_demo:
            st.warning(
                "⚠️ **Demo Mode** — Could not reach NSE (market may be closed or NSE is blocking the request). "
                "Showing realistic simulated data. Data will auto-update when NSE becomes reachable.",
                icon="📊"
            )

        # Sidebar - Expiry dates selection
        with st.sidebar:
            st.divider()
            expiry_dates = fetcher.get_expiry_dates(index_choice)
            selected_expiry = st.selectbox(
                "Select Expiry",
                expiry_dates if expiry_dates else ["Current"],
                help="Choose the expiry date for analysis"
            )
        
        # ==================== KEY METRICS ROW 1 ====================
        st.markdown("### 📈 Key Market Indicators")
        
        col1, col2, col3, col4 = st.columns(4)
        
        sentiment, emoji, call_strike, put_strike = calculate_market_sentiment(df)
        support, resistance = calculate_support_resistance(df)
        pcr, pcr_interpretation = calculate_pcr(df)
        max_pain = calculate_max_pain(df)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card {sentiment.lower()}">
                <h3>Market Sentiment</h3>
                <div style="font-size: 32px; font-weight: 800; margin: 10px 0;">
                    {emoji} {sentiment}
                </div>
                <small>Call: {call_strike:.0f} | Put: {put_strike:.0f}</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            support_color = "🟢" if support < resistance else "🔴"
            st.markdown(f"""
            <div class="metric-card">
                <h3>Support & Resistance</h3>
                <div style="font-size: 14px; margin: 10px 0; line-height: 1.8;">
                    🛡️ Support: <strong>{support:.0f}</strong><br>
                    🔪 Resistance: <strong>{resistance:.0f}</strong><br>
                    Range: <strong>{resistance - support:.0f}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            pcr_color = "🟢" if pcr > 1 else "🔴" if pcr < 0.6 else "🟡"
            st.markdown(f"""
            <div class="metric-card">
                <h3>Put-Call Ratio</h3>
                <div style="font-size: 28px; font-weight: 700; margin: 10px 0; color: #EEFF00;">
                    {pcr:.2f}
                </div>
                <small>{pcr_color} {pcr_interpretation}</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Max Pain Level</h3>
                <div style="font-size: 28px; font-weight: 700; margin: 10px 0; color: #EEFF00;">
                    {max_pain:.0f}
                </div>
                <small>Expiry pressure point</small>
            </div>
            """, unsafe_allow_html=True)
        
        # ==================== DETAILED ANALYSIS ====================
        
        st.markdown("### 📊 Open Interest Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Call OI vs Put OI
            fig_oi = go.Figure()
            
            top_calls = df.nlargest(15, 'call_oi')
            top_puts = df.nlargest(15, 'put_oi')
            
            fig_oi.add_trace(go.Bar(
                x=top_calls['strike'],
                y=top_calls['call_oi'],
                name='Call OI',
                marker_color='#10B981',
                opacity=0.8
            ))
            
            fig_oi.add_trace(go.Bar(
                x=top_puts['strike'],
                y=top_puts['put_oi'],
                name='Put OI',
                marker_color='#EF4444',
                opacity=0.8
            ))
            
            fig_oi.update_layout(
                title="Call vs Put Open Interest (Top Strikes)",
                xaxis_title="Strike Price",
                yaxis_title="Open Interest",
                barmode='group',
                hovermode='x unified',
                template='plotly_dark',
                height=400,
                plot_bgcolor='rgba(15, 23, 42, 0.5)',
                paper_bgcolor='rgba(15, 23, 42, 0.3)',
            )
            
            st.plotly_chart(fig_oi, use_container_width=True)
        
        with col2:
            # Implied Volatility
            fig_iv = go.Figure()
            
            df_sorted = df.sort_values('strike')
            
            fig_iv.add_trace(go.Scatter(
                x=df_sorted['strike'],
                y=df_sorted['call_iv'],
                name='Call IV',
                mode='lines+markers',
                line=dict(color='#10B981', width=2),
                marker=dict(size=6)
            ))
            
            fig_iv.add_trace(go.Scatter(
                x=df_sorted['strike'],
                y=df_sorted['put_iv'],
                name='Put IV',
                mode='lines+markers',
                line=dict(color='#EF4444', width=2),
                marker=dict(size=6)
            ))
            
            fig_iv.update_layout(
                title="Implied Volatility Smile",
                xaxis_title="Strike Price",
                yaxis_title="Implied Volatility (%)",
                hovermode='x unified',
                template='plotly_dark',
                height=400,
                plot_bgcolor='rgba(15, 23, 42, 0.5)',
                paper_bgcolor='rgba(15, 23, 42, 0.3)',
            )
            
            st.plotly_chart(fig_iv, use_container_width=True)
        
        # ==================== EXPECTED TRADING RANGE ====================
        
        st.markdown("### 📍 Expected Trading Range & Price Analysis")
        
        lower_range, upper_range = calculate_expected_range(df)
        range_width = upper_range - lower_range
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Trading Range</h3>
                <div style="font-size: 24px; font-weight: 700; margin: 15px 0;">
                    {lower_range:.0f} - {upper_range:.0f}
                </div>
                <small>Width: {range_width:.0f} points</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            midpoint = (lower_range + upper_range) / 2
            st.markdown(f"""
            <div class="metric-card">
                <h3>Midpoint</h3>
                <div style="font-size: 28px; font-weight: 700; margin: 10px 0; color: #EEFF00;">
                    {midpoint:.0f}
                </div>
                <small>Central expectation</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_iv = (df['call_iv'].mean() + df['put_iv'].mean()) / 2
            st.markdown(f"""
            <div class="metric-card">
                <h3>Average IV</h3>
                <div style="font-size: 28px; font-weight: 700; margin: 10px 0; color: #EEFF00;">
                    {avg_iv:.2f}%
                </div>
                <small>Expected movement</small>
            </div>
            """, unsafe_allow_html=True)
        
        # ==================== DETAILED TABLE ====================
        
        st.markdown("### 📋 Option Chain Data (Top Strikes by OI)")
        
        display_df = df.copy()
        display_df['total_oi'] = display_df['call_oi'] + display_df['put_oi']
        display_df = display_df.nlargest(20, 'total_oi')[
            ['strike', 'call_oi', 'call_iv', 'call_ltp', 'put_oi', 'put_iv', 'put_ltp']
        ].copy()
        
        display_df.columns = ['Strike', 'Call OI', 'Call IV', 'Call LTP', 'Put OI', 'Put IV', 'Put LTP']
        
        st.dataframe(
            display_df.style.format({
                'Strike': '{:.0f}',
                'Call OI': '{:,.0f}',
                'Call IV': '{:.2f}%',
                'Call LTP': '{:.2f}',
                'Put OI': '{:,.0f}',
                'Put IV': '{:.2f}%',
                'Put LTP': '{:.2f}'
            }).background_gradient(
                subset=['Call OI'],
                cmap='Greens',
                vmin=display_df['Call OI'].min(),
                vmax=display_df['Call OI'].max()
            ).background_gradient(
                subset=['Put OI'],
                cmap='Reds',
                vmin=display_df['Put OI'].min(),
                vmax=display_df['Put OI'].max()
            ),
            use_container_width=True,
            height=400
        )
        
        # ==================== INTERPRETATION GUIDE ====================
        
        st.markdown("### 📖 Analysis Interpretation Guide")
        
        interpretation_col1, interpretation_col2 = st.columns(2)
        
        with interpretation_col1:
            st.markdown("""
            #### 🔍 What These Metrics Mean:
            
            **Market Sentiment**
            - 📈 **Bullish**: More put OI (traders buying downside protection)
            - 📉 **Bearish**: More call OI (traders buying upside)
            - ↔️ **Neutral**: Balanced sentiment
            
            **Support & Resistance**
            - 🛡️ Support: Highest put OI strike (floor)
            - 🔪 Resistance: Highest call OI strike (ceiling)
            
            **Put-Call Ratio**
            - **> 1.0**: Bullish (more puts = hedging)
            - **< 0.6**: Bearish (few puts = confidence)
            - **0.6 - 1.0**: Neutral zone
            """)
        
        with interpretation_col2:
            st.markdown("""
            #### 💡 Trader Positioning:
            
            | Price | OI | Meaning |
            |-------|----|---------| 
            | ↑ | ↑ | Long buildup 📈 |
            | ↓ | ↑ | Short buildup 📉 |
            | ↑ | ↓ | Short covering 🔒 |
            | ↓ | ↓ | Long unwinding 😅 |
            
            **Expected Movement (IV)**
            - High IV → Market expects big moves
            - Low IV → Market expects smaller moves
            """)
        
        # Auto-refresh logic
        if auto_refresh:
            time.sleep(refresh_interval)
            st.rerun()
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("💡 Tip: Check your internet connection or try a different index.")

if __name__ == "__main__":
    main()

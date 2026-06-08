# 📊 Indian Options Chain Dashboard - Setup & Usage Guide

## Overview

A professional Streamlit dashboard for analyzing Indian stock index options chains with real-time market sentiment analysis, support/resistance levels, and comprehensive trader positioning metrics.

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the files
# Navigate to the directory
cd path/to/your/project

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Dashboard

```bash
streamlit run options_dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

---

## 📋 Features & Metrics Explained

### 1. **Market Sentiment Analysis** 📈
Shows whether the market is **BULLISH**, **BEARISH**, or **NEUTRAL** based on open interest distribution.

- **📈 BULLISH**: More put OI than call OI (traders buying protective puts)
- **📉 BEARISH**: More call OI than put OI (traders buying calls)
- **↔️ NEUTRAL**: Balanced sentiment

**How it works:**
```
Call OI Strike < Put OI Strike → Bullish (support below)
Call OI Strike > Put OI Strike → Bearish (resistance above)
```

### 2. **Support & Resistance Levels** 🛡️
Key price levels where traders expect the market to pause or reverse.

- **🛡️ Support**: Strike with highest PUT OI (floor where buyers step in)
- **🔪 Resistance**: Strike with highest CALL OI (ceiling where sellers step in)
- **Trading Range**: Corridor between support and resistance

**Why it matters:**
- High put OI at 24,500 means traders expect support there
- High call OI at 25,000 means traders expect resistance there

### 3. **Put-Call Ratio (PCR)** 📊
Overall sentiment indicator comparing total put OI to total call OI.

```
PCR = Total Put OI ÷ Total Call OI

PCR > 1.0    → BULLISH (hedging activity, support expected)
PCR 0.6-1.0  → NEUTRAL (balanced positioning)
PCR < 0.6    → BEARISH (confidence/speculativeness)
PCR > 1.5    → Extreme bullish (contrarian signal possible)
```

**Example:**
- If total put OI = 2,000,000 and total call OI = 1,500,000
- PCR = 2,000,000 ÷ 1,500,000 = 1.33 (Bullish)

### 4. **Expected Trading Range** 📍
The strike prices with highest put and call OI often form the expected range for market movement by expiry.

```
Trading Range = [Highest Put OI Strike, Highest Call OI Strike]

Example:
Support: 24,500 (put OI: 800,000)
Resistance: 25,000 (call OI: 750,000)
Expected Range: 24,500 - 25,000 (500 point range)
```

### 5. **Implied Volatility (IV)** 📈
Reflects what the market expects about future movement.

- **High IV (>25%)**: Market expects significant moves (event-driven uncertainty)
- **Low IV (<15%)**: Market expects stable, smaller moves
- **IV Skew**: Difference between put IV and call IV indicates market bias

**Interpretation:**
- IV rising before RBI policy announcement → Market expects big move
- IV falling gradually → Market calming down/consolidation expected

### 6. **Trader Positioning Analysis** 🎯
Understand what traders are doing by watching price and OI changes together.

| Price | OI | Signal | Meaning |
|-------|----|---------|---------| 
| ↑ | ↑ | Long Buildup | Traders buying, bullish |
| ↓ | ↑ | Short Buildup | Traders shorting, bearish |
| ↑ | ↓ | Short Covering | Shorts buying back, bullish |
| ↓ | ↓ | Long Unwinding | Longs selling, bearish |

### 7. **Max Pain Level** 💡
The strike price where the maximum number of option buyers lose money at expiry.

Markets sometimes gravitate toward max pain levels as expiry approaches, especially in the last few days.

**Three calculation methods shown:**
1. **Primary**: Strike with highest total OI
2. **By Balance**: Strike where call OI ≈ put OI
3. **By IV Weight**: Weighted average considering IV

---

## 📊 Dashboard Sections

### Left Sidebar (Configuration)
- **Select Index**: Choose from NIFTY, NIFTYNXT50, NIFTYIT, NIFTYPHARMA, NIFTYBANK
- **Auto Refresh**: Enable automatic dashboard refresh
- **Refresh Interval**: Set refresh timing (30-300 seconds)
- **Expiry Selection**: Choose expiry date for analysis

### Main Dashboard

#### Key Metrics Row (Top)
1. **Market Sentiment** - Bullish/Bearish indicator
2. **Support & Resistance** - Key price levels
3. **Put-Call Ratio** - Overall sentiment
4. **Max Pain Level** - Expiry pressure point

#### Open Interest Analysis (Charts)
- **Call vs Put OI**: Bar chart comparing open interest
- **IV Smile**: Line chart showing volatility curve

#### Trading Range & Liquidity
- Expected trading range
- Midpoint analysis
- Average IV regime

#### Option Chain Data Table
Top 20 strikes by total open interest with:
- Strike price
- Call OI, IV, LTP
- Put OI, IV, LTP
- Color-coded for easy visualization

---

## 💡 Trading Strategy Examples

### Strategy 1: Range Trading
```
Condition: Trading range identified, PCR normal (0.6-1.0)
Action: Buy support, sell resistance
Example: Buy 24,500 call, sell 25,000 call (bull call spread)
```

### Strategy 2: Bullish Breakout
```
Condition: PCR > 1.2, IV increasing, price near resistance
Action: Buy ATM calls with 1-2 week expiry
Exit: At max pain level or when IV drops
```

### Strategy 3: Hedged Positioning
```
Condition: PCR > 1.5 (extreme bullish signal, contrarian)
Action: Sell puts, buy calls (protective conversion)
Rationale: May indicate bottom near, reduce downside risk
```

### Strategy 4: Earnings/Event Play
```
Condition: High IV (>30%), expected move > 2%
Action: Buy straddles/strangles at ATM strikes
Example: Buy 25,000 call + 25,000 put
Exit: After event announcement or IV crush
```

---

## 📈 Using Data for Decisions

### When to Enter Long Positions
✅ PCR > 1.0 (bullish sentiment)  
✅ Price bouncing off support level (high put OI)  
✅ IV increasing (market expecting moves)  
✅ Short covering signal (price ↑, OI ↓)  

### When to Enter Short Positions
✅ PCR < 0.7 (bearish sentiment)  
✅ Price hitting resistance (high call OI)  
✅ Long unwinding signal (price ↓, OI ↓)  
✅ Max pain below current price  

### When to Avoid Trading
❌ PCR extremely high (>2.0) without confirmation  
❌ Very low liquidity (wide bid-ask spreads)  
❌ Before major data releases (RBI, IIP, etc.)  
❌ Near market close (last hour)  

---

## 🔧 Advanced Usage

### Using the Helper Module

```python
from options_analyzer import NSEDataFetcher, AdvancedOptionsAnalyzer

# Fetch data
fetcher = NSEDataFetcher()
df = fetcher.fetch_with_retry("NIFTY")

# Analyze
analyzer = AdvancedOptionsAnalyzer(df)

# Get comprehensive report
report = analyzer.get_comprehensive_report()

# Print specific metrics
print(f"PCR: {report['pcr_analysis']['pcr_oi']:.2f}")
print(f"Max Pain: {report['max_pain']['primary']}")
print(f"Expected Move: ₹{report['expected_move']['expected_move_1sd']:.0f}")

# Get trading signals
signals = analyzer.get_sentiment_signals()
for signal in signals:
    print(f"{signal['icon']} {signal['signal']} - {signal['reason']}")
```

### Customizing the Dashboard

Edit `options_dashboard.py` to:

1. **Change colors**: Modify CSS variables in the markdown section
2. **Add more indices**: Extend the `index_choice` selectbox
3. **Change chart types**: Modify Plotly chart configurations
4. **Add custom calculations**: Insert new functions before the main() call
5. **Export data**: Add download button for CSV/Excel

```python
# Example: Add export button
if st.button("📥 Download Data as CSV"):
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"options_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
```

---

## 🐛 Troubleshooting

### Problem: "Unable to fetch data"
**Solution:**
- Check internet connection
- Verify NSE website is accessible
- Try different index (some may have temporary issues)
- Ensure market hours (9:15 AM - 3:30 PM IST, Monday-Friday)

### Problem: Dashboard loads but no data shows
**Solution:**
- Wait 30 seconds (NSE API sometimes slow)
- Disable auto-refresh and refresh manually
- Check browser console for errors (F12)
- Try `streamlit run options_dashboard.py --logger.level=debug`

### Problem: Outdated data in sidebar
**Solution:**
- Press "R" to force refresh in Streamlit
- Clear cache: `streamlit cache clear`
- Restart Streamlit: Stop and rerun command

### Problem: Import errors
**Solution:**
```bash
# Verify all packages installed
pip list | grep -E "streamlit|pandas|plotly|requests"

# Reinstall if needed
pip install --upgrade -r requirements.txt
```

---

## 📌 Important Notes

1. **Real-time Data**: Dashboard fetches data from NSE API. Data updates depend on NSE server response (typically 1-2 seconds behind actual market).

2. **Market Hours**: Best used during NSE trading hours (9:15 AM - 3:30 PM IST, Monday-Friday).

3. **Data Accuracy**: Verify critical decisions with official NSE website or broker platform.

4. **PCR Interpretation**: PCR is ONE of many indicators. Never trade solely on PCR; combine with price action and other technical analysis.

5. **Max Pain**: Max pain gravitates on expiry day, but is NOT guaranteed. Use it as ONE factor in decision-making.

---

## 📚 Resources for Further Learning

1. **NSE Official Website**: https://www.nseindia.com/
2. **Options Chain Data**: https://www.nseindia.com/products/content/derivatives/equities/options_analysis.htm
3. **Trading Concepts**: Look for "PCR interpretation" and "max pain calculation" tutorials

---

## 🎯 Key Takeaways

| Metric | Bullish Signal | Bearish Signal | Action |
|--------|----------------|----------------|--------|
| PCR | > 1.0 | < 0.7 | Use for context |
| Support | Holds | Breaks | Watch closely |
| Resistance | Breaks | Holds | Trade range |
| Max Pain | Near support | Near resistance | Contrarian watch |
| IV | Rising | Falling | Volatility direction |

---

## 📞 Support

For issues, improvements, or suggestions:
1. Check error messages carefully
2. Verify all dependencies installed
3. Check NSE website availability
4. Review this guide's troubleshooting section

Happy Trading! 📈

---

**Disclaimer**: This dashboard is for educational purposes. Always conduct your own analysis and consult financial advisors before making investment decisions. Past data does not guarantee future results.

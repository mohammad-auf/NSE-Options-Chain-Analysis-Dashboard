# 📊 NSE Options Chain Analysis Dashboard

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://nse-options-dashboard-6drh.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![NSE API](https://img.shields.io/badge/Data-NSE%20API-0066CC?style=for-the-badge)](https://nseindia.com)

A professional **Streamlit dashboard** for analyzing Indian stock index options chains with real-time sentiment analysis, support/resistance identification, and comprehensive trader positioning metrics.

> 🌐 **Live App**: [https://nse-options-dashboard-6drh.onrender.com/](https://nse-options-dashboard-6drh.onrender.com/)  
> ⚠️ Hosted on Render free tier — may take **~30 seconds to wake up** on first visit.

---

## ✨ Features

✅ **Real-time Market Sentiment** - Bullish/Bearish/Neutral analysis  
✅ **Support & Resistance Levels** - Identify key price zones from option OI  
✅ **Put-Call Ratio (PCR)** - Overall market sentiment indicator  
✅ **Trader Positioning Analysis** - Short covering vs long unwinding  
✅ **Implied Volatility (IV) Analysis** - Expected market movement  
✅ **Max Pain Calculation** - Expiry pressure level  
✅ **Trading Range Projection** - Expected range by expiry  
✅ **Multiple Indices Support** - NIFTY, Bank Nifty, IT, Pharma, etc.  
✅ **Interactive Charts** - Plotly visualizations  
✅ **Auto-Refresh** - Real-time updates during trading hours  

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Internet connection (for NSE data)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run the Dashboard

```bash
streamlit run options_dashboard.py
```

Dashboard opens at: **http://localhost:8501**

---

## 📁 Project Files

| File | Purpose |
|------|---------|
| `options_dashboard.py` | Main Streamlit dashboard (visual, interactive) |
| `options_analyzer.py` | Advanced analysis module (programmatic use) |
| `requirements.txt` | Python dependencies |
| `SETUP_GUIDE.md` | Detailed setup and usage guide |
| `quick_reference.py` | Quick lookup reference card for metrics |
| `examples_and_config.py` | Examples and configuration options |
| `README.md` | This file |

---

## 📊 The 7 Metrics Explained (Simple Version)

### 1. **Market Sentiment** 📈
- **📈 Bullish**: More people protecting against downside (buying puts)
- **📉 Bearish**: More people betting on upside (buying calls)
- **↔️ Neutral**: Balanced outlook

**Use for:** Understanding market consensus direction

---

### 2. **Support & Resistance** 🛡️
- **Support**: The "floor" where buyers expect to buy (highest put OI)
- **Resistance**: The "ceiling" where sellers expect to sell (highest call OI)
- **Range**: Corridor between support and resistance

**Use for:** Setting entry/exit points

---

### 3. **Put-Call Ratio (PCR)** 📊
How many puts vs calls traders have purchased.

```
PCR = Total Put OI ÷ Total Call OI

High PCR (>1.0)  → Bullish   (lots of hedging)
Low PCR (<0.7)   → Bearish   (low hedging, confidence)
```

**Use for:** Quick sentiment check (but not alone!)

---

### 4. **Trader Positioning** 🎯
Watch price AND open interest together:

| Price | OI | Meaning |
|-------|----|---------| 
| Up | Up | Longs building 📈 |
| Down | Up | Shorts building 📉 |
| Up | Down | Shorts covering 🔒 |
| Down | Down | Longs exiting 😅 |

**Use for:** Confirming trend strength

---

### 5. **Implied Volatility** 📈
What the market expects about future movement.

- **High IV (>25%)**: Expect big moves (before news events)
- **Normal IV (15-25%)**: Regular conditions
- **Low IV (<15%)**: Expect small moves (consolidation)

**Use for:** Choosing trading strategies (spreads vs directionality)

---

### 6. **Trading Range** 📍
Where the market likely stays by expiry.

```
Range = Support to Resistance
Example: 24,500 to 25,000 (500 point range)
```

**Use for:** Planning range trading setups

---

### 7. **Max Pain** 💡
The strike where most options expire worthless.

Markets sometimes gravitate toward this level on expiry day (but not always!).

**Use for:** Adding weight to contrarian signals near expiry

---

## 🎯 Common Use Cases

### Use Case 1: Identifying Support Levels
```
1. Look at Support & Resistance section
2. Note the strike with highest put OI
3. This is your strong support level
4. Buy near this level with 2-3 day expiry
```

### Use Case 2: Range Trading
```
1. Check PCR (should be 0.7-1.2 for range)
2. Identify support and resistance
3. Buy call at support, sell call at resistance (spread)
4. Collect premium as market oscillates
```

### Use Case 3: Timing Entries
```
1. Check sentiment (bullish PCR > 1.0)
2. Confirm with Price+OI signal
3. Wait for price near support
4. Enter long when IV increasing
```

### Use Case 4: Pre-Expiry Analysis
```
1. Check Max Pain level
2. On expiry day, watch for pullback toward max pain
3. Take profits if price moving away from max pain
4. Avoid holding 30 min before close
```

---

## 🎓 Learning Path

**Beginner:**
1. Run dashboard and observe for 5 market days
2. Read `quick_reference.py` output (print it)
3. Understand each metric individually
4. Paper trade (no real money) using signals

**Intermediate:**
1. Study `SETUP_GUIDE.md` in detail
2. Run `examples_and_config.py` to see live examples
3. Use 2-3 metrics together for trading decisions
4. Track which combinations work best for you

**Advanced:**
1. Customize `options_analyzer.py` for your strategy
2. Create backtesting scripts using historical data
3. Build alerts when metrics cross thresholds
4. Integrate with your trading platform API

---

## 💡 Tips & Best Practices

### ✅ DO:
- Use 2-3 metrics together (not just one)
- Combine with price action analysis
- Trade near support/resistance levels
- Respect the trading range
- Include risk management (stop losses)

### ❌ DON'T:
- Trade solely on PCR (one metric only)
- Ignore bid-ask spreads (low liquidity kills profits)
- Trade extreme options (too far OTM)
- Hold through expiry day close
- Ignore max pain level on expiry (high probability event)

### 🎯 Golden Rules:
1. **Confluence**: Wait for 2-3 signals aligned
2. **Liquidity**: Trade only strikes with high OI
3. **Timing**: Trade in direction of PCR
4. **Risk**: Always use stop loss (0.5-1% of strike)
5. **Size**: Position size = Risk tolerance ÷ Stop distance

---

## 📈 Example Trading Day

**9:30 AM - Opening Analysis**
```
Dashboard shows:
• PCR: 1.15 (Bullish)
• Support: 24,500, Resistance: 25,000
• IV: 18% (Normal)
• Sentiment: 🟢 Bullish

Action: Look for BUY opportunities near support
```

**10:30 AM - Market Falls to Support**
```
Price near 24,500, check dashboard again:
• Put OI at 24,500 increased (support confirmed)
• Price ↓ but OI ↓ (Long unwinding = contrarian)
• IV rising (market expects move)

Action: BUY 24,700 call expiring in 2-3 days
Stop: 24,400
Target: 25,000 (resistance)
```

**2:30 PM - Approaching Resistance**
```
Price near 24,950:
• Call OI at 25,000 increased significantly
• Can't break 25,000 (resistance holding)
• Max Pain: 24,850

Action: TAKE PROFIT at 25,000 or near it
Don't hold into close (IV crush risk)
```

---

## 🔧 Customization

### Change Dashboard Colors:
Edit line 45 in `options_dashboard.py`:
```python
"colors": {
    "primary": "#0F766E",      # Your color here
    ...
}
```

### Add More Indices:
Edit line 160 in `options_dashboard.py`:
```python
index_choice = st.selectbox(
    "Select Index",
    ["NIFTY", "NIFTYNXT50", "NIFTYIT", "NIFTYPHARMA", 
     "NIFTYBANK", "YOUR_NEW_INDEX"],  # Add here
    ...
)
```

### Change Analysis Thresholds:
Edit `examples_and_config.py`:
```python
ANALYSIS_CONFIG = {
    "pcr_bullish_threshold": 1.0,  # Change here
    "pcr_bearish_threshold": 0.6,  # Change here
    ...
}
```

---

## 🐛 Troubleshooting

### Dashboard won't load
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Run with debug info
streamlit run options_dashboard.py --logger.level=debug
```

### "Unable to fetch data" error
```bash
# Check internet connection
ping www.nseindia.com

# Check if NSE website is accessible
# (Sometimes blocked during market hours if overloaded)

# Try a different index
# Some indices may have temporary issues

# Clear Streamlit cache
streamlit cache clear
```

### Data seems outdated
```bash
# Press 'R' in Streamlit to refresh
# Or manually click "Rerun" in browser

# Check if market is open (9:15-3:30 IST, weekdays only)
```

---

## 📚 Resources

1. **NSE Official**: https://www.nseindia.com/
2. **Options Data**: https://www.nseindia.com/products/content/derivatives/equities/options_analysis.htm
3. **Technical Analysis**: Learn support/resistance from price charts
4. **Option Greeks**: Understand delta, gamma, theta for deeper analysis

---

## 📞 Support & Issues

If you encounter issues:

1. **Check the guides**:
   - `SETUP_GUIDE.md` - Detailed instructions
   - `quick_reference.py` - Metric explanations
   - This README - Common problems

2. **Verify your setup**:
   ```bash
   pip list | grep -E "streamlit|pandas|plotly"
   python -m streamlit --version
   ```

3. **Test the analyzer module**:
   ```bash
   python examples_and_config.py
   # Choose option 1 to run basic analysis
   ```

---

## 📊 Dashboard Overview

```
┌─────────────────────────────────────────────────┐
│  📊 Indian Options Chain Dashboard              │
│  Select Index | Auto Refresh Toggle             │
├─────────────────────────────────────────────────┤
│                                                  │
│  Key Metrics Row                                 │
│  ┌──────────┬──────────┬──────────┬──────────┐   │
│  │Sentiment │Support & │Put-Call  │Max Pain  │   │
│  │          │Resistance│ Ratio    │          │   │
│  └──────────┴──────────┴──────────┴──────────┘   │
│                                                  │
│  Call vs Put OI    │  IV Smile Curve             │
│  [Bar Chart]       │  [Line Chart]               │
│                                                  │
│  Trading Range & Liquidity Metrics               │
│  ┌──────────┬──────────┬──────────┐             │
│  │ Range    │Midpoint  │Avg IV    │             │
│  └──────────┴──────────┴──────────┘             │
│                                                  │
│  Detailed Option Chain Data                      │
│  [Interactive Table with top 20 strikes]        │
│                                                  │
│  Interpretation Guide                            │
│  [Explanation of what metrics mean]              │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## ⚠️ Disclaimer

**This dashboard is for educational purposes only.**

- Not a recommendation to buy/sell any security
- Past data doesn't guarantee future results
- Always consult a financial advisor before investing
- Options trading involves significant risk
- Use proper risk management and position sizing
- Test with paper trading before real money

**Remember: The goal is to understand trader sentiment and market expectations, not to predict the market.**

---

## 🎉 Getting Started Checklist

- [ ] Install Python 3.8+
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run dashboard: `streamlit run options_dashboard.py`
- [ ] Read `SETUP_GUIDE.md` for detailed explanation
- [ ] Print `quick_reference.py` output for quick lookup
- [ ] Run examples: `python examples_and_config.py`
- [ ] Paper trade for 5 days to understand patterns
- [ ] Start small with real trading (1 contract)
- [ ] Track your trades and optimize strategy

---

## 🚀 Next Steps

1. **Understand**: Read all guides thoroughly
2. **Observe**: Run dashboard during market hours for 5 days
3. **Practice**: Paper trade for 2 weeks
4. **Implement**: Start with smallest position size
5. **Refine**: Adjust strategy based on results
6. **Scale**: Increase position size once profitable

---

## 📝 Version History

**v1.0** - Initial release
- Basic dashboard with 7 metrics
- Support for major indices
- Interactive charts and tables
- Real-time data fetching from NSE

---

## 🙏 Acknowledgments

- NSE (National Stock Exchange) for data
- Streamlit for excellent dashboard framework
- Plotly for beautiful visualizations
- Python community for amazing libraries

---

## 📄 License

Open source - Use for learning and personal trading purposes.

---

**Happy Trading! 📈** 

*Remember: Understanding options sentiment is a skill. Like any skill, it takes practice. Start small, learn from mistakes, and scale gradually.*

---

### Quick Command Reference

```bash
# Install
pip install -r requirements.txt

# Run dashboard
streamlit run options_dashboard.py

# Run examples
python examples_and_config.py

# Clear cache if needed
streamlit cache clear

# Get quick reference
python quick_reference.py > quick_ref.txt
```

---

**Last Updated**: May 2026  
**Status**: Production Ready  
**Support**: Community-driven

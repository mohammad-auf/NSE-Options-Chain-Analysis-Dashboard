"""
Configuration and Example Usage for Options Chain Analysis
Customize these settings and run sample analysis
"""

# ==================== CONFIGURATION ====================

# Dashboard Appearance
DASHBOARD_CONFIG = {
    "theme": "dark",  # Options: "light", "dark"
    "auto_refresh": False,
    "refresh_interval": 60,  # seconds
    "page_layout": "wide",  # Options: "wide", "centered"
    
    # Color scheme (can customize)
    "colors": {
        "primary": "#0F766E",      # Teal
        "secondary": "#DC2626",    # Red
        "accent": "#EEFF00",       # Yellow
        "bullish": "#10B981",      # Green
        "bearish": "#EF4444",      # Red
        "neutral": "#F59E0B",      # Amber
    }
}

# Available Indices
INDICES_CONFIG = {
    "NIFTY": {
        "name": "NIFTY 50",
        "description": "Benchmark index",
        "spot_name": "NIFTY"
    },
    "NIFTYNXT50": {
        "name": "NIFTY Next 50",
        "description": "Mid-cap index",
        "spot_name": "NIFTYNXT50"
    },
    "NIFTYIT": {
        "name": "NIFTY IT",
        "description": "IT sector index",
        "spot_name": "NIFTYIT"
    },
    "NIFTYPHARMA": {
        "name": "NIFTY Pharma",
        "description": "Pharma sector index",
        "spot_name": "NIFTYPHARMA"
    },
    "NIFTYBANK": {
        "name": "NIFTY Bank",
        "description": "Banking sector index",
        "spot_name": "NIFTYBANK"
    },
    "NIFTYFMCG": {
        "name": "NIFTY FMCG",
        "description": "FMCG sector index",
        "spot_name": "NIFTYFMCG"
    },
    "NIFTYAUTO": {
        "name": "NIFTY Auto",
        "description": "Auto sector index",
        "spot_name": "NIFTYAUTO"
    }
}

# Analysis Parameters
ANALYSIS_CONFIG = {
    # PCR Thresholds
    "pcr_bullish_threshold": 1.0,
    "pcr_bearish_threshold": 0.6,
    "pcr_extreme_high": 1.5,
    "pcr_extreme_low": 0.5,
    
    # IV Thresholds (in percentage)
    "iv_high_threshold": 25,
    "iv_normal_high": 20,
    "iv_normal_low": 15,
    "iv_low_threshold": 10,
    
    # Support/Resistance
    "sr_levels_count": 5,  # Show top 5 support/resistance levels
    
    # Max Pain calculation methods
    "max_pain_methods": ["total_oi", "balance", "weighted"],
    
    # Expected move (in standard deviations)
    "expected_move_sd": [1, 2],  # 1 SD and 2 SD
}

# ==================== EXAMPLE USAGE ====================

def example_1_basic_analysis():
    """
    Example 1: Basic options analysis
    """
    print("=" * 80)
    print("EXAMPLE 1: Basic Options Analysis")
    print("=" * 80)
    
    from options_analyzer import NSEDataFetcher, AdvancedOptionsAnalyzer
    
    # Fetch data
    print("\n1️⃣ Fetching NIFTY option chain data...")
    fetcher = NSEDataFetcher()
    df = fetcher.fetch_with_retry("NIFTY")
    
    if df.empty:
        print("❌ Failed to fetch data")
        return
    
    print(f"✅ Fetched {len(df)} strikes")
    print(f"Strike range: {df['strike'].min():.0f} - {df['strike'].max():.0f}")
    
    # Analyze
    print("\n2️⃣ Running analysis...")
    analyzer = AdvancedOptionsAnalyzer(df)
    report = analyzer.get_comprehensive_report()
    
    # Display results
    print("\n3️⃣ Analysis Results:")
    print(f"   • PCR: {report['pcr_analysis']['pcr_oi']:.2f}")
    print(f"   • Support Level: {report['support_resistance']['support_levels'][0][0]:.0f}")
    print(f"   • Resistance Level: {report['support_resistance']['resistance_levels'][0][0]:.0f}")
    print(f"   • Max Pain: {report['max_pain']['primary']:.0f}")
    print(f"   • IV Regime: {report['iv_analysis']['iv_regime']}")
    print(f"   • Expected Move (1 SD): ₹{report['expected_move']['expected_move_1sd']:.0f}")
    
    # Trading signals
    print("\n4️⃣ Trading Signals:")
    for signal in report['signals']:
        print(f"   {signal['icon']} {signal['signal']}")
        print(f"      Reason: {signal['reason']}")
        print(f"      Confidence: {signal['confidence']}")


def example_2_range_trading():
    """
    Example 2: Identifying range trading setup
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Range Trading Setup")
    print("=" * 80)
    
    from options_analyzer import NSEDataFetcher, AdvancedOptionsAnalyzer
    
    fetcher = NSEDataFetcher()
    df = fetcher.fetch_with_retry("NIFTYBANK")
    
    if df.empty:
        print("❌ Failed to fetch data")
        return
    
    analyzer = AdvancedOptionsAnalyzer(df)
    report = analyzer.get_comprehensive_report()
    
    pcr = report['pcr_analysis']['pcr_oi']
    support, resistance = (
        report['support_resistance']['support_levels'][0][0],
        report['support_resistance']['resistance_levels'][0][0]
    )
    
    print(f"\nNIFTY Bank Analysis:")
    print(f"Support (Put OI): ₹{support:.0f}")
    print(f"Resistance (Call OI): ₹{resistance:.0f}")
    print(f"Expected Range: ₹{support:.0f} - ₹{resistance:.0f}")
    print(f"PCR: {pcr:.2f}")
    
    # Range trading recommendation
    if 0.7 <= pcr <= 1.3:
        print("\n✅ GOOD SETUP FOR RANGE TRADING")
        print("Strategy:")
        print(f"  • BUY: Buy {support:.0f} strike call")
        print(f"  • SELL: Sell {resistance:.0f} strike call")
        print(f"  • EXIT: When price hits either boundary")
        print(f"  • STOP: Beyond support or resistance")
    else:
        print(f"\n⚠️ NOT IDEAL FOR RANGE TRADING (PCR = {pcr:.2f})")
        print("PCR too extreme for typical range trading")


def example_3_sentiment_filter():
    """
    Example 3: Using sentiment as a filter for direction
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Sentiment-Based Trading Direction")
    print("=" * 80)
    
    from options_analyzer import NSEDataFetcher, AdvancedOptionsAnalyzer
    
    # Analyze multiple indices
    indices = ["NIFTY", "NIFTYBANK", "NIFTYIT"]
    
    print("\nFetching data for multiple indices...")
    
    for index in indices:
        try:
            fetcher = NSEDataFetcher()
            df = fetcher.fetch_with_retry(index)
            
            if df.empty:
                print(f"  ❌ {index}: Failed to fetch")
                continue
            
            analyzer = AdvancedOptionsAnalyzer(df)
            pcr = analyzer.get_pcr_analysis()['pcr_oi']
            
            # Determine bias
            if pcr > 1.2:
                bias = "🟢 STRONG BULLISH"
                action = "Buy dips"
            elif pcr > 0.9:
                bias = "🟢 BULLISH"
                action = "Buy on weakness"
            elif pcr < 0.65:
                bias = "🔴 STRONG BEARISH"
                action = "Sell rallies"
            elif pcr < 0.9:
                bias = "🔴 BEARISH"
                action = "Sell on strength"
            else:
                bias = "🟡 NEUTRAL"
                action = "Trade range"
            
            print(f"\n{index}")
            print(f"  PCR: {pcr:.2f}")
            print(f"  Bias: {bias}")
            print(f"  Action: {action}")
        
        except Exception as e:
            print(f"  ❌ {index}: Error - {str(e)}")


def example_4_daily_monitoring():
    """
    Example 4: Daily monitoring script
    Fetch and store data throughout the day
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Daily Monitoring Script")
    print("=" * 80)
    
    from options_analyzer import NSEDataFetcher, AdvancedOptionsAnalyzer
    import pandas as pd
    from datetime import datetime
    
    # This would run throughout the day
    monitoring_data = []
    
    index = "NIFTY"
    print(f"\nStarting daily monitoring of {index}...")
    print("(In real usage, this would run in a loop throughout trading hours)")
    
    try:
        fetcher = NSEDataFetcher()
        df = fetcher.fetch_with_retry(index)
        
        if not df.empty:
            analyzer = AdvancedOptionsAnalyzer(df)
            report = analyzer.get_comprehensive_report()
            
            # Create monitoring record
            record = {
                'timestamp': datetime.now(),
                'index': index,
                'pcr': report['pcr_analysis']['pcr_oi'],
                'support': report['support_resistance']['support_levels'][0][0],
                'resistance': report['support_resistance']['resistance_levels'][0][0],
                'max_pain': report['max_pain']['primary'],
                'iv_regime': report['iv_analysis']['iv_regime'],
                'expected_move': report['expected_move']['expected_move_1sd'],
            }
            
            monitoring_data.append(record)
            
            # Display current status
            df_monitor = pd.DataFrame(monitoring_data)
            print("\n📊 Current Monitoring Data:")
            print(df_monitor.to_string(index=False))
            
            # Show trend
            if len(monitoring_data) > 1:
                print("\n📈 PCR Trend:")
                pcr_values = df_monitor['pcr'].values
                trend = "📈 Rising (More bullish)" if pcr_values[-1] > pcr_values[-2] else "📉 Falling (More bearish)"
                print(f"   {trend}")
    
    except Exception as e:
        print(f"Error during monitoring: {e}")


# ==================== CUSTOMIZATION EXAMPLES ====================

def customize_analysis():
    """
    Example of customizing analysis parameters
    """
    print("\n" + "=" * 80)
    print("HOW TO CUSTOMIZE ANALYSIS")
    print("=" * 80)
    
    print("""
1. Change PCR Thresholds:
   ANALYSIS_CONFIG['pcr_bullish_threshold'] = 1.1  # Instead of 1.0
   ANALYSIS_CONFIG['pcr_bearish_threshold'] = 0.7  # Instead of 0.6

2. Change IV Thresholds:
   ANALYSIS_CONFIG['iv_high_threshold'] = 30  # Consider IV > 30% as high
   ANALYSIS_CONFIG['iv_low_threshold'] = 12   # Consider IV < 12% as low

3. Get More Support/Resistance Levels:
   ANALYSIS_CONFIG['sr_levels_count'] = 10  # Show top 10 instead of 5

4. Use Different Indices:
   Available: NIFTY, NIFTYNXT50, NIFTYIT, NIFTYPHARMA, NIFTYBANK, NIFTYFMCG

5. Customize Dashboard Colors:
   Edit DASHBOARD_CONFIG['colors'] dictionary in this file
   Or modify CSS variables in options_dashboard.py
    """)


# ==================== QUICK START ====================

if __name__ == "__main__":
    import sys
    
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║              INDIAN OPTIONS ANALYZER - EXAMPLE SCRIPTS                     ║
╚═══════════════════════════════════════════════════════════════════════════╝
    
Choose an example to run:
    1. Basic analysis (All 7 metrics explained)
    2. Range trading setup
    3. Sentiment analysis across indices
    4. Daily monitoring script
    5. Customization guide
    0. Exit
    """)
    
    choice = input("Enter choice (0-5): ").strip()
    
    try:
        if choice == "1":
            example_1_basic_analysis()
        elif choice == "2":
            example_2_range_trading()
        elif choice == "3":
            example_3_sentiment_filter()
        elif choice == "4":
            example_4_daily_monitoring()
        elif choice == "5":
            customize_analysis()
        elif choice == "0":
            print("Goodbye! 👋")
            sys.exit(0)
        else:
            print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have installed all requirements:")
        print("  pip install -r requirements.txt")

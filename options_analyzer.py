"""
Advanced Option Chain Analysis Helper Module
Fetches and analyzes Indian stock index options data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from functools import lru_cache
import json

class AdvancedOptionsAnalyzer:
    """Advanced options analysis with additional metrics"""
    
    def __init__(self, df):
        """
        Initialize with option chain dataframe
        df should have columns: strike, call_oi, call_iv, call_ltp, put_oi, put_iv, put_ltp
        """
        self.df = df.copy()
        self.calculate_all_metrics()
    
    def calculate_all_metrics(self):
        """Calculate all analysis metrics"""
        self.df['total_oi'] = self.df['call_oi'] + self.df['put_oi']
        self.df['oi_ratio'] = self.df['call_oi'] / (self.df['put_oi'] + 1)
        self.df['avg_iv'] = (self.df['call_iv'] + self.df['put_iv']) / 2
        self.df['iv_skew'] = self.df['put_iv'] - self.df['call_iv']
        self.df['bid_ask_spread_call'] = abs(self.df['call_ask'] - self.df['call_bid'])
        self.df['bid_ask_spread_put'] = abs(self.df['put_ask'] - self.df['put_bid'])
        self.df['spread_pct_call'] = (self.df['bid_ask_spread_call'] / (self.df['call_ltp'] + 0.01)) * 100
        self.df['spread_pct_put'] = (self.df['bid_ask_spread_put'] / (self.df['put_ltp'] + 0.01)) * 100
    
    def get_pcr_analysis(self):
        """Detailed PCR analysis"""
        total_put_oi = self.df['put_oi'].sum()
        total_call_oi = self.df['call_oi'].sum()
        total_put_iv = self.df['put_iv'].sum()
        total_call_iv = self.df['call_iv'].sum()
        
        pcr_oi = total_put_oi / (total_call_oi + 1)
        pcr_iv = total_put_iv / (total_call_iv + 1)
        
        return {
            'pcr_oi': pcr_oi,
            'pcr_iv': pcr_iv,
            'total_put_oi': total_put_oi,
            'total_call_oi': total_call_oi,
            'total_put_iv': total_put_iv,
            'total_call_iv': total_call_iv
        }
    
    def get_support_resistance_levels(self, top_n=5):
        """Get multiple support and resistance levels"""
        top_puts = self.df.nlargest(top_n, 'put_oi')[['strike', 'put_oi']].values
        top_calls = self.df.nlargest(top_n, 'call_oi')[['strike', 'call_oi']].values
        
        return {
            'support_levels': top_puts,
            'resistance_levels': top_calls
        }
    
    def get_max_pain(self):
        """Calculate max pain with additional analysis"""
        # Multiple methods
        
        # Method 1: Highest total OI
        max_pain_by_total_oi = self.df.loc[self.df['total_oi'].idxmax(), 'strike']
        
        # Method 2: Balance point (where call OI = put OI approximately)
        balance_df = self.df.copy()
        balance_df['oi_diff'] = abs(balance_df['call_oi'] - balance_df['put_oi'])
        max_pain_by_balance = balance_df.loc[balance_df['oi_diff'].idxmin(), 'strike']
        
        # Method 3: Weighted by IV
        balance_df['weighted_oi'] = (
            (balance_df['call_oi'] * balance_df['call_iv'] + 
             balance_df['put_oi'] * balance_df['put_iv']) / 
            (balance_df['call_oi'] + balance_df['put_oi'] + 1)
        )
        max_pain_by_weighted = balance_df.loc[balance_df['weighted_oi'].idxmin(), 'strike']
        
        return {
            'primary': max_pain_by_total_oi,
            'by_balance': max_pain_by_balance,
            'by_iv_weight': max_pain_by_weighted
        }
    
    def get_iv_analysis(self):
        """Analyze implied volatility"""
        return {
            'mean_call_iv': self.df['call_iv'].mean(),
            'mean_put_iv': self.df['put_iv'].mean(),
            'max_call_iv': self.df['call_iv'].max(),
            'max_put_iv': self.df['put_iv'].max(),
            'min_call_iv': self.df['call_iv'].min(),
            'min_put_iv': self.df['put_iv'].min(),
            'iv_skew_mean': self.df['iv_skew'].mean(),
            'iv_skew_max': self.df['iv_skew'].max(),
            'iv_skew_min': self.df['iv_skew'].min(),
            'iv_regime': 'High' if self.df['avg_iv'].mean() > 25 else 'Normal' if self.df['avg_iv'].mean() > 15 else 'Low'
        }
    
    def get_liquidity_analysis(self):
        """Analyze option liquidity"""
        return {
            'call_spread_mean': self.df['spread_pct_call'].mean(),
            'put_spread_mean': self.df['spread_pct_put'].mean(),
            'most_liquid_calls': self.df.nlargest(3, 'call_volume')[['strike', 'call_volume']],
            'most_liquid_puts': self.df.nlargest(3, 'put_volume')[['strike', 'put_volume']],
            'call_volume_total': self.df['call_volume'].sum(),
            'put_volume_total': self.df['put_volume'].sum(),
        }
    
    def get_expected_move(self):
        """Calculate expected move in rupees"""
        atm_iv = self.df['avg_iv'].mean()
        
        # Using ATM strike approximately
        atm_strike = self.df.iloc[len(self.df)//2]['strike']
        
        # Expected move = Strike * IV (for 1 standard deviation)
        expected_move = atm_strike * (atm_iv / 100)
        
        return {
            'expected_move_1sd': expected_move,
            'expected_move_2sd': expected_move * 2,
            'expected_move_pct': (expected_move / atm_strike) * 100,
            'atm_strike': atm_strike
        }
    
    def get_sentiment_signals(self):
        """Generate trading signals based on metrics"""
        pcr = self.get_pcr_analysis()['pcr_oi']
        iv_info = self.get_iv_analysis()
        max_pain = self.get_max_pain()
        
        signals = []
        
        # Signal 1: PCR based
        if pcr > 1.5:
            signals.append({
                'signal': 'STRONG BULLISH',
                'reason': f'Very high PCR ({pcr:.2f})',
                'confidence': 'High',
                'icon': '🟢🟢🟢'
            })
        elif pcr > 1:
            signals.append({
                'signal': 'BULLISH',
                'reason': f'High PCR ({pcr:.2f})',
                'confidence': 'Medium',
                'icon': '🟢🟢'
            })
        elif pcr < 0.6:
            signals.append({
                'signal': 'STRONG BEARISH',
                'reason': f'Very low PCR ({pcr:.2f})',
                'confidence': 'High',
                'icon': '🔴🔴🔴'
            })
        elif pcr < 1:
            signals.append({
                'signal': 'BEARISH',
                'reason': f'Low PCR ({pcr:.2f})',
                'confidence': 'Medium',
                'icon': '🔴🔴'
            })
        else:
            signals.append({
                'signal': 'NEUTRAL',
                'reason': f'Balanced PCR ({pcr:.2f})',
                'confidence': 'Low',
                'icon': '🟡'
            })
        
        # Signal 2: IV regime
        if iv_info['iv_regime'] == 'High':
            signals.append({
                'signal': 'HIGH VOLATILITY',
                'reason': f"IV Regime: {iv_info['iv_regime']} ({iv_info['mean_put_iv']:.2f}%)",
                'confidence': 'High',
                'icon': '📈'
            })
        
        return signals
    
    def get_comprehensive_report(self):
        """Generate comprehensive analysis report"""
        return {
            'timestamp': datetime.now(),
            'pcr_analysis': self.get_pcr_analysis(),
            'support_resistance': self.get_support_resistance_levels(),
            'max_pain': self.get_max_pain(),
            'iv_analysis': self.get_iv_analysis(),
            'liquidity_analysis': self.get_liquidity_analysis(),
            'expected_move': self.get_expected_move(),
            'signals': self.get_sentiment_signals(),
            'data_summary': {
                'total_strikes': len(self.df),
                'max_total_oi': self.df['total_oi'].max(),
                'avg_total_oi': self.df['total_oi'].mean(),
                'strike_range': f"{self.df['strike'].min():.0f} - {self.df['strike'].max():.0f}"
            }
        }


class NSEDataFetcher:
    """Enhanced NSE data fetcher with retry logic"""
    
    def __init__(self, max_retries=3):
        self.base_url = "https://www.nseindia.com/api/option-chain-indices"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.max_retries = max_retries
        self.session = requests.Session()
    
    def fetch_with_retry(self, index="NIFTY", expiry=""):
        """Fetch with automatic retry on failure"""
        for attempt in range(self.max_retries):
            try:
                params = {"index": index}
                if expiry:
                    params["expiry_date"] = expiry
                
                response = self.session.get(
                    self.base_url,
                    params=params,
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._process_option_chain(data)
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    continue
                else:
                    raise
        
        return pd.DataFrame()
    
    def _process_option_chain(self, data):
        """Process raw API response"""
        records = data.get("records", {}).get("data", [])
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


# Example usage and testing
if __name__ == "__main__":
    fetcher = NSEDataFetcher()
    
    print("Fetching NIFTY option chain...")
    df = fetcher.fetch_with_retry("NIFTY")
    
    if not df.empty:
        analyzer = AdvancedOptionsAnalyzer(df)
        report = analyzer.get_comprehensive_report()
        
        print("\n" + "="*50)
        print("OPTIONS ANALYSIS REPORT")
        print("="*50)
        print(f"\nTimestamp: {report['timestamp']}")
        print(f"\nData Summary: {report['data_summary']}")
        print(f"\nPCR Analysis: {report['pcr_analysis']['pcr_oi']:.2f}")
        print(f"\nMax Pain Levels: {report['max_pain']}")
        print(f"\nSignals: {[s['signal'] for s in report['signals']]}")

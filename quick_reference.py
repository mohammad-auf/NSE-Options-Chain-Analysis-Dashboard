#!/usr/bin/env python3
"""
Quick Reference for Options Chain Analysis
Print or screenshot this for quick lookup while trading
"""

REFERENCE_CARD = """
╔════════════════════════════════════════════════════════════════════════════╗
║            INDIAN OPTIONS CHAIN ANALYSIS - QUICK REFERENCE                 ║
╚════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. MARKET SENTIMENT                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ Highest Call OI Strike vs Highest Put OI Strike                             │
│                                                                              │
│ 📈 BULLISH:  Put OI > Call OI                                              │
│    Reason: Traders buying downside protection (puts) → expect support      │
│    Action: Look for longs, buy support levels                              │
│                                                                              │
│ 📉 BEARISH:  Call OI > Put OI                                              │
│    Reason: Traders buying upside (calls) → expect resistance               │
│    Action: Look for shorts, sell resistance levels                         │
│                                                                              │
│ ↔️ NEUTRAL:  Call OI ≈ Put OI                                              │
│    Reason: Balanced sentiment, no clear direction                          │
│    Action: Trade within range, avoid directional bets                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. SUPPORT & RESISTANCE                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ 🛡️ SUPPORT = Strike with Highest Put OI                                    │
│    This is where buyers expect market to bounce up                         │
│    High put OI = Traders protecting from downside                          │
│                                                                              │
│    Example: 24,500 strike has put OI of 800,000                            │
│    → Market likely supported at 24,500                                      │
│    → Buying 24,500 call might be safe                                      │
│                                                                              │
│ 🔪 RESISTANCE = Strike with Highest Call OI                                │
│    This is where sellers expect market to face selling                     │
│    High call OI = Traders expect resistance here                           │
│                                                                              │
│    Example: 25,000 strike has call OI of 750,000                           │
│    → Market likely faces selling at 25,000                                 │
│    → Selling 25,000 call might capture premium                             │
│                                                                              │
│ EXPECTED RANGE = Support to Resistance                                      │
│    Market likely trades between these two levels by expiry                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. PUT-CALL RATIO (PCR)                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ Formula: Total Put OI ÷ Total Call OI                                       │
│                                                                              │
│ > 1.5   🟢🟢🟢 STRONG BULLISH - Extreme hedging (watch for contrarian)    │
│ 1.0-1.5 🟢🟢  BULLISH - Healthy hedging activity                          │
│ 0.7-1.0 🟡    NEUTRAL - Balanced positioning                              │
│ 0.6-0.7 🔴🔴  BEARISH - Low hedging, traders confident (or foolish)       │
│ < 0.6   🔴🔴🔴 STRONG BEARISH - Very low puts (watch for reversal)        │
│                                                                              │
│ RULE OF THUMB:                                                              │
│ • PCR > 1.2 → Bullish bias, support likely to hold                        │
│ • PCR < 0.8 → Bearish bias, resistance likely to cap gains                │
│ • Extreme PCR (>2 or <0.5) → Contrarian signal possible                  │
│                                                                              │
│ Example:                                                                     │
│   Total Put OI = 3,000,000                                                 │
│   Total Call OI = 2,000,000                                                │
│   PCR = 3,000,000 ÷ 2,000,000 = 1.50 → BULLISH                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. TRADER POSITIONING (Price + OI Change)                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ Price ↑  OI ↑  =  LONG BUILDUP       📈 Most Bullish                      │
│          Traders buying calls, building longs                              │
│          → Expect price to continue up                                      │
│                                                                              │
│ Price ↓  OI ↑  =  SHORT BUILDUP      📉 Most Bearish                      │
│          Traders selling, building shorts                                  │
│          → Expect price to continue down                                    │
│                                                                              │
│ Price ↑  OI ↓  =  SHORT COVERING     🔒 Bullish                            │
│          Shorts buying back (covering losses)                              │
│          → Likely bottomed, uptrend starting                                │
│                                                                              │
│ Price ↓  OI ↓  =  LONG UNWINDING     😅 Bearish                            │
│          Longs selling (closing profits/losses)                            │
│          → Likely peaked, downtrend starting                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. IMPLIED VOLATILITY (IV)                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ What it means: Expected movement in 30-45 days                              │
│                                                                              │
│ HIGH IV (>25%)                                                              │
│   → Market expects big moves ↕️                                              │
│   → Before earnings/RBI announcements                                       │
│   → Good for selling premium (high value)                                   │
│   → Straddles/strangles expensive but good for range traders               │
│                                                                              │
│ NORMAL IV (15-25%)                                                          │
│   → Regular trading conditions                                              │
│   → Good for directional trading                                            │
│   → Best balance of risk/reward                                             │
│                                                                              │
│ LOW IV (<15%)                                                               │
│   → Market expects small moves ↔️                                            │
│   → Sideways/consolidation expected                                         │
│   → Poor for premium selling (low value)                                    │
│   → Good for range-bound options selling                                    │
│                                                                              │
│ IV SKEW (Put IV - Call IV)                                                  │
│   > 0 → Puts more expensive → Market fears downside                        │
│   < 0 → Calls more expensive → Market expects upside                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 6. MAX PAIN LEVEL                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ Definition: Strike where MOST option buyers lose maximum money at expiry   │
│                                                                              │
│ Why it matters:                                                              │
│   • Market sometimes gravitates toward max pain level on expiry day        │
│   • Especially strong in last 1-3 days before expiry                       │
│   • Large traders may be protecting positions around this level            │
│                                                                              │
│ How to use it:                                                              │
│   • If max pain is 24,900 and market is at 25,200 on day before expiry   │
│   → Watch for potential pullback to 24,900                                 │
│   • Don't trade solely on max pain, use as ADDITIONAL confirmation         │
│                                                                              │
│ Important: Max pain is NOT guaranteed. It's a probability, not destiny     │
│            Strong news/events can override max pain                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ TRADING DECISION FLOW                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  START → Check PCR                                                          │
│           ↓                                                                  │
│      PCR > 1.2?  →YES→ Bullish bias, buy support                           │
│        ↓ NO                                                                  │
│      PCR < 0.7?  →YES→ Bearish bias, sell resistance                       │
│        ↓ NO                                                                  │
│      → Neutral, trade range between Support & Resistance                    │
│                                                                              │
│  CONFIRM with:                                                              │
│    □ Is price near support/resistance?                                      │
│    □ Is IV rising or falling? (direction)                                   │
│    □ What's the Price-OI signal? (long/short buildup)                      │
│    □ Is max pain aligned with your bias?                                    │
│                                                                              │
│  EXECUTE:                                                                    │
│    ✓ Buy support level on dips (if PCR > 1.0)                              │
│    ✓ Sell resistance on rallies (if PCR < 1.0)                             │
│    ✓ Hold range trades (if PCR = neutral)                                  │
│    ✓ Avoid trading without 2-3 signals aligned                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ QUICK CHECKLIST - Before Every Trade                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ ☐ Is PCR confirming my trade direction? (BUY=PCR>1, SELL=PCR<0.8)         │
│ ☐ Is price near support (for buys) or resistance (for sells)?              │
│ ☐ Is IV trending in favor of my position?                                  │
│ ☐ Do Price+OI changes confirm my bias?                                     │
│ ☐ Is max pain at least neutral to my trade?                                │
│ ☐ Do I have proper risk/reward (2:1 minimum)?                              │
│ ☐ Is market in trending or ranging mode?                                   │
│ ☐ Do I have 2-3 confluent signals, not just 1?                             │
│                                                                              │
│ If ALL checks pass → Proceed with trade                                     │
│ If < 3 checks pass → Wait for better setup                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

╔════════════════════════════════════════════════════════════════════════════╗
║ GOLDEN RULES:                                                              ║
║  1. Never trade solely on one metric                                       ║
║  2. Combine PCR + Support/Resistance + Price-OI analysis                   ║
║  3. Extreme metrics (PCR >1.5, <0.5) = Potential reversals                 ║
║  4. Low liquidity = Wide spreads, avoid such strikes                       ║
║  5. Trade the option expiry near support/resistance for theta decay        ║
║  6. Don't hold overnight on expiry day (IV crash risk)                     ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

if __name__ == "__main__":
    print(REFERENCE_CARD)
    
    # Optional: Save to file
    with open("OPTIONS_QUICK_REFERENCE.txt", "w", encoding="utf-8") as f:
        f.write(REFERENCE_CARD)
    print("\n✅ Reference card saved to OPTIONS_QUICK_REFERENCE.txt")
    print("💡 Print this or save it for quick lookup during trading hours!")

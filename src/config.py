"""
config.py — Global constants, index definitions, color system
"""

# ── Index Definitions ─────────────────────────────────────────────────────────

INDICES = {
    "NIFTY": {
        "display": "NIFTY 50",
        "symbol": "NIFTY",
        "nse_symbol": "NIFTY",
        "base_price": 24500,
        "strike_step": 50,
        "lot_size": 25,
        "description": "NSE Nifty 50 Index",
        "color": "#00D4FF",
    },
    "BANKNIFTY": {
        "display": "BANK NIFTY",
        "symbol": "BANKNIFTY",
        "nse_symbol": "BANKNIFTY",
        "base_price": 52000,
        "strike_step": 100,
        "lot_size": 15,
        "description": "NSE Bank Nifty Index",
        "color": "#7C3AED",
    },
    "FINNIFTY": {
        "display": "FIN NIFTY",
        "symbol": "FINNIFTY",
        "nse_symbol": "FINNIFTY",
        "base_price": 23500,
        "strike_step": 50,
        "lot_size": 40,
        "description": "NSE Fin Nifty Index",
        "color": "#10B981",
    },
    "MIDCPNIFTY": {
        "display": "MIDCP NIFTY",
        "symbol": "MIDCPNIFTY",
        "nse_symbol": "MIDCPNIFTY",
        "base_price": 12500,
        "strike_step": 25,
        "lot_size": 75,
        "description": "NSE Midcap Nifty Index",
        "color": "#F59E0B",
    },
    "SENSEX": {
        "display": "SENSEX",
        "symbol": "SENSEX",
        "nse_symbol": "SENSEX",
        "base_price": 80000,
        "strike_step": 100,
        "lot_size": 10,
        "description": "BSE Sensex Index",
        "color": "#EF4444",
    },
}

DEFAULT_INDEX = "NIFTY"

# ── Color System ──────────────────────────────────────────────────────────────

COLORS = {
    # Theme
    "bg_primary":     "#020614",
    "bg_secondary":   "#070D1E",
    "bg_card":        "#0C1428",
    "bg_card_hover":  "#0F1A30",
    "border":         "rgba(0, 212, 255, 0.12)",
    "border_bright":  "rgba(0, 212, 255, 0.4)",

    # Signal colors
    "bullish":        "#00E676",
    "bullish_dim":    "#00C853",
    "bearish":        "#FF4444",
    "bearish_dim":    "#D32F2F",
    "neutral":        "#FFD600",
    "warning":        "#FF9800",
    "info":           "#00D4FF",
    "purple":         "#7C3AED",

    # Text
    "text_primary":   "#E8EAF0",
    "text_secondary": "#8892A4",
    "text_muted":     "#4A5568",

    # Gradients (CSS strings)
    "grad_bullish":   "linear-gradient(135deg, #00E676 0%, #00C853 100%)",
    "grad_bearish":   "linear-gradient(135deg, #FF4444 0%, #D32F2F 100%)",
    "grad_info":      "linear-gradient(135deg, #00D4FF 0%, #0099CC 100%)",
    "grad_purple":    "linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%)",
    "grad_neutral":   "linear-gradient(135deg, #FFD600 0%, #FF9800 100%)",
}

# ── Plotly Dark Template ──────────────────────────────────────────────────────

PLOTLY_TEMPLATE = {
    "layout": {
        "paper_bgcolor": "rgba(7, 13, 30, 0.0)",
        "plot_bgcolor":  "rgba(7, 13, 30, 0.0)",
        "font":          {"color": "#8892A4", "family": "Inter, sans-serif", "size": 12},
        "title":         {"font": {"color": "#E8EAF0", "size": 14, "family": "Inter, sans-serif"}},
        "xaxis": {
            "gridcolor":     "rgba(255,255,255,0.04)",
            "zerolinecolor": "rgba(255,255,255,0.08)",
            "tickcolor":     "#4A5568",
            "linecolor":     "rgba(255,255,255,0.06)",
        },
        "yaxis": {
            "gridcolor":     "rgba(255,255,255,0.04)",
            "zerolinecolor": "rgba(255,255,255,0.08)",
            "tickcolor":     "#4A5568",
            "linecolor":     "rgba(255,255,255,0.06)",
        },
        "legend": {
            "bgcolor":      "rgba(7,13,30,0.6)",
            "bordercolor":  "rgba(0,212,255,0.15)",
            "borderwidth":  1,
            "font":         {"color": "#8892A4", "size": 11},
        },
        # NOTE: no "margin" key here — pass it per-chart to avoid duplicate-keyword errors
        "hoverlabel": {
            "bgcolor":    "#0C1428",
            "bordercolor": "rgba(0,212,255,0.3)",
            "font":       {"color": "#E8EAF0", "size": 12},
        },
    }
}

_DEFAULT_MARGIN = {"l": 50, "r": 20, "t": 40, "b": 40}


def plotly_layout(height: int = 400, margin: dict = None, **extra) -> dict:
    """
    Return a merged layout dict for fig.update_layout(**plotly_layout(...)).

    Usage:
        fig.update_layout(**plotly_layout(height=380, margin=dict(l=40, r=10, t=10, b=30),
                                          xaxis_title="Strike"))

    This is the safe replacement for:
        fig.update_layout(height=380, **PLOTLY_TEMPLATE["layout"],
                          margin=dict(...))   # ← would raise duplicate-key error
    """
    layout = dict(PLOTLY_TEMPLATE["layout"])
    layout["height"] = height
    layout["margin"] = margin if margin is not None else _DEFAULT_MARGIN
    layout.update(extra)
    return layout


# ── Market Timing ─────────────────────────────────────────────────────────────

MARKET_OPEN_HOUR   = 9
MARKET_OPEN_MIN    = 15
MARKET_CLOSE_HOUR  = 15
MARKET_CLOSE_MIN   = 30

# ── Risk-Free Rate ────────────────────────────────────────────────────────────

RISK_FREE_RATE = 0.065   # 6.5% — approximate Indian 91-day T-bill

# ── Sentiment Thresholds ──────────────────────────────────────────────────────

PCR_BULLISH    = 1.2
PCR_BEARISH    = 0.8
IV_HIGH_PCTILE = 70
IV_LOW_PCTILE  = 30

# ── Strategy Definitions ──────────────────────────────────────────────────────

STRATEGIES = [
    "Long Call",
    "Long Put",
    "Bull Call Spread",
    "Bear Put Spread",
    "Iron Condor",
    "Iron Fly",
    "Straddle",
    "Strangle",
]

# ── Watchlist Defaults ────────────────────────────────────────────────────────

DEFAULT_WATCHLIST = list(INDICES.keys())

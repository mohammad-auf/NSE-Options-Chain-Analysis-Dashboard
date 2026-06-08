"""
analytics/greeks.py — Black-Scholes option pricing and Greeks calculator
"""

import numpy as np
from scipy import stats
from scipy.stats import norm


def _d1_d2(S, K, T, r, sigma):
    """Compute d1 and d2 for Black-Scholes."""
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return 0.0, 0.0
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2


def bs_price(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call") -> float:
    """
    Black-Scholes option price.
    S: spot, K: strike, T: time to expiry (years), r: risk-free rate, sigma: IV, option_type: 'call'/'put'
    """
    if T <= 0:
        if option_type == "call":
            return max(0.0, S - K)
        else:
            return max(0.0, K - S)

    d1, d2 = _d1_d2(S, K, T, r, sigma)

    if option_type == "call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    return max(0.0, price)


def delta(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call") -> float:
    """Option delta."""
    if T <= 0:
        if option_type == "call":
            return 1.0 if S > K else 0.0
        else:
            return -1.0 if S < K else 0.0
    d1, _ = _d1_d2(S, K, T, r, sigma)
    if option_type == "call":
        return float(norm.cdf(d1))
    else:
        return float(norm.cdf(d1) - 1)


def gamma(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Option gamma (same for call and put)."""
    if T <= 0 or sigma <= 0:
        return 0.0
    d1, _ = _d1_d2(S, K, T, r, sigma)
    return float(norm.pdf(d1) / (S * sigma * np.sqrt(T)))


def theta(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call") -> float:
    """Option theta (per day)."""
    if T <= 0 or sigma <= 0:
        return 0.0
    d1, d2 = _d1_d2(S, K, T, r, sigma)
    term1 = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
    if option_type == "call":
        term2 = -r * K * np.exp(-r * T) * norm.cdf(d2)
    else:
        term2 = r * K * np.exp(-r * T) * norm.cdf(-d2)
    return float((term1 + term2) / 365)


def vega(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Option vega (per 1% change in IV)."""
    if T <= 0 or sigma <= 0:
        return 0.0
    d1, _ = _d1_d2(S, K, T, r, sigma)
    return float(S * norm.pdf(d1) * np.sqrt(T) * 0.01)


def rho(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call") -> float:
    """Option rho (per 1% change in rate)."""
    if T <= 0 or sigma <= 0:
        return 0.0
    _, d2 = _d1_d2(S, K, T, r, sigma)
    if option_type == "call":
        return float(K * T * np.exp(-r * T) * norm.cdf(d2) * 0.01)
    else:
        return float(-K * T * np.exp(-r * T) * norm.cdf(-d2) * 0.01)


def all_greeks(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call") -> dict:
    """Return all Greeks as a dict."""
    return {
        "price":  bs_price(S, K, T, r, sigma, option_type),
        "delta":  delta(S, K, T, r, sigma, option_type),
        "gamma":  gamma(S, K, T, r, sigma),
        "theta":  theta(S, K, T, r, sigma, option_type),
        "vega":   vega(S, K, T, r, sigma),
        "rho":    rho(S, K, T, r, sigma, option_type),
    }


def implied_volatility(market_price: float, S: float, K: float, T: float, r: float,
                       option_type: str = "call", tol: float = 1e-5, max_iter: int = 100) -> float:
    """
    Newton-Raphson method to compute implied volatility.
    Returns IV in decimal form (e.g. 0.15 = 15%).
    """
    if T <= 0 or market_price <= 0:
        return 0.0

    sigma = 0.2  # initial guess
    for _ in range(max_iter):
        price  = bs_price(S, K, T, r, sigma, option_type)
        v      = vega(S, K, T, r, sigma) / 0.01  # raw vega
        if abs(v) < 1e-10:
            break
        diff   = market_price - price
        if abs(diff) < tol:
            break
        sigma += diff / v
        sigma = max(0.001, min(sigma, 5.0))  # clamp

    return sigma


def gamma_exposure(strikes, call_ois, put_ois, gammas_call, gammas_put, lot_size: int = 25) -> list:
    """
    Gamma Exposure (GEX) per strike.
    GEX = (Call OI * Gamma_call - Put OI * Gamma_put) * lot_size
    """
    gex = []
    for i, s in enumerate(strikes):
        call_gex = call_ois[i] * gammas_call[i] * lot_size
        put_gex  = put_ois[i]  * gammas_put[i]  * lot_size
        gex.append(call_gex - put_gex)
    return gex

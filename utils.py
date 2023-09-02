from datetime import datetime
from flask import jsonify, request, Response
from functools import wraps
from cache_interface import CacheInterface
from configurations import Config
from constants import *
from errors import UNAUTHORIZED

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("x-api-key")
        if api_key == Config.ADMIN_API_KEY:
            return f(*args, **kwargs)
        return build_error(UNAUTHORIZED, 401)

    return decorated

def get_cache_duration(current_time: datetime, high_low_ratio: float) -> int:
    """
    Calculate the cache duration based on trading hours and volatility.

    Args:
        current_time (datetime.time): Current time.
        high_low_ratio (float): Ratio of high to low stock price.

    Returns:
        int: Cache duration in seconds.
    """
    if TRADING_HOUR_START <= current_time.hour < TRADING_HOUR_END:
        return (
            CACHE_DURATION_HIGH_VOLATILITY
            if high_low_ratio > HIGH_LOW_RATIO_THRESHOLD
            else CACHE_DURATION_LOW_VOLATILITY
        )
    else:
        return CACHE_DURATION_NON_TRADING


def build_error(error_string: str, error_code: int = 500) -> Response:
    return jsonify({"error": error_string}), error_code

def increment_cost_counter(cache: CacheInterface):
    current_cost = cache.get(COST_COUNTER) or 0.0
    new_cost = current_cost + QUERY_COST
    cache.set(COST_COUNTER, new_cost)

def update_cache(cache: CacheInterface, symbol: str, stock_data: dict, current_time: datetime):
    increment_cost_counter(cache)
    high_low_ratio = stock_data.get(HIGH_LOW_RATIO)
    stock_quote_data = stock_data.get(STOCK_QUOTE_DATA)
    cache_time = get_cache_duration(current_time, high_low_ratio)
    cache.set_with_expiry(symbol, stock_quote_data, cache_time)
    
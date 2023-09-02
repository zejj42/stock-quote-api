from flask import jsonify, request
from functools import wraps
import json
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

def get_cache_duration(current_time, high_low_ratio):
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


def build_error(error_string, error_code=500):
    return jsonify({"error": error_string}), error_code

def increment_cost_counter(cache):
    current_cost = get_float_from_cache(cache, "cost_counter")
    new_cost = current_cost + QUERY_COST
    cache.set("cost_counter", str(new_cost))

def update_cache(cache, symbol, stock_data, current_time):
    increment_cost_counter(cache)
    high_low_ratio = stock_data.get("high_low_ratio")
    stock_quote_data = stock_data.get("stock_quote_data")
    cache_time = get_cache_duration(current_time, high_low_ratio)
    cache.setex(symbol, cache_time, json.dumps(stock_quote_data))



def get_float_from_cache(cache, key):
    """Retrieve a floating-point value from Redis cache.

    Args:
        cache: Redis cache instance.
        key (str): Key to retrieve from cache.

    Returns:
        float: Floating-point value of the key in cache.
    """
    return float(cache.get(key).decode("utf-8"))

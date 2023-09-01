from constants import *


def get_cache_duration(current_time, high_low_ratio):
    if TRADING_HOUR_START <= current_time.hour < TRADING_HOUR_END:
        return (
            CACHE_DURATION_HIGH_VOLATILITY
            if high_low_ratio > HIGH_LOW_RATIO_THRESHOLD
            else CACHE_DURATION_LOW_VOLATILITY
        )
    else:
        return CACHE_DURATION_NON_TRADING

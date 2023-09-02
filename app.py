from flask import Flask, jsonify
import datetime
from cache_interface import CacheFactory
from configurations import Config
from stock_api import StockAPIFactory
from errors import SYMBOL_NOT_FOUND, FETCH_STOCK_DATA_FAILED
from utils import build_error, requires_auth, update_cache
from constants import *


API_NAME = Config.API_NAME 
api_client = StockAPIFactory.create(API_NAME)

CACHE_NAME = Config.CACHE_NAME
cache = CacheFactory.create(CACHE_NAME)

app = Flask(__name__)


if not cache.exists(COST_COUNTER):
    cache.set(COST_COUNTER, COST_COUNTER_RESET_VALUE)

@app.route("/quote/<symbol>", methods=["GET"])
def get_quote(symbol):
    symbol = symbol.upper()
    cached_data = cache.get(symbol)

    if cached_data:
        return jsonify(cached_data)
    
    current_time = datetime.datetime.now()
    stock_data = api_client.get_stock_quote(symbol, current_time)

    if stock_data == SYMBOL_NOT_FOUND:
          return build_error(SYMBOL_NOT_FOUND, 404)
    if stock_data is None:
        return build_error(FETCH_STOCK_DATA_FAILED)

    
    update_cache(cache, symbol, stock_data, current_time)
    return jsonify(stock_data.get(STOCK_QUOTE_DATA))


@app.route("/cost", methods=["GET"])
@requires_auth
def get_cost():
    cost_counter = cache.get(COST_COUNTER) or COST_COUNTER_RESET_VALUE
    return jsonify({"total_cost": cost_counter})


@app.route("/reset_cost", methods=["POST"])
@requires_auth
def reset_cost():
    cache.set(COST_COUNTER, COST_COUNTER_RESET_VALUE)
    return jsonify({"status": "Cost counter reset"})


if __name__ == "__main__":
    app.run(host=Config.APP_HOST, port=Config.APP_PORT)

from flask import Flask, jsonify
from functools import wraps
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
import redis
import json
import datetime
from configurations import Config
from stock_api import StockAPIFactory
from errors import SYMBOL_NOT_FOUND, FETCH_STOCK_DATA_FAILED
from utils import build_error, get_float_from_cache, requires_auth, update_cache

API_NAME = Config.API_NAME 
ADMIN_API_KEY = Config.ADMIN_API_KEY
api_client = StockAPIFactory.create(API_NAME)

app = Flask(__name__)
cache = redis.StrictRedis(host=Config.CACHE_HOST, port=Config.CACHE_PORT, db=Config.CACHE_DB)
limiter = Limiter(app, key_func=get_remote_address, default_limits=["10 per minute"])

if not cache.exists("cost_counter"):
    cache.set("cost_counter", 0)

@app.route("/quote/<symbol>", methods=["GET"])
@limiter.limit("10/minute")
def get_quote(symbol):
    symbol = symbol.upper()
    cached_data = cache.get(symbol)

    if cached_data:
        return jsonify(json.loads(cached_data))
    
    current_time = datetime.datetime.now()
    stock_data = api_client.get_stock_quote(symbol, current_time)

    if stock_data == SYMBOL_NOT_FOUND:
          return build_error(SYMBOL_NOT_FOUND, 404)
    if stock_data is None:
        return build_error(FETCH_STOCK_DATA_FAILED)

    
    update_cache(cache, symbol, stock_data, current_time)
    return jsonify(stock_data.get("stock_quote_data"))


@app.route("/cost", methods=["GET"])
@requires_auth
def get_cost():
    cost_counter = get_float_from_cache(cache, "cost_counter")
    return jsonify({"total_cost": cost_counter})


@app.route("/reset_cost", methods=["POST"])
@requires_auth
def reset_cost():
    cache.set("cost_counter", 0)
    return jsonify({"status": "Cost counter reset"})


if __name__ == "__main__":
    app.run(host=Config.APP_HOST, port=Config.APP_PORT)

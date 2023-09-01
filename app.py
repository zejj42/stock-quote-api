from flask import Flask, request, jsonify
import requests
import redis
import json
import datetime
from errors import SYMBOL_NOT_FOUND, UNAUTHORIZED, FETCH_STOCK_DATA_FAILED
from utils import get_cache_duration
from constants import QUERY_COST


ADMIN_API_KEY = "k78a0snbf8JHm"
ALPHAVANTAGE_API_URL = "https://www.alphavantage.co/query"
ALPHAVANTAGE_API_KEY = "3E11545CAV72Q0C2"

app = Flask(__name__)
cache = redis.StrictRedis(host="redis", port=6379, db=0)

cost_counter = 0

from functools import wraps


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("x-api-key")
        if api_key == ADMIN_API_KEY:
            return f(*args, **kwargs)
        return jsonify(UNAUTHORIZED), 401

    return decorated


def get_stock_quote(symbol):
    try:
        params = {
            "function": "GLOBAL_QUOTE",
            "apikey": ALPHAVANTAGE_API_KEY,
            "symbol": symbol,
        }
        response = requests.get(ALPHAVANTAGE_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("Global Quote", {})

    except requests.RequestException:
        return None


@app.route("/quote/<symbol>", methods=["GET"])
def get_quote(symbol):
    global cost_counter
    symbol = symbol.upper()

    cached_data = cache.get(symbol)

    if cached_data:
        return jsonify(json.loads(cached_data))

    stock_data = get_stock_quote(symbol)

    if stock_data is None:
        return jsonify(FETCH_STOCK_DATA_FAILED), 500
    elif not stock_data:
        return jsonify(SYMBOL_NOT_FOUND), 404

    cost_counter += QUERY_COST

    current_time = datetime.datetime.now()
    high_low_ratio = float(stock_data["03. high"]) / float(stock_data["04. low"])

    cache_time = get_cache_duration(current_time, high_low_ratio)

    stock_quote_data = {
        "symbol": stock_data["01. symbol"],
        "update_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "price": stock_data["05. price"],
        "change_percent": stock_data["10. change percent"],
    }
    cache.setex(symbol, cache_time, json.dumps(stock_quote_data))

    return jsonify(stock_quote_data)


@app.route("/cost", methods=["GET"])
@requires_auth
def get_cost():
    return jsonify({"total_cost": cost_counter})


@app.route("/reset_cost", methods=["POST"])
@requires_auth
def reset_cost():
    global cost_counter
    cost_counter = 0
    return jsonify({"status": "Cost counter reset"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

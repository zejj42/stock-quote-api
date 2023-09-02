from abc import ABC, abstractmethod
import requests
from configurations import Config
from constants import *
from errors import SYMBOL_NOT_FOUND

class StockAPIInterface(ABC):
    
    @abstractmethod
    def get_stock_quote(self, symbol, current_time):
        pass
    
    @abstractmethod
    def extract_stock_data(self, data, current_time):
        pass

class AlphaVantageAPI(StockAPIInterface):

    API_KEY = Config.ALPHAVANTAGE_API_KEY
    API_URL = Config.ALPHAVANTAGE_API_URL

    def get_stock_quote(self, symbol, current_time):
        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "apikey": self.API_KEY,
                "symbol": symbol,
            }
            response = requests.get(self.API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            global_quote_data = data.get("Global Quote", {})

            if not global_quote_data:
                return SYMBOL_NOT_FOUND
            
            return self.extract_stock_data(global_quote_data, current_time)

        except requests.RequestException:
            return None

    def extract_stock_data(self, data, current_time):
        stock_quote_data = {
            SYMBOL: data["01. symbol"],
            UPDATE_TIME: current_time.strftime("%Y-%m-%d %H:%M:%S"),
            PRICE: data["05. price"],
            CHANGE_PERCENT: data["10. change percent"],
        }
        high_low_ratio = float(data["03. high"]) / float(data["04. low"])
        return { STOCK_QUOTE_DATA: stock_quote_data, HIGH_LOW_RATIO: high_low_ratio }

class StockAPIFactory:
    
    @staticmethod
    def create(api_name: str):
        supported_apis = [ALPHA_VANTAGE]

        if api_name in supported_apis:
            if api_name == ALPHA_VANTAGE:
                return AlphaVantageAPI()
        else:
            raise ValueError(f"API {api_name} not supported")

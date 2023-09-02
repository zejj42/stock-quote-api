from abc import ABC, abstractmethod
from configurations import Config
import requests

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
            "symbol": data["01. symbol"],
            "update_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "price": data["05. price"],
            "change_percent": data["10. change percent"],
        }
        high_low_ratio = float(data["03. high"]) / float(data["04. low"])
        return { "stock_quote_data": stock_quote_data, "high_low_ratio": high_low_ratio }

class StockAPIFactory:

    @staticmethod
    def create(api_name):
        if api_name == Config.API_NAME:
            return AlphaVantageAPI()
        else:
            raise ValueError(f"API {api_name} not supported")

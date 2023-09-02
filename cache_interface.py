from abc import ABC, abstractmethod
from redis import Redis
import redis
import json
from typing import Any, Optional, Union, Type, Dict
from configurations import Config
from constants import REDIS

class CacheInterface(ABC):

    @abstractmethod
    def exists(self, key: str) -> bool:
        pass
    
    @abstractmethod
    def get(self, key: str) -> Union[None, float, Dict]:
        pass

    @abstractmethod
    def set(self, key: str, value: Union[float, Dict]):
        pass

    @abstractmethod
    def set_with_expiry(self, key: str, value: Union[float, Dict], expiry_time: int):
        pass


class RedisCache(CacheInterface):

    def __init__(self, client: Redis):
        self.client = client

    def exists(self, key: str) -> bool:
        return bool(self.client.exists(key))    

    def get(self, key: str) ->  Union[None, float, Dict]:
        value = self.client.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value.decode("utf-8") 

    def set(self, key: str, value: Union[float, Dict]): 
        if isinstance(value, (dict, list, tuple)):
            self.client.set(key, json.dumps(value))
        else:
            self.client.set(key, str(value))

    def set_with_expiry(self, key: str, value: Union[float, Dict], expiry_time: int): 
        if isinstance(value, (dict, list, tuple)):
            value_str = json.dumps(value)
        else:
            value_str = str(value)
        self.client.setex(key, expiry_time, value_str)

class CacheFactory:

    @staticmethod
    def create(cache_name: str) -> Type[CacheInterface]:
        supported_caches = [REDIS]  

        if cache_name in supported_caches:
            if cache_name == REDIS:
                cache_client = redis.StrictRedis(host=Config.CACHE_HOST, port=Config.CACHE_PORT, db=Config.CACHE_DB)
                return RedisCache(cache_client)
        else:
            raise ValueError(f"Cache {cache_name} not supported")
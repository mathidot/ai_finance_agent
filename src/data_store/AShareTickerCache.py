import redis
import pandas as pd
import redis.client
import redis.exceptions
from src.utils.logging_config import setup_logger
from src.config import app_config
import time
from threading import Lock, Timer
from typing import Callable, Any, Union
import json
from src.tools.api import get_all_a_share_tickers

logger = setup_logger("AShareTickerCache")

class AShareTickerCache:
    _instance: 'AShareTickerCache' = None
    _tickers_df: pd.DataFrame = pd.DataFrame()
    _last_fetched_local_time: float | None = None
    _redis_client: redis.client.Redis | None = None
    _redis_key: str = "ashare_tickers_df"
    _redis_ttl_seconds: int = app_config.get("ashare_data_ttl_seconds", 24 * 3600)
    _update_interval_seconds: int = app_config.get("update_interval_seconds", 3600)
    _data_fetch_func: Callable[[], pd.DataFrame] = None
    _lock: Lock = Lock()
    _config = None
    
    
    def __new__(cls, config = None, data_fetch_func: 'Callable[[], pd.DataFrame]' = None):
        if cls._instance is None:
            cls._instance = super(AShareTickerCache, cls).__new__(cls)
            cls._instance._config = config
            cls._instance._data_fetch_func = data_fetch_func
            redis_port: int = cls._instance._config.get("redis.port", 6379)
            redis_host: str = cls._instance._config.get("redis.host", "localhost")
            redis_db: int = cls._instance._config.get("redis.db", 0)
            redis_password: str | None = cls._instance._config.get("redis.password", None)

            cls._instance._redis_key = cls._instance._config.get("ticker_data.redis_key", "ashare_tickers_df")
            cls._instance._redis_ttl_seconds = cls._instance._config.get("ticker_data.redis_ttl_seconds", 24 * 3600)
            cls._instance._update_interval_seconds = cls._instance._config.get("ticker_data.update_interval_seconds", 3600)
            
            try:
                cls._instance._redis_client = redis.StrictRedis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    password=redis_password,
                    decode_responses=True
                )
                cls._instance._redis_client.ping()
                logger.info(f"Successfully connected to Redis at {redis_host}:{redis_port}/{redis_db}")
            except redis.exceptions.ConnectionError as e:
                logger.error(f"Could not connect to Redis: {e}. Ticker cache will operate in memory only(not persistent)")
                cls._instance._redis_client = None
            
            if cls._instance._data_fetch_func is None:
                raise ValueError("data_fetch_func must be provided to AShareTickerRedisCache.")
            
            cls._instance._init_cache()
            cls._instance._start_auto_updater()
        return cls._instance

    def _init_cache(self) -> None:
        """Try to load data from Redis, otherwise from url
        """
        if self._redis_client:
            self._load_from_redis()
        
        is_stale: bool = (self._tickers_df.empty or
                    self._last_fetched_local_time is None or
                    (time.time() - self._last_fetched_local_time > self._redis_ttl_seconds))
        redis_key_exists: bool = False
        if self._redis_client:
            redis_key_exists = self._redis_client.exists(self._redis_key)
            if not redis_key_exists:
                is_stale = False
        if self._tickers_df.empty or is_stale:
            logger.info("Ticker cache is empty, stale, or Redis key expired/missing. Attempting to fetch from source.")
            self.update_tickers_from_source(force_update=True)
        else:
            logger.info("Ticker cache is fresh from Redis or recently fetched.")
        
    def _load_from_redis(self) -> None:
        """从 Redis 加载股票代码 DataFrame"""
        if not self._redis_client:
            return

        with self._lock:
            try:
                json_str: Union[str, None] = self._redis_client.get(self._redis_key)
                if json_str:
                    data: list = json.loads(json_str)
                    self._tickers_df = pd.DataFrame(data)
                    self._last_fetched_local_time = time.time()
                    logger.info(f"Loaded {len(self._tickers_df)} A-share tickers from Redis.")
                else:
                    self._tickers_df = pd.DataFrame()
                    self._last_fetched_local_time = None
                    logger.info(f"Redis key '{self._redis_key}' not found or empty.")
            except (json.JSONDecodeError, redis.exceptions.RedisError) as e:
                logger.error(f"Error loading ticker data from Redis: {e}")
                self._tickers_df = pd.DataFrame()
                self._last_fetched_local_time = None
        
    def update_tickers_from_source(self, force_update: bool = False) -> None:
        """
        从外部数据源获取最新数据，更新到 Redis 和内存缓存。
        """
        if not force_update and (self._last_fetched_local_time is not None and
                                 (time.time() - self._last_fetched_local_time < self._redis_ttl_seconds)):
            logger.info("Local ticker cache is fresh and within Redis TTL, skipping forced update.")
            return
        
        logger.info("Attempting to update tickers from external source and push to Redis...")
        try:
            new_df: pd.DataFrame = self._data_fetch_func()
            
            if new_df is not None and not new_df.empty:
                if not self._tickers_df.empty and set(new_df['ticker']) == set(self._tickers_df.get('ticker', [])):
                    logger.info("Ticker data from source is identical to current local cache. No Redis/local update needed.")
                else:
                    self._save_to_redis(new_df)
                    logger.info("Ticker data successfully updated from source, pushed to Redis and local cache.")
            else:
                logger.warning("Data fetch function returned empty or invalid DataFrame. Cannot update Redis/local cache.")
        except Exception as e:
            logger.error(f"Error updating tickers from source: {e}")
    
    def _save_to_redis(self, df: pd.DataFrame) -> None:
        """将DataFrame保存到redis中"""
        if not self._redis_client or df.empty:
            logger.warning("No Redis client or DataFrame is empty. Skipping save to Redis.")
            return

        with self._lock:
            try:
                data_to_save: list[dict] = df.to_dict(orient='records')
                json_str: str = json.dumps(data_to_save, ensure_ascii=True)
                self._redis_client.setex(self._redis_key, self._redis_ttl_seconds, json_str)
                self._tickers_df = df
                self._last_fetched_local_time = time.time()
                logger.info(f"Saved {len(self._tickers_df)} A-share tickers to Redis with TTL {self._redis_ttl_seconds}s.")
            except redis.exceptions.RedisError as e:
                logger.error(f"Error saving ticker data to Redis: {e}")
    
    def _start_auto_updater(self) -> None:
        """启动后台线程自动更新"""
        t = Timer(self._update_interval_seconds, self._check_for_updates_background)
        t.daemon = True
        t.start()
    
    def _check_for_updates_background(self):
        """
        后台定时检查 Redis 缓存是否过期或需要刷新。
        判断依据是本地缓存的加载时间是否超过了配置的检查间隔，
        或者 Redis 中的 Key 是否已经过期。
        """
        is_local_cache_stale: bool = (self._last_fetched_local_time is None or
                                      (time.time() - self._last_fetched_local_time) > self._update_interval_seconds)
        redis_key_exists: bool = False
        if self._redis_client:
            redis_key_exists = self._redis_client.exists(self._redis_key)

        if is_local_cache_stale or not redis_key_exists:
            logger.info("Ticker cache detected as stale (local or Redis). Attempting to refresh from source.")
            self.update_tickers_from_source(force_update=True) # 强制从源更新
        else:
            logger.debug("Ticker cache is fresh in Redis and local memory. No update needed.")
            
        self._start_auto_updater()

    def get_tickers_df(self) -> pd.DataFrame:
        """返回当前内存中的股票代码 DataFrame"""
        return self._tickers_df.copy() # 返回副本，防止外部直接修改缓存数据

ashare_cache = AShareTickerCache(app_config, get_all_a_share_tickers)
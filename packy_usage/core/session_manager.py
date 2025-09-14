"""
HTTP 会话管理器
提供高性能的连接池和会话复用
"""

import asyncio
import threading
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

import aiohttp
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..utils.logger import get_logger

logger = get_logger(__name__)


class SessionManager:
    """
    单例模式的 HTTP 会话管理器
    提供同步和异步两种会话管理
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._sync_session: Optional[requests.Session] = None
        self._async_session: Optional[aiohttp.ClientSession] = None
        self._session_lock = threading.Lock()
        self._async_lock = asyncio.Lock()
        
        # 连接池配置
        self.pool_connections = 10
        self.pool_maxsize = 10
        self.max_retries = 3
        self.timeout = 10
        
        # 缓存配置
        self._cache: Dict[str, tuple] = {}
        self._cache_ttl = timedelta(seconds=30)
        
        logger.info("SessionManager 初始化完成")
    
    def get_sync_session(self) -> requests.Session:
        """
        获取同步 HTTP 会话（线程安全）
        使用连接池和重试机制
        """
        with self._session_lock:
            if self._sync_session is None:
                logger.info("创建新的同步 HTTP 会话")
                
                # 创建会话
                self._sync_session = requests.Session()
                
                # 配置重试策略
                retry_strategy = Retry(
                    total=self.max_retries,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504],
                    allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
                )
                
                # 配置连接池适配器
                adapter = HTTPAdapter(
                    pool_connections=self.pool_connections,
                    pool_maxsize=self.pool_maxsize,
                    max_retries=retry_strategy
                )
                
                # 挂载适配器
                self._sync_session.mount("http://", adapter)
                self._sync_session.mount("https://", adapter)
                
                # 设置默认请求头
                self._sync_session.headers.update({
                    'User-Agent': 'Packy-Usage-Monitor/1.0.0',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Connection': 'keep-alive',  # 保持连接
                    'Keep-Alive': 'timeout=5, max=100'  # Keep-Alive 设置
                })
                
                logger.debug(f"同步会话配置: 连接池={self.pool_connections}, "
                           f"最大连接={self.pool_maxsize}, 重试={self.max_retries}")
            
            return self._sync_session
    
    async def get_async_session(self) -> aiohttp.ClientSession:
        """
        获取异步 HTTP 会话（协程安全）
        使用连接池和持久连接
        """
        if self._async_session is None or self._async_session.closed:
            async with self._async_lock:
                if self._async_session is None or self._async_session.closed:
                    logger.info("创建新的异步 HTTP 会话")
                    
                    # 配置连接器
                    connector = aiohttp.TCPConnector(
                        limit=100,  # 总连接数限制
                        limit_per_host=30,  # 每个主机的连接数限制
                        ttl_dns_cache=300,  # DNS 缓存时间
                        enable_cleanup_closed=True,  # 自动清理关闭的连接
                        keepalive_timeout=30,  # Keep-Alive 超时
                        force_close=False  # 不强制关闭连接
                    )
                    
                    # 配置超时
                    timeout = aiohttp.ClientTimeout(
                        total=self.timeout,
                        connect=5,
                        sock_read=5
                    )
                    
                    # 创建会话
                    self._async_session = aiohttp.ClientSession(
                        connector=connector,
                        timeout=timeout,
                        headers={
                            'User-Agent': 'Packy-Usage-Monitor/1.0.0',
                            'Accept': 'application/json',
                            'Content-Type': 'application/json',
                            'Connection': 'keep-alive'
                        }
                    )
                    
                    logger.debug("异步会话创建完成，启用连接池和持久连接")
        
        return self._async_session
    
    def get_cached_data(self, cache_key: str) -> Optional[Any]:
        """
        从缓存获取数据
        
        Args:
            cache_key: 缓存键
            
        Returns:
            缓存的数据，如果存在且未过期；否则返回 None
        """
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if datetime.now() - timestamp < self._cache_ttl:
                logger.debug(f"缓存命中: {cache_key}")
                return data
            else:
                # 清理过期缓存
                del self._cache[cache_key]
                logger.debug(f"缓存过期: {cache_key}")
        
        return None
    
    def set_cached_data(self, cache_key: str, data: Any):
        """
        设置缓存数据
        
        Args:
            cache_key: 缓存键
            data: 要缓存的数据
        """
        self._cache[cache_key] = (data, datetime.now())
        logger.debug(f"缓存设置: {cache_key}")
        
        # 清理过旧的缓存（保持缓存大小）
        self._cleanup_cache()
    
    def _cleanup_cache(self):
        """清理过期的缓存项"""
        now = datetime.now()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if now - timestamp >= self._cache_ttl
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.debug(f"清理了 {len(expired_keys)} 个过期缓存项")
    
    def clear_cache(self):
        """清空所有缓存"""
        self._cache.clear()
        logger.info("缓存已清空")
    
    def close_sync_session(self):
        """关闭同步会话"""
        if self._sync_session:
            self._sync_session.close()
            self._sync_session = None
            logger.info("同步会话已关闭")
    
    async def close_async_session(self):
        """关闭异步会话"""
        if self._async_session and not self._async_session.closed:
            await self._async_session.close()
            self._async_session = None
            logger.info("异步会话已关闭")
    
    def __del__(self):
        """析构函数，确保会话被正确关闭"""
        try:
            self.close_sync_session()
            # 异步会话需要在事件循环中关闭
            if self._async_session and not self._async_session.closed:
                asyncio.create_task(self.close_async_session())
        except:
            pass
    
    @classmethod
    def get_instance(cls) -> 'SessionManager':
        """获取单例实例"""
        return cls()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取会话管理器统计信息
        
        Returns:
            包含连接池状态的字典
        """
        stats = {
            'sync_session_active': self._sync_session is not None,
            'async_session_active': self._async_session is not None and not self._async_session.closed,
            'cache_size': len(self._cache),
            'cache_ttl_seconds': self._cache_ttl.total_seconds(),
            'pool_connections': self.pool_connections,
            'pool_maxsize': self.pool_maxsize
        }
        
        # 如果异步会话存在，获取连接器信息
        if self._async_session and not self._async_session.closed:
            connector = self._async_session.connector
            if connector:
                stats['async_connections'] = len(connector._conns) if hasattr(connector, '_conns') else 0
        
        return stats
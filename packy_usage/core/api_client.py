"""
API 客户端
负责与 Packy Code API 进行通信
使用连接池和缓存优化性能
"""

import asyncio
import aiohttp
import requests
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import hashlib
import json
import time

from .budget_data import BudgetData
from .session_manager import SessionManager
from ..config.manager import ConfigManager
from ..security.token_manager import TokenManager
from ..utils.exceptions import ApiError, NetworkError, AuthError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ApiClient:
    """API 客户端 - 使用连接池和缓存优化"""
    
    def __init__(self, config: ConfigManager, token_manager: TokenManager):
        self.config = config
        self.token_manager = token_manager
        self.session_manager = SessionManager.get_instance()
        self._last_request_time = 0
        self._min_request_interval = 1  # 最小请求间隔（秒）
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        # 使用 SessionManager 管理会话
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        # SessionManager 会自动管理会话生命周期
        pass
    
    def _get_cache_key(self, token: str) -> str:
        """生成缓存键"""
        # 使用 token 的哈希值作为缓存键的一部分
        token_hash = hashlib.md5(token.encode()).hexdigest()[:8]
        endpoint = self.config.get_api_endpoint()
        endpoint_hash = hashlib.md5(endpoint.encode()).hexdigest()[:8]
        return f"budget_data_{endpoint_hash}_{token_hash}"
    
    def _sync_fetch_budget_data(self) -> Optional[BudgetData]:
        """同步版本的预算数据获取（使用连接池和缓存）"""
        try:
            token = self.token_manager.get_token()
            if not token:
                logger.warning("未找到API Token")
                return None
            
            # 检查缓存
            cache_key = self._get_cache_key(token)
            cached_data = self.session_manager.get_cached_data(cache_key)
            if cached_data:
                logger.info("使用缓存的预算数据")
                return cached_data
            
            # 限制请求频率
            current_time = time.time()
            time_since_last = current_time - self._last_request_time
            if time_since_last < self._min_request_interval:
                time.sleep(self._min_request_interval - time_since_last)
            
            endpoint = self.config.get_api_endpoint()
            
            # 使用连接池的会话
            session = self.session_manager.get_sync_session()
            
            # 设置请求头
            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            # 配置代理
            proxies = {}
            proxy_url = self.config.get_proxy_url()
            if proxy_url:
                proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
            
            logger.debug(f"发送API请求: {endpoint}")
            
            # 发送请求（使用持久连接）
            response = session.get(
                endpoint,
                headers=headers,
                proxies=proxies,
                timeout=self.session_manager.timeout,
                verify=True  # 强制SSL证书验证
            )
            
            # 更新最后请求时间
            self._last_request_time = time.time()
            
            if response.status_code == 401 or response.status_code == 403:
                # 认证失败，清理可能过期的Token和缓存
                self.token_manager.delete_token()
                self.session_manager.clear_cache()
                error_text = response.text
                logger.error(f"认证失败 ({response.status_code}): {error_text}")
                raise AuthError(f"认证失败 ({response.status_code}): {error_text}")
            
            if not response.ok:
                error_text = response.text
                logger.error(f"API请求失败 ({response.status_code}): {error_text}")
                logger.debug(f"请求URL: {endpoint}")
                logger.debug(f"请求头: {headers}")
                raise ApiError(f"API请求失败 ({response.status_code}): {error_text}")
            
            # 解析响应
            try:
                data = response.json()
            except ValueError as e:
                logger.error(f"JSON解析失败: {e}, 响应内容: {response.text[:500]}")
                raise ApiError(f"服务器响应格式错误: {e}")
            
            budget_data = BudgetData.from_api_response(data)
            
            # 缓存数据
            self.session_manager.set_cached_data(cache_key, budget_data)
            
            logger.info(f"成功获取预算数据: 日使用率={budget_data.daily.percentage:.1f}%, "
                       f"月使用率={budget_data.monthly.percentage:.1f}%")
            
            # 输出连接统计信息（调试用）
            stats = self.session_manager.get_stats()
            logger.debug(f"连接池状态: {stats}")
            
            return budget_data
            
        except requests.exceptions.Timeout:
            raise NetworkError("请求超时")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"网络连接失败: {e}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"网络请求异常: {e}")
        except Exception as e:
            logger.error(f"获取预算数据时发生未知错误: {e}")
            raise ApiError(f"未知错误: {e}")
    
    async def fetch_budget_data(self) -> Optional[BudgetData]:
        """异步获取预算数据（使用连接池和缓存）"""
        try:
            token = self.token_manager.get_token()
            if not token:
                logger.warning("未找到API Token")
                return None
            
            # 检查缓存
            cache_key = self._get_cache_key(token)
            cached_data = self.session_manager.get_cached_data(cache_key)
            if cached_data:
                logger.info("使用缓存的预算数据")
                return cached_data
            
            # 限制请求频率
            current_time = time.time()
            time_since_last = current_time - self._last_request_time
            if time_since_last < self._min_request_interval:
                await asyncio.sleep(self._min_request_interval - time_since_last)
            
            # 获取会话（使用连接池）
            session = await self.session_manager.get_async_session()
            
            endpoint = self.config.get_api_endpoint()
            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            # 配置代理
            proxy = None
            proxy_url = self.config.get_proxy_url()
            if proxy_url:
                proxy = proxy_url
            
            logger.debug(f"发送异步API请求: {endpoint}")
            
            async with session.get(
                endpoint,
                headers=headers,
                proxy=proxy,
                ssl=True  # 强制SSL
            ) as response:
                
                # 更新最后请求时间
                self._last_request_time = time.time()
                
                if response.status in (401, 403):
                    # 认证失败，清理可能过期的Token和缓存
                    self.token_manager.delete_token()
                    self.session_manager.clear_cache()
                    raise AuthError(f"认证失败 ({response.status})")
                
                if response.status != 200:
                    text = await response.text()
                    raise ApiError(f"API请求失败 ({response.status}): {text}")
                
                # 解析响应
                data = await response.json()
                budget_data = BudgetData.from_api_response(data)
                
                # 缓存数据
                self.session_manager.set_cached_data(cache_key, budget_data)
                
                logger.info(f"成功获取预算数据: 日使用率={budget_data.daily.percentage:.1f}%, "
                           f"月使用率={budget_data.monthly.percentage:.1f}%")
                
                # 输出连接统计信息（调试用）
                stats = self.session_manager.get_stats()
                logger.debug(f"连接池状态: {stats}")
                
                return budget_data
        
        except aiohttp.ClientTimeout:
            raise NetworkError("请求超时")
        except aiohttp.ClientConnectionError as e:
            raise NetworkError(f"网络连接失败: {e}")
        except aiohttp.ClientError as e:
            raise NetworkError(f"网络请求异常: {e}")
        except Exception as e:
            logger.error(f"获取预算数据时发生未知错误: {e}")
            raise ApiError(f"未知错误: {e}")
    
    def fetch_budget_data_sync(self) -> Optional[BudgetData]:
        """同步获取预算数据（便于在非异步代码中使用）"""
        return self._sync_fetch_budget_data()
    
    def clear_cache(self):
        """清空缓存"""
        self.session_manager.clear_cache()
        logger.info("预算数据缓存已清空")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """获取连接统计信息"""
        return self.session_manager.get_stats()
    
    async def test_connection(self) -> bool:
        """测试API连接"""
        try:
            data = await self.fetch_budget_data()
            return data is not None
        except Exception as e:
            logger.error(f"连接测试失败: {e}")
            return False
    
    def test_connection_sync(self) -> bool:
        """同步测试API连接"""
        try:
            data = self.fetch_budget_data_sync()
            return data is not None
        except Exception as e:
            logger.error(f"连接测试失败: {e}")
            return False
    
    def invalidate_cache(self):
        """使缓存失效（强制下次请求获取新数据）"""
        self.session_manager.clear_cache()
        logger.info("缓存已失效，下次请求将获取新数据")
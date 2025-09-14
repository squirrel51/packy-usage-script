"""
性能优化工具集
包含图标缓存、线程池管理和批量更新机制
"""

import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional, Callable, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import weakref

from PIL import Image, ImageDraw, ImageFont
import io

from ..utils.logger import get_logger

logger = get_logger(__name__)


class IconCache:
    """
    图标缓存管理器
    避免重复创建图标，提高渲染性能
    """
    
    def __init__(self, max_cache_size: int = 100):
        self._cache: Dict[str, Image.Image] = {}
        self._access_times: Dict[str, datetime] = {}
        self._max_cache_size = max_cache_size
        self._lock = threading.Lock()
        self._cache_ttl = timedelta(minutes=10)  # 缓存10分钟
        
        logger.info(f"IconCache 初始化: 最大缓存={max_cache_size}, TTL={self._cache_ttl}")
    
    def get_icon(self, status: str, percentage: float, 
                 creator_func: Optional[Callable] = None) -> Image.Image:
        """
        获取缓存的图标，如果不存在则创建
        
        Args:
            status: 状态标识
            percentage: 百分比（四舍五入到整数）
            creator_func: 图标创建函数
            
        Returns:
            缓存的或新创建的图标
        """
        # 生成缓存键（精度降低到整数百分比）
        cache_key = f"{status}_{int(percentage)}"
        
        with self._lock:
            # 检查缓存
            if cache_key in self._cache:
                # 更新访问时间
                self._access_times[cache_key] = datetime.now()
                logger.debug(f"图标缓存命中: {cache_key}")
                return self._cache[cache_key]
            
            # 创建新图标
            if creator_func:
                icon = creator_func(status, percentage)
            else:
                icon = self._create_default_icon(status, percentage)
            
            # 添加到缓存
            self._add_to_cache(cache_key, icon)
            
            return icon
    
    def _create_default_icon(self, status: str, percentage: float) -> Image.Image:
        """创建默认图标"""
        size = (32, 32)
        image = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # 状态颜色映射
        colors = {
            "normal": "#00AA00",
            "warning": "#FFAA00",
            "critical": "#FF0000",
            "error": "#AA0000",
            "init": "#808080"
        }
        
        color = colors.get(status, "#808080")
        
        # 绘制圆形背景
        draw.ellipse([2, 2, 30, 30], fill=color, outline=color)
        
        # 绘制百分比文字
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
        
        text = f"{int(percentage)}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
        draw.text(position, text, fill="white", font=font)
        
        return image
    
    def _add_to_cache(self, key: str, icon: Image.Image):
        """添加图标到缓存"""
        # 如果缓存已满，清理最旧的项
        if len(self._cache) >= self._max_cache_size:
            self._cleanup_cache()
        
        self._cache[key] = icon
        self._access_times[key] = datetime.now()
        logger.debug(f"图标添加到缓存: {key}, 当前缓存大小: {len(self._cache)}")
    
    def _cleanup_cache(self):
        """清理缓存（LRU + TTL）"""
        now = datetime.now()
        
        # 清理过期的缓存
        expired_keys = [
            key for key, access_time in self._access_times.items()
            if now - access_time > self._cache_ttl
        ]
        
        for key in expired_keys:
            del self._cache[key]
            del self._access_times[key]
            logger.debug(f"清理过期图标缓存: {key}")
        
        # 如果还是超过限制，删除最少使用的
        if len(self._cache) >= self._max_cache_size:
            # 按访问时间排序，删除最旧的
            sorted_keys = sorted(self._access_times.items(), key=lambda x: x[1])
            keys_to_remove = [k for k, _ in sorted_keys[:len(self._cache) // 4]]
            
            for key in keys_to_remove:
                del self._cache[key]
                del self._access_times[key]
                logger.debug(f"清理LRU图标缓存: {key}")
    
    def clear(self):
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
            logger.info("图标缓存已清空")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            'cache_size': len(self._cache),
            'max_size': self._max_cache_size,
            'ttl_minutes': self._cache_ttl.total_seconds() / 60,
            'oldest_access': min(self._access_times.values()) if self._access_times else None
        }


class ManagedThreadPool:
    """
    托管的线程池
    提供更好的线程管理和监控
    """
    
    def __init__(self, max_workers: int = 4, thread_name_prefix: str = "Worker"):
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix=thread_name_prefix
        )
        self._futures = weakref.WeakSet()
        self._lock = threading.Lock()
        self._shutdown = False
        
        logger.info(f"ManagedThreadPool 初始化: 最大工作线程={max_workers}")
    
    def submit(self, fn: Callable, *args, **kwargs):
        """提交任务到线程池"""
        if self._shutdown:
            raise RuntimeError("线程池已关闭")
        
        future = self.executor.submit(fn, *args, **kwargs)
        
        with self._lock:
            self._futures.add(future)
        
        # 添加完成回调以清理引用
        future.add_done_callback(self._cleanup_future)
        
        return future
    
    def _cleanup_future(self, future):
        """清理完成的 future"""
        try:
            # 获取结果或异常（避免未处理的异常）
            future.result(timeout=0)
        except Exception as e:
            logger.error(f"线程池任务异常: {e}")
    
    def map(self, fn: Callable, *iterables, timeout=None):
        """并行映射函数到可迭代对象"""
        return self.executor.map(fn, *iterables, timeout=timeout)
    
    def shutdown(self, wait: bool = True):
        """关闭线程池"""
        with self._lock:
            self._shutdown = True
        
        self.executor.shutdown(wait=wait)
        logger.info("线程池已关闭")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取线程池统计信息"""
        active_count = sum(1 for f in self._futures if not f.done())
        completed_count = sum(1 for f in self._futures if f.done())
        
        return {
            'active_tasks': active_count,
            'completed_tasks': completed_count,
            'total_tasks': len(self._futures),
            'is_shutdown': self._shutdown
        }


class BatchUpdateManager:
    """
    批量更新管理器
    合并频繁的更新请求，减少UI刷新频率
    """
    
    def __init__(self, batch_interval: float = 0.5, max_batch_size: int = 10):
        self._queue = queue.Queue()
        self._batch_interval = batch_interval
        self._max_batch_size = max_batch_size
        self._processor_thread = None
        self._running = False
        self._update_callback = None
        self._lock = threading.Lock()
        self._last_update_time = 0
        self._pending_updates = []
        
        logger.info(f"BatchUpdateManager 初始化: 批处理间隔={batch_interval}秒, "
                   f"最大批次={max_batch_size}")
    
    def start(self, update_callback: Callable):
        """启动批处理器"""
        with self._lock:
            if self._running:
                return
            
            self._update_callback = update_callback
            self._running = True
            self._processor_thread = threading.Thread(
                target=self._process_loop,
                daemon=True,
                name="BatchUpdateProcessor"
            )
            self._processor_thread.start()
            
            logger.info("批量更新管理器已启动")
    
    def stop(self):
        """停止批处理器"""
        with self._lock:
            self._running = False
        
        if self._processor_thread:
            # 发送停止信号
            self._queue.put(None)
            self._processor_thread.join(timeout=2)
            
        logger.info("批量更新管理器已停止")
    
    def add_update(self, data: Any):
        """添加更新到队列"""
        if not self._running:
            logger.warning("批量更新管理器未运行，忽略更新")
            return
        
        try:
            self._queue.put(data, block=False)
            logger.debug(f"添加更新到批处理队列，当前队列大小: {self._queue.qsize()}")
        except queue.Full:
            logger.warning("批处理队列已满，丢弃更新")
    
    def _process_loop(self):
        """批处理循环"""
        while self._running:
            batch = []
            deadline = time.time() + self._batch_interval
            
            # 收集批次
            while time.time() < deadline and len(batch) < self._max_batch_size:
                try:
                    timeout = deadline - time.time()
                    if timeout > 0:
                        item = self._queue.get(timeout=timeout)
                        if item is None:  # 停止信号
                            break
                        batch.append(item)
                except queue.Empty:
                    break
            
            # 处理批次
            if batch and self._update_callback:
                try:
                    # 只处理最新的数据（去重）
                    if len(batch) > 1:
                        # 保留最新的更新
                        latest_data = batch[-1]
                        logger.debug(f"批处理合并 {len(batch)} 个更新为 1 个")
                    else:
                        latest_data = batch[0]
                    
                    # 执行回调
                    self._update_callback(latest_data)
                    
                except Exception as e:
                    logger.error(f"批处理更新失败: {e}")
    
    def flush(self):
        """立即处理所有待处理的更新"""
        batch = []
        
        # 收集所有待处理项
        while not self._queue.empty():
            try:
                item = self._queue.get_nowait()
                if item is not None:
                    batch.append(item)
            except queue.Empty:
                break
        
        # 处理批次
        if batch and self._update_callback:
            try:
                latest_data = batch[-1]
                self._update_callback(latest_data)
                logger.debug(f"强制刷新 {len(batch)} 个更新")
            except Exception as e:
                logger.error(f"强制刷新失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'queue_size': self._queue.qsize(),
            'batch_interval': self._batch_interval,
            'max_batch_size': self._max_batch_size,
            'is_running': self._running
        }


class PerformanceOptimizer:
    """
    性能优化器
    整合所有优化功能
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
        
        # 初始化各个优化组件
        self.icon_cache = IconCache(max_cache_size=50)
        self.thread_pool = ManagedThreadPool(max_workers=3)
        self.batch_manager = BatchUpdateManager(
            batch_interval=0.5,
            max_batch_size=5
        )
        
        logger.info("PerformanceOptimizer 初始化完成")
    
    @classmethod
    def get_instance(cls) -> 'PerformanceOptimizer':
        """获取单例实例"""
        return cls()
    
    def shutdown(self):
        """关闭所有优化组件"""
        self.batch_manager.stop()
        self.thread_pool.shutdown()
        self.icon_cache.clear()
        logger.info("PerformanceOptimizer 已关闭")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取所有组件的统计信息"""
        return {
            'icon_cache': self.icon_cache.get_stats(),
            'thread_pool': self.thread_pool.get_stats(),
            'batch_manager': self.batch_manager.get_stats()
        }
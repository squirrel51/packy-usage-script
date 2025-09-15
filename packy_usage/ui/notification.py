"""
通知管理器
提供跨平台的桌面通知功能
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Set, Optional

from plyer import notification

from ..config.manager import ConfigManager, NotificationConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)


class NotificationManager:
    """通知管理器"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.notification_config = config.get_notification_config()
        
        # 通知去重，防止重复通知
        self.recent_notifications: Dict[str, datetime] = {}
        self.notification_cooldown = timedelta(minutes=5)  # 5分钟冷却时间
        
        # 静默时间检查
        self.quiet_hours_active = False
    
    def send_info(self, title: str, message: str, timeout: int = 5):
        """发送信息通知"""
        self._send_notification(title, message, "info", timeout)
    
    def send_warning_alert(self, title: str, message: str, timeout: int = 10):
        """发送警告通知"""
        self._send_notification(title, message, "warning", timeout)
    
    def send_critical_alert(self, title: str, message: str, timeout: int = 15):
        """发送严重警告通知"""
        self._send_notification(title, message, "critical", timeout)
    
    def send_error(self, title: str, message: str, timeout: int = 10):
        """发送错误通知"""
        self._send_notification(title, message, "error", timeout)
    
    def _send_notification(
        self, 
        title: str, 
        message: str, 
        level: str = "info", 
        timeout: int = 5
    ):
        """
        发送通知的内部方法
        
        Args:
            title: 通知标题
            message: 通知消息
            level: 通知级别 (info, warning, critical, error)
            timeout: 显示时间（秒）
        """
        try:
            # 检查通知是否启用
            if not self.notification_config.enabled:
                logger.debug(f"通知已禁用，跳过: {title}")
                return
            
            # 检查免打扰时间
            if self._is_in_quiet_hours() and level not in ["critical", "error"]:
                logger.debug(f"处于免打扰时间，跳过非紧急通知: {title}")
                return
            
            # 检查通知去重
            if self._is_duplicate_notification(title, level):
                logger.debug(f"重复通知，跳过: {title}")
                return
            
            # 准备通知内容
            app_name = "Packy Usage Monitor"
            full_title = f"[{level.upper()}] {title}" if level != "info" else title
            
            # 选择图标
            app_icon = self._get_notification_icon(level)
            
            # 发送通知
            notification.notify(
                title=full_title,
                message=message,
                app_name=app_name,
                app_icon=app_icon,
                timeout=timeout,
                ticker="Packy Usage Monitor"  # Android ticker text
            )
            
            # 记录通知历史
            self._record_notification(title, level)
            
            logger.info(f"已发送{level}通知: {title}")
            
        except Exception as e:
            error_msg = str(e)

            # 将常见的英文错误消息转换为中文
            if "No usable implementation found" in error_msg:
                error_msg = "通知系统不可用 (缺少必要的系统组件)"
            elif "No module named 'plyer.platforms'" in error_msg:
                error_msg = "通知库模块缺失 (plyer.platforms)"
            elif "Permission denied" in error_msg:
                error_msg = "通知权限被拒绝"
            elif "timeout" in error_msg.lower():
                error_msg = "通知发送超时"
            else:
                error_msg = f"通知系统错误: {error_msg}"

            logger.error(f"发送通知失败: {error_msg}")
            # 通知失败不应该影响程序运行，所以不抛出异常
    
    def _is_in_quiet_hours(self) -> bool:
        """检查是否在免打扰时间内"""
        try:
            now = datetime.now().time()
            
            start_str = self.notification_config.quiet_hours_start
            end_str = self.notification_config.quiet_hours_end
            
            # 解析时间字符串
            start_time = datetime.strptime(start_str, "%H:%M").time()
            end_time = datetime.strptime(end_str, "%H:%M").time()
            
            # 处理跨天情况（如22:00-08:00）
            if start_time <= end_time:
                # 同一天内的时间段
                return start_time <= now <= end_time
            else:
                # 跨天的时间段
                return now >= start_time or now <= end_time
                
        except Exception as e:
            logger.debug(f"解析免打扰时间失败: {e}")
            return False
    
    def _is_duplicate_notification(self, title: str, level: str) -> bool:
        """检查是否为重复通知"""
        key = f"{level}:{title}"
        now = datetime.now()
        
        if key in self.recent_notifications:
            last_sent = self.recent_notifications[key]
            if now - last_sent < self.notification_cooldown:
                return True
        
        return False
    
    def _record_notification(self, title: str, level: str):
        """记录通知历史"""
        key = f"{level}:{title}"
        self.recent_notifications[key] = datetime.now()
        
        # 清理过期记录
        cutoff_time = datetime.now() - self.notification_cooldown
        self.recent_notifications = {
            k: v for k, v in self.recent_notifications.items()
            if v > cutoff_time
        }
    
    def _get_notification_icon(self, level: str) -> Optional[str]:
        """获取通知图标路径"""
        # 这里可以返回自定义图标路径
        # 如果没有自定义图标，plyer会使用系统默认图标
        return None
    
    def test_notification(self):
        """测试通知功能"""
        try:
            self.send_info(
                "通知测试",
                "这是一条来自 Packy 使用监视器的测试通知。如果您能看到这条消息，说明通知功能运行正常！"
            )
            return True
        except Exception as e:
            logger.error(f"通知测试失败: {e}")
            return False
    
    def set_quiet_mode(self, enabled: bool):
        """设置静默模式"""
        self.config.update_config("notification", {"enabled": not enabled})
        self.notification_config = self.config.get_notification_config()
        
        if enabled:
            logger.info("已启用静默模式")
        else:
            logger.info("已禁用静默模式")
    
    def is_enabled(self) -> bool:
        """检查通知是否启用"""
        return self.notification_config.enabled
    
    def get_stats(self) -> Dict[str, int]:
        """获取通知统计信息"""
        now = datetime.now()
        cutoff_time = now - timedelta(hours=1)  # 最近1小时的统计
        
        recent_count = sum(
            1 for timestamp in self.recent_notifications.values()
            if timestamp > cutoff_time
        )
        
        return {
            "recent_notifications": recent_count,
            "quiet_hours_active": self._is_in_quiet_hours(),
            "notifications_enabled": self.notification_config.enabled
        }
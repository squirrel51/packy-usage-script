"""
配置管理器
负责管理应用的所有配置项
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ApiConfig:
    """API相关配置"""
    endpoint: str = "https://www.packycode.com/api/backend/users/info"
    timeout: int = 10
    retry_count: int = 3
    
    
@dataclass 
class PollingConfig:
    """轮询相关配置"""
    enabled: bool = True
    interval: int = 30  # 秒
    retry_on_failure: int = 3
    

@dataclass
class DisplayConfig:
    """显示相关配置"""
    decimal_places: int = 2
    currency_symbol: str = "$"
    show_percentage: bool = True
    show_amounts: bool = True
    

@dataclass
class AlertConfig:
    """警报相关配置"""
    daily_warning: float = 75.0      # 75%时警告
    daily_critical: float = 90.0     # 90%时严重警告
    monthly_warning: float = 80.0    # 80%时警告
    monthly_critical: float = 95.0   # 95%时严重警告
    

@dataclass
class NotificationConfig:
    """通知相关配置"""
    enabled: bool = True
    quiet_hours_start: str = "22:00"  # 免打扰开始时间
    quiet_hours_end: str = "08:00"    # 免打扰结束时间
    channels: list = None             # 通知渠道列表
    
    def __post_init__(self):
        if self.channels is None:
            self.channels = ["desktop"]


@dataclass
class NetworkConfig:
    """网络相关配置"""
    proxy: str = ""  # HTTP代理地址
    verify_ssl: bool = True
    user_agent: str = "Packy-Usage-Monitor/1.0.0"


@dataclass
class LoggingConfig:
    """日志相关配置"""
    level: str = "INFO"
    file: str = ""  # 默认为空，表示不记录到文件
    max_size: str = "10MB"
    backup_count: int = 5


class ConfigManager:
    """配置管理器"""
    
    _config_dir: Optional[Path] = None
    
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.yaml"
        self.config_data = self._load_config()
    
    @classmethod
    def set_config_dir(cls, config_dir: Path):
        """设置配置目录"""
        cls._config_dir = config_dir
    
    def _get_config_dir(self) -> Path:
        """获取配置目录"""
        if self._config_dir:
            return self._config_dir
        
        # 优先使用环境变量
        if env_dir := os.environ.get('PACKY_USAGE_CONFIG_DIR'):
            return Path(env_dir)
        
        # 默认使用用户主目录下的 .packy-usage
        config_dir = Path.home() / ".packy-usage"
        config_dir.mkdir(exist_ok=True)
        return config_dir
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "api": asdict(ApiConfig()),
            "polling": asdict(PollingConfig()),
            "display": asdict(DisplayConfig()),
            "alerts": asdict(AlertConfig()),
            "notification": asdict(NotificationConfig()),
            "network": asdict(NetworkConfig()),
            "logging": asdict(LoggingConfig())
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f) or {}
                
                # 合并默认配置和用户配置
                default_config = self._get_default_config()
                merged_config = self._deep_merge(default_config, user_config)
                
                logger.info(f"已加载配置文件: {self.config_file}")
                return merged_config
            else:
                # 首次运行，创建默认配置文件
                default_config = self._get_default_config()
                self._save_config(default_config)
                logger.info(f"已创建默认配置文件: {self.config_file}")
                return default_config
                
        except Exception as e:
            logger.error(f"加载配置失败，使用默认配置: {e}")
            return self._get_default_config()
    
    def _deep_merge(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并配置字典"""
        merged = default.copy()
        
        for key, value in user.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._deep_merge(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def _save_config(self, config: Dict[str, Any]):
        """保存配置"""
        try:
            self.config_dir.mkdir(exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(
                    config, 
                    f, 
                    default_flow_style=False, 
                    allow_unicode=True,
                    indent=2
                )
            
            logger.info(f"配置已保存: {self.config_file}")
            
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            raise
    
    def get_api_config(self) -> ApiConfig:
        """获取API配置"""
        return ApiConfig(**self.config_data["api"])
    
    def get_polling_config(self) -> PollingConfig:
        """获取轮询配置"""
        return PollingConfig(**self.config_data["polling"])
    
    def get_display_config(self) -> DisplayConfig:
        """获取显示配置"""
        return DisplayConfig(**self.config_data["display"])
    
    def get_alert_config(self) -> AlertConfig:
        """获取警报配置"""
        return AlertConfig(**self.config_data["alerts"])
    
    def get_notification_config(self) -> NotificationConfig:
        """获取通知配置"""
        return NotificationConfig(**self.config_data["notification"])
    
    def get_network_config(self) -> NetworkConfig:
        """获取网络配置"""
        return NetworkConfig(**self.config_data["network"])
    
    def get_logging_config(self) -> LoggingConfig:
        """获取日志配置"""
        return LoggingConfig(**self.config_data["logging"])
    
    # 便捷方法
    def get_api_endpoint(self) -> str:
        """获取API端点"""
        return self.get_api_config().endpoint
    
    def get_polling_interval(self) -> int:
        """获取轮询间隔"""
        return self.get_polling_config().interval
    
    def is_polling_enabled(self) -> bool:
        """是否启用轮询"""
        return self.get_polling_config().enabled
    
    def get_proxy_url(self) -> Optional[str]:
        """获取代理URL"""
        proxy = self.get_network_config().proxy
        if not proxy:
            # 尝试从环境变量获取
            return os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY')
        return proxy if proxy.strip() else None
    
    def update_config(self, section: str, updates: Dict[str, Any]):
        """更新配置"""
        if section in self.config_data:
            self.config_data[section].update(updates)
            self._save_config(self.config_data)
            logger.info(f"已更新配置节 '{section}': {updates}")
        else:
            raise ValueError(f"未知配置节: {section}")
    
    def reset_to_defaults(self):
        """重置为默认配置"""
        default_config = self._get_default_config()
        self._save_config(default_config)
        self.config_data = default_config
        logger.info("配置已重置为默认值")
    
    def show_config(self):
        """显示当前配置"""
        print("📋 当前配置:")
        print(f"  配置文件: {self.config_file}")
        print()
        
        api_config = self.get_api_config()
        print("🔗 API配置:")
        print(f"  端点: {api_config.endpoint}")
        print(f"  超时: {api_config.timeout}秒")
        print()
        
        polling_config = self.get_polling_config()
        print("🔄 轮询配置:")
        print(f"  启用: {polling_config.enabled}")
        print(f"  间隔: {polling_config.interval}秒")
        print()
        
        alert_config = self.get_alert_config()
        print("⚠️  警报配置:")
        print(f"  日预算警告阈值: {alert_config.daily_warning}%")
        print(f"  日预算严重阈值: {alert_config.daily_critical}%")
        print(f"  月预算警告阈值: {alert_config.monthly_warning}%")
        print(f"  月预算严重阈值: {alert_config.monthly_critical}%")
        print()
        
        network_config = self.get_network_config()
        proxy_url = self.get_proxy_url()
        print("🌐 网络配置:")
        print(f"  代理: {proxy_url if proxy_url else '未设置'}")
        print(f"  SSL验证: {network_config.verify_ssl}")
        print()
    
    @property
    def config_directory(self) -> Path:
        """配置目录路径"""
        return self.config_dir
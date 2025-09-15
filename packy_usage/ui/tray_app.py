"""
系统托盘应用
提供类似VS Code状态栏的体验
集成性能优化：图标缓存、线程池、批量更新
"""

import threading
import time
import os
import sys
from typing import Optional, Callable
from pathlib import Path

import pystray
from pystray import MenuItem, Menu
from PIL import Image, ImageDraw, ImageFont

from ..core.budget_data import BudgetData
from ..core.api_client import ApiClient
from ..core.performance import PerformanceOptimizer
from ..config.manager import ConfigManager
from ..security.token_manager import TokenManager
from ..ui.notification import NotificationManager
from ..utils.logger import get_logger
from ..utils.exceptions import UIError

logger = get_logger(__name__)


class TrayApp:
    """系统托盘应用 - 集成性能优化"""
    
    def __init__(self, config: ConfigManager, token_manager: TokenManager, api_client: ApiClient):
        self.config = config
        self.token_manager = token_manager
        self.api_client = api_client
        self.notification_manager = NotificationManager(config)
        
        # 性能优化器
        self.optimizer = PerformanceOptimizer.get_instance()
        
        self.icon: Optional[pystray.Icon] = None
        self.current_data: Optional[BudgetData] = None
        self.polling_thread: Optional[threading.Thread] = None
        self.running = False
        
        # 创建托盘图标
        self._create_tray_icon()
        
        # 启动批量更新管理器
        self.optimizer.batch_manager.start(self._batch_update_handler)
    
    def run(self):
        """启动托盘应用"""
        try:
            if not self.token_manager.is_token_available():
                self._show_no_token_icon()
                logger.warning("未找到有效Token，托盘应用以受限模式启动")
            
            self.running = True
            
            # 启动数据轮询线程
            if self.config.is_polling_enabled():
                self._start_polling()
            
            # 初始数据获取
            self._update_data()
            
            # 运行托盘图标
            self.icon.run()
            
        except Exception as e:
            logger.error(f"托盘应用运行失败: {e}")
            raise UIError(f"托盘应用启动失败: {e}")
    
    def stop(self):
        """停止托盘应用"""
        logger.info("正在停止托盘应用...")
        self.running = False

        try:
            # 停止轮询线程（更短的超时时间）
            if self.polling_thread and self.polling_thread.is_alive():
                logger.debug("正在停止轮询线程...")
                self.polling_thread.join(timeout=1)  # 减少超时时间
                if self.polling_thread.is_alive():
                    logger.warning("轮询线程停止超时，将被强制终止")

            # 停止批量更新管理器
            try:
                logger.debug("正在停止批量更新管理器...")
                self.optimizer.batch_manager.stop()
            except Exception as e:
                logger.warning(f"停止批量更新管理器失败: {e}")

            # 关闭性能优化器
            try:
                logger.debug("正在关闭性能优化器...")
                self.optimizer.shutdown()
            except Exception as e:
                logger.warning(f"关闭性能优化器失败: {e}")

            # 停止托盘图标（最后执行，最短超时）
            if self.icon:
                logger.debug("正在停止托盘图标...")
                try:
                    self.icon.stop()
                except Exception as e:
                    logger.warning(f"停止托盘图标失败: {e}")

        except Exception as e:
            logger.error(f"停止托盘应用时出现错误: {e}")

        logger.info("托盘应用清理完成")
    
    def _create_tray_icon(self):
        """创建托盘图标"""
        # 创建初始图标
        image = self._create_icon_image("init")
        
        # 创建托盘菜单
        menu = self._create_menu()
        
        # 创建托盘图标
        self.icon = pystray.Icon(
            "packy-usage",
            image,
            "Packy 使用监视器 - 初始化中...",
            menu
        )
    
    def _create_menu(self) -> Menu:
        """创建右键菜单"""
        return Menu(
            MenuItem("📊 显示详情", self._show_details, default=True),
            MenuItem("🔄 刷新数据", self._refresh_data),
            Menu.SEPARATOR,
            MenuItem("⚙️ 设置", Menu(
                MenuItem("🔑 设置 Token", self._configure_token),
                MenuItem("📋 显示配置", self._show_config),
                Menu.SEPARATOR,
                MenuItem("🔄 启用轮询", self._toggle_polling, checked=self._is_polling_enabled),
                MenuItem("🔇 静音模式", self._toggle_quiet_mode, checked=self._is_quiet_mode),
            )),
            Menu.SEPARATOR,
            MenuItem("ℹ️ 关于", self._show_about),
            MenuItem("❌ 退出", self._exit_app),
            MenuItem("⚡ 强制退出", self._force_exit)
        )
    
    def _create_icon_image(self, status: str = "normal", percentage: float = 0) -> Image.Image:
        """
        创建托盘图标图像（使用缓存优化）
        
        Args:
            status: 状态 (init, normal, warning, critical, error, no_token)
            percentage: 使用百分比（用于显示数字）
        """
        # 使用图标缓存
        return self.optimizer.icon_cache.get_icon(
            status, percentage, 
            lambda s, p: self._create_icon_internal(s, p)
        )
    
    def _create_icon_internal(self, status: str, percentage: float) -> Image.Image:
        """内部图标创建函数"""
        # 图标尺寸 
        size = (32, 32)
        
        # 创建图像
        image = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # 状态颜色映射
        colors = {
            "init": "#808080",      # 灰色
            "normal": "#00AA00",    # 绿色
            "warning": "#FFAA00",   # 黄色
            "critical": "#FF0000",  # 红色
            "error": "#AA0000",     # 深红色
            "no_token": "#404040"   # 深灰色
        }
        
        color = colors.get(status, colors["normal"])
        
        if status == "no_token":
            # 显示钥匙图标
            self._draw_key_icon(draw, size, color)
        elif status == "error":
            # 显示错误图标
            self._draw_error_icon(draw, size, color)
        elif status == "init":
            # 显示初始化图标
            self._draw_loading_icon(draw, size, color)
        else:
            # 显示圆形图标
            self._draw_circle_icon(draw, size, color)
            
            # 如果有百分比数据，显示数字
            if percentage > 0 and percentage <= 99:
                self._draw_percentage_text(draw, size, f"{int(percentage)}")
        
        return image
    
    def _draw_circle_icon(self, draw: ImageDraw.Draw, size: tuple, color: str):
        """绘制圆形图标"""
        margin = 4
        draw.ellipse([margin, margin, size[0] - margin, size[1] - margin], fill=color)
    
    def _draw_key_icon(self, draw: ImageDraw.Draw, size: tuple, color: str):
        """绘制钥匙图标（表示需要Token）"""
        # 简化的钥匙形状
        w, h = size
        cx, cy = w // 2, h // 2
        
        # 钥匙圆形部分
        r = 8
        draw.ellipse([cx - r, cy - r - 4, cx + r, cy + r - 4], outline=color, width=3)
        
        # 钥匙柄部分
        draw.rectangle([cx, cy + 2, cx + 10, cy + 6], fill=color)
        draw.rectangle([cx + 6, cy + 6, cx + 10, cy + 10], fill=color)
    
    def _draw_error_icon(self, draw: ImageDraw.Draw, size: tuple, color: str):
        """绘制错误图标"""
        w, h = size
        cx, cy = w // 2, h // 2
        
        # X形状
        margin = 8
        draw.line([margin, margin, w - margin, h - margin], fill=color, width=4)
        draw.line([w - margin, margin, margin, h - margin], fill=color, width=4)
    
    def _draw_loading_icon(self, draw: ImageDraw.Draw, size: tuple, color: str):
        """绘制加载图标"""
        w, h = size
        cx, cy = w // 2, h // 2
        
        # 简单的点图标
        r = 4
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    
    def _draw_percentage_text(self, draw: ImageDraw.Draw, size: tuple, text: str):
        """在图标上绘制百分比文字"""
        try:
            # 尝试使用系统字体，如果失败则跳过文字
            font_size = 10
            try:
                # Windows/Linux
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    # macOS
                    font = ImageFont.truetype("Helvetica.ttc", font_size)
                except:
                    # 使用默认字体
                    font = ImageFont.load_default()
            
            # 计算文字位置
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            
            x = (size[0] - text_w) // 2
            y = (size[1] - text_h) // 2
            
            # 绘制文字（白色，带黑色描边）
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                draw.text((x + dx, y + dy), text, font=font, fill="black")
            draw.text((x, y), text, font=font, fill="white")
            
        except Exception as e:
            logger.debug(f"绘制百分比文字失败: {e}")
    
    def _start_polling(self):
        """启动轮询线程（使用线程池）"""
        if self.polling_thread and self.polling_thread.is_alive():
            return
        
        # 使用线程池提交轮询任务
        future = self.optimizer.thread_pool.submit(self._polling_loop)
        logger.info("已启动数据轮询（使用线程池）")
    
    def _polling_loop(self):
        """轮询循环"""
        interval = self.config.get_polling_interval()
        
        while self.running:
            try:
                time.sleep(interval)
                if not self.running:
                    break
                
                self._update_data()
                
            except Exception as e:
                logger.error(f"轮询过程中发生错误: {e}")
                time.sleep(min(interval, 60))  # 错误时等待时间不超过60秒
    
    def _update_data(self):
        """更新预算数据（使用批量更新）"""
        try:
            # 检查Token
            if not self.token_manager.is_token_available():
                self._show_no_token_icon()
                return
            
            # 获取数据（已经有缓存优化）
            data = self.api_client.fetch_budget_data_sync()
            
            if data:
                # 添加到批量更新队列
                self.optimizer.batch_manager.add_update(data)
                logger.debug(f"数据更新已添加到批处理队列")
            else:
                self._show_error_icon("获取数据失败")
                
        except Exception as e:
            logger.error(f"更新数据失败: {e}")
            self._show_error_icon(f"错误: {e}")
    
    def _batch_update_handler(self, data: BudgetData):
        """批量更新处理器"""
        try:
            self.current_data = data
            self._update_icon_with_data(data)
            
            # 检查是否需要发送通知
            self._check_and_send_notification(data)
            
            logger.debug(f"批量更新完成: 日使用率={data.daily.percentage:.1f}%")
        except Exception as e:
            logger.error(f"批量更新处理失败: {e}")
    
    def _update_icon_with_data(self, data: BudgetData):
        """根据数据更新图标"""
        max_percentage = data.max_usage_percentage
        
        # 确定状态
        if max_percentage >= 90:
            status = "critical"
        elif max_percentage >= 75:
            status = "warning"
        else:
            status = "normal"
        
        # 更新图标
        self.icon.icon = self._create_icon_image(status, max_percentage)
        
        # 更新工具提示
        tooltip = self._create_tooltip(data)
        self.icon.title = tooltip
    
    def _create_tooltip(self, data: BudgetData) -> str:
        """创建工具提示文本"""
        daily = data.daily
        monthly = data.monthly
        
        tooltip_parts = [
            "Packy 使用监视器",
            "",
            f"日预算: {daily.percentage:.1f}% (${daily.used:.2f}/${daily.total:.2f})",
            f"月预算: {monthly.percentage:.1f}% (${monthly.used:.2f}/${monthly.total:.2f})",
        ]
        
        if data.overall_status in ["warning", "critical"]:
            tooltip_parts.append("")
            tooltip_parts.append(f"⚠️ 状态: {data.overall_status.title()}")
        
        if data.last_updated:
            update_time = data.last_updated.strftime("%H:%M:%S")
            tooltip_parts.append(f"更新时间: {update_time}")
        
        return "\n".join(tooltip_parts)
    
    def _show_no_token_icon(self):
        """显示无Token状态"""
        self.icon.icon = self._create_icon_image("no_token")
        self.icon.title = "Packy 使用监视器 - 需要 Token\n右键点击进行配置"
    
    def _show_error_icon(self, message: str):
        """显示错误状态"""
        self.icon.icon = self._create_icon_image("error")
        self.icon.title = f"Packy 使用监视器 - {message}\n右键点击刷新"
    
    def _check_and_send_notification(self, data: BudgetData):
        """检查并发送通知"""
        alert_config = self.config.get_alert_config()
        
        # 检查日预算
        if data.daily.percentage >= alert_config.daily_critical:
            self.notification_manager.send_critical_alert(
                "日预算严重警告",
                f"日预算使用量已达到 {data.daily.percentage:.1f}% (${data.daily.used:.2f}/${data.daily.total:.2f})"
            )
        elif data.daily.percentage >= alert_config.daily_warning:
            self.notification_manager.send_warning_alert(
                "日预算警告",
                f"日预算使用量为 {data.daily.percentage:.1f}% (${data.daily.used:.2f}/${data.daily.total:.2f})"
            )
        
        # 检查月预算
        if data.monthly.percentage >= alert_config.monthly_critical:
            self.notification_manager.send_critical_alert(
                "月预算严重警告",
                f"月预算使用量已达到 {data.monthly.percentage:.1f}% (${data.monthly.used:.2f}/${data.monthly.total:.2f})"
            )
        elif data.monthly.percentage >= alert_config.monthly_warning:
            self.notification_manager.send_warning_alert(
                "月预算警告",
                f"月预算使用量为 {data.monthly.percentage:.1f}% (${data.monthly.used:.2f}/${data.monthly.total:.2f})"
            )
    
    # 菜单事件处理器
    def _show_details(self, icon, item):
        """显示详细信息"""
        if self.current_data:
            self._show_details_window()
        else:
            self.notification_manager.send_info("没有数据", "暂无预算数据。请点击刷新获取数据。")
    
    def _show_details_window(self):
        """显示详细信息窗口（使用通知代替）"""
        if not self.current_data:
            return
        
        data = self.current_data
        message = f"""日预算: {data.daily.percentage:.1f}% (${data.daily.used:.2f}/${data.daily.total:.2f})
月预算: {data.monthly.percentage:.1f}% (${data.monthly.used:.2f}/${data.monthly.total:.2f})
状态: {data.overall_status.title()}"""
        
        self.notification_manager.send_info("预算详情", message)
    
    def _refresh_data(self, icon, item):
        """刷新数据（使用线程池）"""
        # 清空缓存以获取最新数据
        self.api_client.clear_cache()
        
        # 使用线程池提交更新任务
        self.optimizer.thread_pool.submit(self._update_data)
        self.notification_manager.send_info("刷新", "正在刷新预算数据...")
    
    def _configure_token(self, icon, item):
        """配置Token（打开配置提示）"""
        message = """配置 API Token:

1. API Token（推荐）:
   - 从 PackyCode 仪表板获取永久 API Token（以 'sk-' 开头）

2. JWT Token:
   - 访问 PackyCode 仪表板
   - 打开浏览器开发者工具 (F12)
   - 转到 Application > Cookies
   - 复制 'token' cookie 值

运行: packy_usage.py config set-token"""
        
        self.notification_manager.send_info("配置 Token", message)
    
    def _show_config(self, icon, item):
        """显示配置"""
        config = self.config.get_api_config()
        polling = self.config.get_polling_config()
        
        message = f"""配置信息:
API 端点: {config.endpoint}
轮询: {'已启用' if polling.enabled else '已禁用'} ({polling.interval}秒)
Token: {'已配置' if self.token_manager.is_token_available() else '未设置'}"""
        
        self.notification_manager.send_info("配置信息", message)
    
    def _toggle_polling(self, icon, item):
        """切换轮询状态"""
        current = self.config.is_polling_enabled()
        self.config.update_config("polling", {"enabled": not current})
        
        if not current:
            self._start_polling()
            self.notification_manager.send_info("轮询", "轮询已启用")
        else:
            self.notification_manager.send_info("轮询", "轮询已禁用")
    
    def _toggle_quiet_mode(self, icon, item):
        """切换静默模式"""
        current = self.config.get_notification_config().enabled
        self.config.update_config("notification", {"enabled": not current})
        self.notification_manager.send_info(
            "通知",
            "已禁用" if current else "已启用"
        )
    
    def _show_about(self, icon, item):
        """显示关于信息"""
        from .. import __version__
        message = f"""Packy 使用监视器 v{__version__}

一个独立的 Packy Code API 预算监控工具。

功能特性:
• 实时预算监控
• 系统托盘集成
• 智能通知
• 命令行界面

访问: https://github.com/packycode/packy-usage-monitor"""
        
        self.notification_manager.send_info("关于", message)
    
    def _exit_app(self, icon, item):
        """退出应用"""
        def force_exit():
            """强制退出函数"""
            try:
                logger.info("用户请求退出应用")

                # 立即设置停止标志
                self.running = False

                # 尝试正常停止
                self.stop()

                # 给一点时间让清理完成
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"退出应用时出现错误: {e}")
            finally:
                # 强制退出
                logger.info("强制退出应用")
                os._exit(0)

        # 在新线程中执行退出，避免阻塞GUI线程
        exit_thread = threading.Thread(target=force_exit, daemon=True)
        exit_thread.start()

    def _force_exit(self, icon, item):
        """强制退出应用（无清理）"""
        logger.warning("用户请求强制退出应用")
        os._exit(0)
    
    # 菜单状态检查器
    def _is_polling_enabled(self, item):
        """检查轮询是否启用"""
        return self.config.is_polling_enabled()
    
    def _is_quiet_mode(self, item):
        """检查是否为静默模式"""
        return not self.config.get_notification_config().enabled
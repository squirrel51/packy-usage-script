"""
命令行显示工具
提供各种格式的预算数据展示
"""

import json
import time
import asyncio
from typing import Optional
from datetime import datetime

import click

from ..core.budget_data import BudgetData, BudgetUsage
from ..core.api_client import ApiClient
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CliDisplay:
    """命令行显示工具"""
    
    def __init__(self):
        self.last_update = None
    
    def show_budget_data(
        self, 
        data: BudgetData, 
        brief: bool = False, 
        output_json: bool = False,
        alert_only: bool = False
    ):
        """
        显示预算数据
        
        Args:
            data: 预算数据
            brief: 简要显示模式
            output_json: JSON格式输出
            alert_only: 仅显示警告状态
        """
        if output_json:
            self._show_json_format(data)
            return
        
        if alert_only:
            self._show_alerts_only(data)
            return
        
        if brief:
            self._show_brief_format(data)
        else:
            self._show_detailed_format(data)
    
    def _show_json_format(self, data: BudgetData):
        """JSON格式显示"""
        click.echo(json.dumps(data.to_dict(), indent=2, ensure_ascii=False))
    
    def _show_brief_format(self, data: BudgetData):
        """简要格式显示"""
        daily_icon = data.daily.status_icon
        monthly_icon = data.monthly.status_icon
        
        click.echo(f"{daily_icon} 日预算: {data.daily.percentage:.1f}% | "
                  f"{monthly_icon} 月预算: {data.monthly.percentage:.1f}%")
    
    def _show_detailed_format(self, data: BudgetData):
        """详细格式显示"""
        # 标题
        click.echo("==== " + click.style("Packy 预算使用报告", bold=True, fg='blue') + " ====")
        click.echo("=" * 50)
        
        # 整体状态
        status_colors = {
            "normal": "green",
            "notice": "blue", 
            "warning": "yellow",
            "critical": "red"
        }
        
        status_texts = {
            "normal": "正常",
            "notice": "注意",
            "warning": "警告",
            "critical": "危险"
        }
        
        status_color = status_colors.get(data.overall_status, "white")
        status_text = status_texts.get(data.overall_status, data.overall_status)
        click.echo(f"整体状态: {data.status_icon} " + 
                  click.style(status_text, fg=status_color, bold=True))
        click.echo()
        
        # 日预算信息
        self._show_usage_section("[日预算]", data.daily)
        click.echo()
        
        # 月预算信息
        self._show_usage_section("[月预算]", data.monthly)
        
        # 更新时间
        if data.last_updated:
            update_time = data.last_updated.strftime("%Y-%m-%d %H:%M:%S")
            click.echo(f"\n[更新时间] {update_time}")
    
    def _show_usage_section(self, title: str, usage: BudgetUsage):
        """显示使用情况节"""
        click.echo(click.style(title, bold=True))
        
        # 进度条
        progress_bar = self._create_progress_bar(usage.percentage)
        click.echo(f"  {progress_bar} {usage.percentage:.1f}%")
        
        # 金额信息
        click.echo(f"  已使用:     ${usage.used:.2f}")
        click.echo(f"  总额度:     ${usage.total:.2f}")
        click.echo(f"  剩余额度:   ${usage.remaining:.2f}")
        
        # 状态
        status_msg = self._get_status_message(usage)
        if status_msg:
            click.echo(f"  状态:       {status_msg}")
    
    def _show_alerts_only(self, data: BudgetData):
        """仅显示警告状态"""
        alerts = []
        
        if data.daily.is_critical:
            alerts.append(f"[危险] 日预算危险: {data.daily.percentage:.1f}%")
        elif data.daily.is_warning:
            alerts.append(f"[警告] 日预算警告: {data.daily.percentage:.1f}%")
        
        if data.monthly.is_critical:
            alerts.append(f"[危险] 月预算危险: {data.monthly.percentage:.1f}%")
        elif data.monthly.is_warning:
            alerts.append(f"[警告] 月预算警告: {data.monthly.percentage:.1f}%")
        
        if alerts:
            for alert in alerts:
                click.echo(alert)
        else:
            click.echo("[OK] 所有预算使用均在正常范围内")
    
    def _create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """创建进度条"""
        filled = int(percentage / 100 * width)
        # 使用ASCII字符避免编码问题
        bar = "#" * filled + "-" * (width - filled)
        
        # 根据使用率设置颜色
        if percentage >= 90:
            return click.style(bar, fg='red')
        elif percentage >= 75:
            return click.style(bar, fg='yellow')
        elif percentage >= 50:
            return click.style(bar, fg='blue')
        else:
            return click.style(bar, fg='green')
    
    def _get_status_message(self, usage: BudgetUsage) -> str:
        """获取状态消息"""
        if usage.is_critical:
            return click.style("[!] 危险 - 接近限额！", fg='red', bold=True)
        elif usage.is_warning:
            return click.style("[!] 警告 - 使用率较高", fg='yellow')
        elif usage.percentage >= 50:
            return click.style("[i] 中等使用", fg='blue')
        else:
            return click.style("[OK] 正常使用", fg='green')
    
    def watch_mode(self, api_client: ApiClient, interval: int = 30):
        """
        实时监控模式
        
        Args:
            api_client: API客户端
            interval: 刷新间隔（秒）
        """
        click.echo(f">> 监控预算使用情况 (每 {interval} 秒刷新)")
        click.echo("按 Ctrl+C 停止监控\n")
        
        try:
            while True:
                # 清屏（仅在非首次更新时）
                if self.last_update:
                    click.clear()
                
                # 获取数据
                try:
                    data = api_client.fetch_budget_data_sync()
                    if data:
                        self._show_watch_display(data, interval)
                        self.last_update = datetime.now()
                    else:
                        click.echo("[X] 无法获取预算数据")
                
                except Exception as e:
                    click.echo(f"[X] 错误: {e}")
                
                # 等待下次更新
                time.sleep(interval)
                
        except KeyboardInterrupt:
            pass
    
    def _show_watch_display(self, data: BudgetData, interval: int):
        """监控模式下的显示格式"""
        now = datetime.now().strftime("%H:%M:%S")

        # 标题行
        title = f"Packy 预算监控 - {now} (刷新间隔: {interval}秒)"
        click.echo("\n" + "=" * 60)
        click.echo(click.style(f"  {title}", bold=True, fg='cyan'))
        click.echo("=" * 60)

        # 紧凑的双栏显示
        daily = data.daily
        monthly = data.monthly

        # 计算对齐宽度
        click.echo()
        click.echo("  " + "日预算".center(26) + " | " + "月预算".center(26))
        click.echo("  " + "-" * 26 + "-+-" + "-" * 26)

        # 进度条
        daily_bar = self._create_progress_bar(daily.percentage, 20)
        monthly_bar = self._create_progress_bar(monthly.percentage, 20)

        click.echo(f"  {daily_bar} | {monthly_bar}")
        click.echo(f"  {daily.percentage:>6.1f}% 已使用{' ' * 14} | {monthly.percentage:>6.1f}% 已使用")
        click.echo()

        # 金额信息 - 更清晰的格式
        daily_used_str = f"${daily.used:,.2f}"
        daily_total_str = f"${daily.total:,.2f}"
        monthly_used_str = f"${monthly.used:,.2f}"
        monthly_total_str = f"${monthly.total:,.2f}"

        click.echo(f"  已使用: {daily_used_str:>10}{' ' * 8} | 已使用: {monthly_used_str:>10}")
        click.echo(f"  总额度: {daily_total_str:>10}{' ' * 8} | 总额度: {monthly_total_str:>10}")
        click.echo(f"  剩余额: ${daily.remaining:>9,.2f}{' ' * 8} | 剩余额: ${monthly.remaining:>9,.2f}")
        click.echo()

        # 状态指示 - 居中对齐
        if daily.is_critical:
            daily_status = "❌ 危险"
            daily_color = 'red'
        elif daily.is_warning:
            daily_status = "⚠️  警告"
            daily_color = 'yellow'
        else:
            daily_status = "✅ 正常"
            daily_color = 'green'

        if monthly.is_critical:
            monthly_status = "❌ 危险"
            monthly_color = 'red'
        elif monthly.is_warning:
            monthly_status = "⚠️  警告"
            monthly_color = 'yellow'
        else:
            monthly_status = "✅ 正常"
            monthly_color = 'green'

        daily_status_colored = click.style(f"状态: {daily_status}", fg=daily_color, bold=True)
        monthly_status_colored = click.style(f"状态: {monthly_status}", fg=monthly_color, bold=True)

        # 计算填充以居中
        status_line = f"  {daily_status_colored}".ljust(35) + " | " + f"{monthly_status_colored}"
        click.echo(status_line)

        # 底部分隔线
        click.echo("=" * 60)

        # 提示信息
        if data.overall_status in ["warning", "critical"]:
            if data.overall_status == "critical":
                alert_msg = "💥 危险警报：预算使用率过高，请立即注意！"
                alert_color = 'red'
            else:
                alert_msg = "⚠️  注意：预算使用率较高，请合理控制使用"
                alert_color = 'yellow'
            click.echo()
            click.echo(click.style(f"  {alert_msg}", fg=alert_color, bold=True, blink=True))
    
    def show_error(self, message: str, suggestion: Optional[str] = None):
        """显示错误信息"""
        click.echo(click.style(f"[X] {message}", fg='red'), err=True)
        if suggestion:
            click.echo(click.style(f"[!] {suggestion}", fg='yellow'), err=True)
    
    def show_success(self, message: str):
        """显示成功信息"""
        click.echo(click.style(f"[OK] {message}", fg='green'))
    
    def show_warning(self, message: str):
        """显示警告信息"""
        click.echo(click.style(f"[!] {message}", fg='yellow'))
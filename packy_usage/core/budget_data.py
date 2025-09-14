"""
预算数据模型
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class BudgetUsage:
    """预算使用情况"""
    percentage: float  # 使用百分比
    total: float      # 总预算金额
    used: float       # 已使用金额
    
    @property
    def remaining(self) -> float:
        """剩余预算"""
        return max(0, self.total - self.used)
    
    @property
    def is_warning(self) -> bool:
        """是否为警告状态 (>= 75%)"""
        return self.percentage >= 75
    
    @property
    def is_critical(self) -> bool:
        """是否为严重状态 (>= 90%)"""
        return self.percentage >= 90
    
    @property
    def status_icon(self) -> str:
        """获取状态图标"""
        if self.is_critical:
            return "🔴"  # 严重
        elif self.is_warning:
            return "🟡"  # 警告
        elif self.percentage >= 50:
            return "🔵"  # 注意
        else:
            return "🟢"  # 安全


@dataclass
class BudgetData:
    """完整预算数据"""
    daily: BudgetUsage
    monthly: BudgetUsage
    last_updated: Optional[datetime] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'BudgetData':
        """从API响应创建预算数据对象"""
        
        # 解析日预算
        daily_budget = float(data.get('daily_budget_usd', 0))
        daily_spent = float(data.get('daily_spent_usd', 0))
        daily_percentage = (daily_spent / daily_budget * 100) if daily_budget > 0 else 0
        
        # 解析月预算
        monthly_budget = float(data.get('monthly_budget_usd', 0))
        monthly_spent = float(data.get('monthly_spent_usd', 0))
        monthly_percentage = (monthly_spent / monthly_budget * 100) if monthly_budget > 0 else 0
        
        return cls(
            daily=BudgetUsage(
                percentage=daily_percentage,
                total=daily_budget,
                used=daily_spent
            ),
            monthly=BudgetUsage(
                percentage=monthly_percentage,
                total=monthly_budget,
                used=monthly_spent
            ),
            last_updated=datetime.now()
        )
    
    @property
    def max_usage_percentage(self) -> float:
        """获取最高使用率"""
        return max(self.daily.percentage, self.monthly.percentage)
    
    @property
    def overall_status(self) -> str:
        """获取整体状态"""
        max_percent = self.max_usage_percentage
        if max_percent >= 90:
            return "critical"
        elif max_percent >= 75:
            return "warning"
        elif max_percent >= 50:
            return "notice"
        else:
            return "normal"
    
    @property
    def status_icon(self) -> str:
        """获取整体状态图标"""
        status = self.overall_status
        icons = {
            "critical": "🔴",
            "warning": "🟡", 
            "notice": "🔵",
            "normal": "🟢"
        }
        return icons.get(status, "❓")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "daily": {
                "percentage": round(self.daily.percentage, 2),
                "total": round(self.daily.total, 2),
                "used": round(self.daily.used, 2),
                "remaining": round(self.daily.remaining, 2)
            },
            "monthly": {
                "percentage": round(self.monthly.percentage, 2),
                "total": round(self.monthly.total, 2),
                "used": round(self.monthly.used, 2),
                "remaining": round(self.monthly.remaining, 2)
            },
            "overall_status": self.overall_status,
            "max_usage_percentage": round(self.max_usage_percentage, 2),
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }
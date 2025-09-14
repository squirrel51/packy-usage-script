# 开发者指南

## 🏗️ 项目架构

### 总体设计

Packy Usage Monitor 采用**分层架构**设计，遵循 SOLID 原则：

```
┌─────────────────┐
│   CLI Layer     │  命令行接口层
├─────────────────┤
│    UI Layer     │  用户界面层（托盘、通知、显示）
├─────────────────┤
│  Service Layer  │  业务逻辑层（配置、安全、数据）
├─────────────────┤
│   Core Layer    │  核心功能层（API客户端、数据模型）
└─────────────────┘
```

### 模块职责

| 模块 | 职责 | 主要类 |
|------|------|-------|
| `cli/` | 命令行界面 | `commands.py` |
| `core/` | 核心功能 | `ApiClient`, `BudgetData` |
| `config/` | 配置管理 | `ConfigManager` |
| `security/` | 安全功能 | `TokenManager` |
| `ui/` | 用户界面 | `TrayApp`, `CliDisplay`, `NotificationManager` |
| `utils/` | 工具函数 | 异常类、日志工具 |

## 🔧 开发环境

### 环境搭建

```bash
# 1. 克隆项目
git clone <repository-url>
cd packy-usage-script

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装开发工具
pip install pytest black flake8 mypy pre-commit

# 5. 设置Git钩子
pre-commit install
```

### IDE 配置

**VS Code 推荐设置** (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "editor.formatOnSave": true
}
```

## 📝 编码规范

### 代码风格

- **格式化工具**: Black
- **代码检查**: Flake8  
- **类型检查**: MyPy
- **文档字符串**: Google Style

```python
def fetch_budget_data(self, timeout: int = 10) -> Optional[BudgetData]:
    """
    获取预算数据
    
    Args:
        timeout: 请求超时时间（秒）
        
    Returns:
        BudgetData: 预算数据对象，失败时返回None
        
    Raises:
        ApiError: API请求失败
        NetworkError: 网络连接失败
    """
    pass
```

### 命名规范

```python
# 类名：大驼峰
class ApiClient:
    pass

# 方法/变量名：小写下划线
def fetch_budget_data():
    pass

user_config = {}

# 常量：大写下划线
DEFAULT_TIMEOUT = 10
API_ENDPOINT = "https://api.example.com"

# 私有方法：下划线前缀
def _internal_method():
    pass
```

### 异常处理

```python
# 使用自定义异常
from ..utils.exceptions import ApiError, NetworkError

try:
    result = api_call()
except requests.RequestException as e:
    logger.error(f"API调用失败: {e}")
    raise ApiError(f"API请求失败: {e}") from e
```

## 🧪 测试

### 测试结构

```
tests/
├── __init__.py
├── conftest.py              # pytest配置
├── test_api_client.py       # API客户端测试
├── test_budget_data.py      # 数据模型测试
├── test_config_manager.py   # 配置管理测试
└── fixtures/               # 测试数据
    └── api_responses.json
```

### 编写测试

```python
# tests/test_budget_data.py

import pytest
from packy_usage.core.budget_data import BudgetData

class TestBudgetData:
    """预算数据测试"""
    
    def test_from_api_response_success(self):
        """测试从API响应成功创建数据"""
        api_data = {
            'daily_budget_usd': 10.0,
            'daily_spent_usd': 6.5,
            'monthly_budget_usd': 100.0,
            'monthly_spent_usd': 42.8
        }
        
        budget_data = BudgetData.from_api_response(api_data)
        
        assert budget_data.daily.percentage == 65.0
        assert budget_data.daily.is_warning is False
        assert budget_data.overall_status == "notice"
    
    def test_critical_status(self):
        """测试严重状态判断"""
        api_data = {
            'daily_budget_usd': 10.0,
            'daily_spent_usd': 9.5,  # 95%
            'monthly_budget_usd': 100.0,
            'monthly_spent_usd': 42.8
        }
        
        budget_data = BudgetData.from_api_response(api_data)
        
        assert budget_data.daily.is_critical is True
        assert budget_data.overall_status == "critical"

# fixtures
@pytest.fixture
def sample_api_response():
    """示例API响应数据"""
    return {
        'daily_budget_usd': 10.0,
        'daily_spent_usd': 6.5,
        'monthly_budget_usd': 100.0,
        'monthly_spent_usd': 42.8
    }
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行指定测试文件
pytest tests/test_api_client.py

# 运行指定测试方法
pytest tests/test_budget_data.py::TestBudgetData::test_critical_status

# 生成覆盖率报告
pytest --cov=packy_usage --cov-report=html
open htmlcov/index.html  # 查看覆盖率报告
```

## 🔌 扩展开发

### 添加新的CLI命令

```python
# packy_usage/cli/commands.py

@cli.command()
@click.option('--days', default=7, help='历史天数')
@click.option('--format', default='table', help='输出格式')
def history(days, format):
    """显示使用历史"""
    try:
        # 1. 获取历史数据
        history_data = get_usage_history(days)
        
        # 2. 格式化显示
        if format == 'json':
            click.echo(json.dumps(history_data, indent=2))
        else:
            display_history_table(history_data)
            
    except Exception as e:
        click.echo(f"❌ 获取历史数据失败: {e}", err=True)
        sys.exit(1)
```

### 添加新的通知渠道

```python
# packy_usage/ui/notifications/slack_notifier.py

import requests
from typing import Optional

class SlackNotifier:
    """Slack通知器"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_notification(self, title: str, message: str, level: str = "info"):
        """发送Slack通知"""
        color_map = {
            "info": "#36a64f",      # 绿色
            "warning": "#ff9500",   # 橙色  
            "critical": "#ff0000"   # 红色
        }
        
        payload = {
            "attachments": [{
                "color": color_map.get(level, "#36a64f"),
                "title": title,
                "text": message,
                "footer": "Packy Usage Monitor",
                "ts": int(time.time())
            }]
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(f"Slack通知发送失败: {e}")
            return False

# 集成到NotificationManager
# packy_usage/ui/notification.py

class NotificationManager:
    def __init__(self, config: ConfigManager):
        # ... 现有代码 ...
        
        # 初始化Slack通知器（如果配置了）
        slack_webhook = config.get_slack_webhook()
        if slack_webhook:
            self.slack_notifier = SlackNotifier(slack_webhook)
        else:
            self.slack_notifier = None
    
    def _send_notification(self, title: str, message: str, level: str = "info", timeout: int = 5):
        # ... 现有桌面通知代码 ...
        
        # 发送Slack通知
        if self.slack_notifier and "slack" in self.notification_config.channels:
            self.slack_notifier.send_notification(title, message, level)
```

### 添加配置选项

```python
# packy_usage/config/manager.py

@dataclass
class IntegrationConfig:
    """集成配置"""
    slack_webhook: str = ""
    email_smtp_server: str = ""
    email_recipient: str = ""

class ConfigManager:
    def _get_default_config(self) -> Dict[str, Any]:
        return {
            # ... 现有配置 ...
            "integrations": asdict(IntegrationConfig())
        }
    
    def get_integration_config(self) -> IntegrationConfig:
        """获取集成配置"""
        return IntegrationConfig(**self.config_data["integrations"])
    
    def get_slack_webhook(self) -> Optional[str]:
        """获取Slack Webhook URL"""
        webhook = self.get_integration_config().slack_webhook
        return webhook if webhook.strip() else None
```

### 添加数据持久化

```python
# packy_usage/storage/history_store.py

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path

class HistoryStore:
    """历史数据存储"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    daily_percentage REAL NOT NULL,
                    daily_used REAL NOT NULL,
                    daily_total REAL NOT NULL,
                    monthly_percentage REAL NOT NULL,
                    monthly_used REAL NOT NULL,
                    monthly_total REAL NOT NULL,
                    raw_data TEXT NOT NULL
                )
            """)
            
            # 创建索引
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON usage_history(timestamp)
            """)
    
    def save_usage_data(self, budget_data: BudgetData):
        """保存使用数据"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO usage_history (
                    timestamp, daily_percentage, daily_used, daily_total,
                    monthly_percentage, monthly_used, monthly_total, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                budget_data.daily.percentage,
                budget_data.daily.used,
                budget_data.daily.total,
                budget_data.monthly.percentage,
                budget_data.monthly.used,
                budget_data.monthly.total,
                json.dumps(budget_data.to_dict())
            ))
    
    def get_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取历史数据"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM usage_history 
                WHERE timestamp >= ? 
                ORDER BY timestamp DESC
            """, (cutoff_date.isoformat(),))
            
            return [dict(row) for row in cursor.fetchall()]
```

## 🚀 构建与发布

### 本地构建

```bash
# 构建所有平台
python build.py

# 构建特定平台
python build.py --platform windows

# 调试模式构建（保留控制台）
python build.py --debug
```

### CI/CD 配置

**GitHub Actions** (`.github/workflows/build.yml`):
```yaml
name: Build and Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=packy_usage --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Build executable
      run: python build.py
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: packy-usage-monitor-${{ matrix.os }}
        path: dist/
```

### 版本管理

```python
# 版本号格式：MAJOR.MINOR.PATCH
# packy_usage/__init__.py
__version__ = "1.2.0"

# 版本发布流程
# 1. 更新版本号
# 2. 更新CHANGELOG.md  
# 3. 提交并打标签
git tag v1.2.0
git push origin v1.2.0

# 4. GitHub Actions自动构建发布包
```

## 📊 性能优化

### 内存优化

```python
# 使用__slots__减少内存占用
@dataclass
class BudgetUsage:
    __slots__ = ['percentage', 'total', 'used']
    percentage: float
    total: float
    used: float

# 及时清理大对象
class ApiClient:
    async def _close_session(self):
        if self.session:
            await self.session.close()
            self.session = None
```

### 性能监控

```python
# packy_usage/utils/profiler.py

import time
import functools
from typing import Callable, Any

def profile_time(func: Callable) -> Callable:
    """性能计时装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed = time.time() - start_time
            logger.debug(f"{func.__name__} 执行时间: {elapsed:.3f}s")
    return wrapper

# 使用示例
@profile_time
def fetch_budget_data(self) -> Optional[BudgetData]:
    # 实现代码
    pass
```

## 🐛 调试技巧

### 日志调试

```python
# 开发环境启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 或修改配置文件
# ~/.packy-usage/config.yaml
logging:
  level: "DEBUG"
  file: "/tmp/packy-usage-debug.log"
```

### 单元测试调试

```python
# 运行单个测试并显示详细输出
pytest tests/test_api_client.py::test_fetch_data -v -s

# 调试失败的测试
pytest tests/test_api_client.py --pdb
```

### 托盘应用调试

```python
# 添加控制台窗口（Windows）
# 修改build.py中的console参数
exe = EXE(
    # ...
    console=True,  # 显示控制台窗口
    # ...
)
```

## 📚 参考资源

### 技术文档

- [Click框架文档](https://click.palletsprojects.com/)
- [Pystray文档](https://pystray.readthedocs.io/)
- [aiohttp文档](https://docs.aiohttp.org/)
- [Keyring文档](https://keyring.readthedocs.io/)

### 开发工具

- [Black代码格式化](https://black.readthedocs.io/)
- [Flake8代码检查](https://flake8.pycqa.org/)
- [MyPy类型检查](https://mypy.readthedocs.io/)
- [Pytest测试框架](https://pytest.org/)

### 设计模式

本项目应用的设计模式：

1. **单例模式**: ConfigManager
2. **工厂模式**: 服务实例创建
3. **观察者模式**: 数据变更通知
4. **策略模式**: 多种显示格式
5. **适配器模式**: 跨平台API封装

---

**维护者**: Packy Usage Team  
**最后更新**: 2024-01-15  

有问题或建议？欢迎提交 [GitHub Issue](https://github.com/packycode/packy-usage-monitor/issues)！
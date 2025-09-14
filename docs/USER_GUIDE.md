# Packy Usage Monitor 使用手册

## 📖 目录

- [快速开始](#快速开始)
- [安装指南](#安装指南)
- [基本使用](#基本使用)
- [配置详解](#配置详解)
- [高级功能](#高级功能)
- [故障排除](#故障排除)
- [开发指南](#开发指南)

---

## 🚀 快速开始

### 最简单的使用方式

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Token
python packy_usage.py config set-token

# 3. 启动系统托盘应用
python packy_usage.py tray
```

### 5分钟快速体验

1. **获取 API Token**
   - 访问 [PackyCode Dashboard](https://www.packycode.com)
   - 获取以 `sk-` 开头的 API Token（推荐）
   - 或从浏览器开发者工具获取 JWT Token

2. **配置并启动**
   ```bash
   python packy_usage.py config set-token
   # 输入您的 Token
   
   python packy_usage.py tray
   # 系统托盘出现预算监控图标
   ```

3. **查看效果**
   - 托盘图标显示当前预算使用状态
   - 右键菜单提供详细信息和设置
   - 超过阈值自动发送桌面通知

---

## 📦 安装指南

### 方式1：Python 源码运行（推荐开发者）

**系统要求**：
- Python 3.8+
- Windows 10+ / macOS 10.14+ / Ubuntu 18.04+

**步骤**：
```bash
# 克隆或下载项目
cd packy-usage-script

# 安装依赖
pip install -r requirements.txt

# 验证安装
python packy_usage.py --version
```

### 方式2：可执行文件（推荐最终用户）

```bash
# 构建可执行文件
python build.py

# 运行构建好的程序
cd dist
./packy-usage-monitor --help
```

**自动安装脚本**：
- **Windows**：运行 `dist/install.bat`
- **macOS/Linux**：运行 `dist/install.sh`

### 依赖说明

| 依赖包 | 版本要求 | 用途 |
|--------|----------|------|
| `requests` | ≥2.28.0 | HTTP请求 |
| `aiohttp` | ≥3.8.0 | 异步HTTP请求 |
| `pystray` | ≥0.19.4 | 系统托盘 |
| `plyer` | ≥2.1.0 | 跨平台通知 |
| `keyring` | ≥24.0.0 | 安全存储 |
| `pyyaml` | ≥6.0 | 配置文件 |
| `click` | ≥8.1.0 | 命令行界面 |
| `Pillow` | ≥9.0.0 | 图标渲染 |

---

## 🎮 基本使用

### 命令行工具模式

#### 查看预算状态

```bash
# 详细显示（默认）
python packy_usage.py status
# 输出：
# 📊 Packy Usage Report
# ==================================================
# Overall Status: 🟡 Warning
# 
# 📅 Daily Budget
#   ████████████░░░░░░░░ 65.2%
#   Used:      $6.52
#   Total:     $10.00
#   Remaining: $3.48
#   Status:    ℹ️ Moderate usage

# 简要显示
python packy_usage.py status --brief
# 输出：🟡 Daily: 65.2% | 🟢 Monthly: 42.8%

# JSON 格式（便于脚本处理）
python packy_usage.py status --json
# 输出结构化JSON数据

# 仅显示警告
python packy_usage.py status --alert-only
# 输出：🟡 Daily budget WARNING: 78.5%
```

#### 实时监控模式

```bash
# 启动实时监控（默认30秒刷新）
python packy_usage.py watch

# 自定义刷新间隔
python packy_usage.py watch --interval 10

# 输出示例：
# 🖥️ Packy Usage Monitor - 14:30:45 (refresh: 30s)
# ==================================================
# Daily Budget   │ Monthly Budget
# ───────────────┼────────────────
# ████████████░░░ 65.2% │ █████████░░░░░░ 42.8%
# $    6.52/$10.00      │ $   42.80/$100.00
# Remaining: $    3.48  │ Remaining: $   57.20
# Status: 🟡            │ Status: 🟢
```

#### CI/CD 集成

```bash
# 预算检查（适用于构建脚本）
python packy_usage.py check --threshold 85
echo $?  # 返回码：0=正常, 1=超限, 2=错误

# 在构建脚本中使用
if ! python packy_usage.py check --threshold 90; then
    echo "预算使用率过高，停止构建"
    exit 1
fi
```

### 系统托盘模式

#### 启动托盘应用

```bash
python packy_usage.py tray
```

#### 托盘功能详解

**图标状态**：
- 🟢 **绿色圆圈**：使用率 < 50%（安全）
- 🔵 **蓝色圆圈**：使用率 50-75%（正常）  
- 🟡 **黄色圆圈**：使用率 75-90%（警告）
- 🔴 **红色圆圈**：使用率 ≥ 90%（严重）
- ⚪ **灰色/钥匙图标**：未配置Token或错误状态

**鼠标悬停**：显示详细工具提示
```
Packy Usage Monitor

Daily: 65.2% ($6.52/$10.00)
Monthly: 42.8% ($42.80/$100.00)
Updated: 14:30:45
```

**右键菜单**：
- 📊 **显示详情**：弹出详细预算信息
- 🔄 **刷新**：立即更新数据
- ⚙️ **设置** → 
  - 🔑 设置Token
  - 📋 显示配置
  - 🔄 启用/禁用轮询
  - 🔇 静默模式开关
- ℹ️ **关于**：显示版本和帮助信息
- ❌ **退出**：关闭应用

---

## ⚙️ 配置详解

### Token 配置

#### 支持的 Token 类型

1. **API Token（强烈推荐）**
   ```bash
   python packy_usage.py config set-token
   # 输入以 'sk-' 开头的永久Token
   ```
   
   **获取方式**：
   - 登录 PackyCode Dashboard
   - 导航到 API 设置页面
   - 生成新的 API Token
   - 复制完整的 Token（包含 `sk-` 前缀）

2. **JWT Token（临时使用）**
   ```bash
   python packy_usage.py config set-token
   # 输入从浏览器获取的JWT Token
   ```
   
   **获取方式**：
   - 访问 PackyCode Dashboard 并登录
   - 按 F12 打开开发者工具
   - 切换到 "Application" 或 "Storage" 标签页
   - 展开 "Cookies" → 选择当前网站
   - 找到名为 "token" 的 Cookie
   - 复制其值作为 JWT Token

#### Token 管理

```bash
# 查看Token状态（不显示Token内容）
python packy_usage.py config show

# 重新设置Token
python packy_usage.py config set-token

# 测试Token有效性
python packy_usage.py status
```

### 配置文件详解

**位置**：`~/.packy-usage/config.yaml`

**完整配置示例**：

```yaml
# API 相关配置
api:
  endpoint: "https://www.packycode.com/api/backend/users/info"
  timeout: 10          # 请求超时时间（秒）
  retry_count: 3       # 失败重试次数

# 轮询配置
polling:
  enabled: true        # 是否启用自动轮询
  interval: 30         # 轮询间隔（秒），最小5秒
  retry_on_failure: 3  # 轮询失败重试次数

# 显示配置
display:
  decimal_places: 2        # 金额显示小数位数
  currency_symbol: "$"     # 货币符号
  show_percentage: true    # 显示百分比
  show_amounts: true       # 显示具体金额

# 预警阈值配置
alerts:
  daily_warning: 75.0      # 日预算警告阈值（%）
  daily_critical: 90.0     # 日预算严重阈值（%）
  monthly_warning: 80.0    # 月预算警告阈值（%）
  monthly_critical: 95.0   # 月预算严重阈值（%）

# 通知配置
notification:
  enabled: true                    # 启用通知
  quiet_hours_start: "22:00"       # 免打扰开始时间
  quiet_hours_end: "08:00"         # 免打扰结束时间
  channels: ["desktop"]            # 通知渠道

# 网络配置
network:
  proxy: ""                        # HTTP代理（空=不使用）
  verify_ssl: true                 # SSL证书验证
  user_agent: "Packy-Usage-Monitor/1.0.0"

# 日志配置
logging:
  level: "INFO"        # 日志级别：DEBUG/INFO/WARNING/ERROR
  file: ""             # 日志文件路径（空=不记录文件）
  max_size: "10MB"     # 日志文件最大大小
  backup_count: 5      # 保留日志文件数量
```

#### 配置管理命令

```bash
# 显示当前配置
python packy_usage.py config show

# 重置为默认配置
python packy_usage.py config reset
# 注意：这将清除所有自定义配置，但保留Token

# 手动编辑配置文件
# Windows: notepad %USERPROFILE%\.packy-usage\config.yaml
# macOS/Linux: nano ~/.packy-usage/config.yaml
```

---

## 🚀 高级功能

### 企业网络环境配置

#### HTTP 代理设置

**方式1：配置文件**
```yaml
# ~/.packy-usage/config.yaml
network:
  proxy: "http://proxy.company.com:8080"
  verify_ssl: true
```

**方式2：环境变量**
```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=https://proxy.company.com:8080

# Windows
set HTTP_PROXY=http://proxy.company.com:8080
set HTTPS_PROXY=https://proxy.company.com:8080
```

#### 企业防火墙

如果遇到SSL证书问题：
```yaml
network:
  verify_ssl: false  # 仅在必要时禁用
```

**注意**：禁用SSL验证会降低安全性，仅在可信网络环境中使用。

### 通知系统定制

#### 通知级别

- **信息通知**：配置变更、数据更新成功
- **警告通知**：使用率达到警告阈值（默认75%/80%）
- **严重通知**：使用率达到严重阈值（默认90%/95%）
- **错误通知**：网络失败、认证错误

#### 免打扰模式

```yaml
notification:
  enabled: true
  quiet_hours_start: "18:00"    # 自定义静默开始时间
  quiet_hours_end: "09:00"      # 自定义静默结束时间
```

**特殊规则**：
- 严重通知（≥90%）始终发送，忽略免打扰时间
- 通知去重：相同类型通知5分钟内只发送一次

#### 通知测试

```bash
# 通过托盘应用测试
# 右键托盘图标 → 设置 → 测试通知
```

### 数据导出与集成

#### JSON 格式输出

```bash
python packy_usage.py status --json | jq '.'
```

**输出结构**：
```json
{
  "daily": {
    "percentage": 65.23,
    "total": 10.00,
    "used": 6.52,
    "remaining": 3.48
  },
  "monthly": {
    "percentage": 42.80,
    "total": 100.00,
    "used": 42.80,
    "remaining": 57.20
  },
  "overall_status": "warning",
  "max_usage_percentage": 65.23,
  "last_updated": "2024-01-15T14:30:45.123456"
}
```

#### 脚本集成示例

**Bash 脚本**：
```bash
#!/bin/bash
# 预算监控脚本

USAGE=$(python packy_usage.py status --json | jq -r '.max_usage_percentage')

if (( $(echo "$USAGE > 85" | bc -l) )); then
    echo "⚠️ 预算使用率过高: ${USAGE}%"
    # 发送邮件通知、Slack消息等
    exit 1
else
    echo "✅ 预算使用正常: ${USAGE}%"
    exit 0
fi
```

**Python 脚本**：
```python
import subprocess
import json

def get_budget_status():
    result = subprocess.run([
        'python', 'packy_usage.py', 'status', '--json'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        raise Exception(f"获取预算数据失败: {result.stderr}")

# 使用示例
data = get_budget_status()
if data['max_usage_percentage'] > 85:
    print(f"预算警告: {data['max_usage_percentage']:.1f}%")
```

### 性能优化

#### 轮询间隔优化

```yaml
polling:
  enabled: true
  interval: 60  # 降低频率，减少API调用
```

**建议设置**：
- **开发环境**：30-60秒
- **生产监控**：60-120秒
- **低频检查**：300秒（5分钟）

#### 资源使用监控

```bash
# 查看进程资源使用
# Windows
tasklist | findstr packy-usage-monitor

# macOS/Linux
ps aux | grep packy_usage
```

---

## 🐛 故障排除

### 常见问题

#### 1. Token 相关问题

**问题**: `❌ 认证失败 (401): Unauthorized`

**排查步骤**:
```bash
# 1. 检查Token状态
python packy_usage.py config show

# 2. 重新设置Token
python packy_usage.py config set-token

# 3. 测试Token有效性
python packy_usage.py status
```

**可能原因**:
- Token已过期（JWT Token）
- Token格式错误
- API密钥已被撤销

#### 2. 网络连接问题

**问题**: `❌ 网络连接失败`

**排查步骤**:
```bash
# 1. 测试网络连接
ping www.packycode.com

# 2. 检查代理设置
python packy_usage.py config show

# 3. 测试直接连接（禁用代理）
unset HTTP_PROXY HTTPS_PROXY
python packy_usage.py status
```

**解决方案**:
- 配置正确的HTTP代理
- 检查防火墙设置
- 联系网络管理员开放访问权限

#### 3. 系统托盘问题

**问题**: 托盘图标不显示

**Linux 解决方案**:
```bash
# Ubuntu/Debian
sudo apt-get install gir1.2-appindicator3-0.1

# CentOS/RHEL
sudo yum install libappindicator-gtk3
```

**macOS 解决方案**:
- 检查"系统偏好设置" → "安全性与隐私" → "辅助功能"
- 允许应用访问系统托盘

**Windows 解决方案**:
- 检查Windows版本（需要Windows 10+）
- 重启应用程序

#### 4. 通知问题

**问题**: 桌面通知不显示

**排查步骤**:
```bash
# 1. 检查通知配置
python packy_usage.py config show

# 2. 测试通知功能
# 通过托盘应用右键菜单 → 设置 → 测试通知
```

**解决方案**:
- 检查系统通知权限设置
- 确认通知服务正在运行
- 临时禁用免打扰模式测试

#### 5. 配置文件问题

**问题**: `❌ 配置加载失败`

**解决方案**:
```bash
# 1. 备份现有配置
cp ~/.packy-usage/config.yaml ~/.packy-usage/config.yaml.bak

# 2. 重置为默认配置
python packy_usage.py config reset

# 3. 重新配置Token
python packy_usage.py config set-token
```

### 日志调试

#### 启用调试日志

**临时启用**:
```bash
# 修改配置文件
# ~/.packy-usage/config.yaml
logging:
  level: "DEBUG"
  file: "~/.packy-usage/debug.log"
```

**查看日志**:
```bash
# 实时查看日志
tail -f ~/.packy-usage/debug.log

# Windows
type %USERPROFILE%\.packy-usage\debug.log
```

#### 常见日志消息

```
INFO - 已启动数据轮询线程
INFO - 成功获取预算数据: 日使用率=65.2%, 月使用率=42.8%
WARNING - Token已过期，自动清理
ERROR - 网络连接失败: Connection timeout
DEBUG - 配置已加载: /home/user/.packy-usage/config.yaml
```

### 技术支持

如果问题依然存在：

1. **收集诊断信息**:
   ```bash
   python packy_usage.py --version
   python packy_usage.py config show
   # 提供操作系统版本、Python版本
   ```

2. **GitHub Issues**: [提交问题报告](https://github.com/packycode/packy-usage-monitor/issues)

3. **社区支持**: [PackyCode 用户论坛](https://community.packycode.com)

---

## 🛠️ 开发指南

### 开发环境搭建

```bash
# 1. 克隆仓库
git clone https://github.com/your-org/packy-usage-monitor.git
cd packy-usage-monitor

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装开发依赖
pip install -r requirements.txt

# 4. 安装开发工具
pip install pytest black flake8 mypy

# 5. 运行测试
pytest
```

### 项目结构

```
packy-usage-script/
├── packy_usage.py              # 主入口文件
├── requirements.txt            # 生产依赖
├── build.py                   # 构建脚本
├── config.example.yaml        # 配置模板
├── docs/                      # 文档目录
│   └── USER_GUIDE.md         # 本使用手册
└── packy_usage/              # 主要代码包
    ├── __init__.py           # 包初始化
    ├── cli/                  # 命令行界面
    │   ├── __init__.py
    │   └── commands.py       # CLI命令实现
    ├── core/                 # 核心功能
    │   ├── __init__.py
    │   ├── api_client.py     # API客户端
    │   └── budget_data.py    # 数据模型
    ├── config/               # 配置管理
    │   ├── __init__.py
    │   └── manager.py        # 配置管理器
    ├── security/             # 安全功能
    │   ├── __init__.py
    │   └── token_manager.py  # Token管理
    ├── ui/                   # 用户界面
    │   ├── __init__.py
    │   ├── cli_display.py    # CLI显示
    │   ├── notification.py   # 通知管理
    │   └── tray_app.py      # 系统托盘
    └── utils/                # 工具函数
        ├── __init__.py
        ├── exceptions.py     # 异常定义
        └── logger.py         # 日志工具
```

### 添加新功能

#### 1. 添加新的CLI命令

```python
# packy_usage/cli/commands.py

@cli.command()
@click.option('--format', default='table', help='输出格式')
def history(format):
    """显示使用历史"""
    # 实现历史记录功能
    pass
```

#### 2. 扩展配置选项

```python
# packy_usage/config/manager.py

@dataclass
class NewFeatureConfig:
    """新功能配置"""
    enabled: bool = True
    option1: str = "default_value"
    option2: int = 100
```

#### 3. 添加新的通知渠道

```python
# packy_usage/ui/notification.py

class SlackNotifier:
    """Slack通知器"""
    
    def send_message(self, title: str, message: str):
        # 实现Slack消息发送
        pass
```

### 代码规范

#### 代码格式化

```bash
# 自动格式化代码
black packy_usage/

# 检查代码风格
flake8 packy_usage/

# 类型检查
mypy packy_usage/
```

#### 提交规范

```bash
# 提交消息格式
git commit -m "feat: 添加历史记录功能"
git commit -m "fix: 修复Token过期处理逻辑" 
git commit -m "docs: 更新用户手册"
```

### 测试

#### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_api_client.py

# 覆盖率报告
pytest --cov=packy_usage --cov-report=html
```

#### 编写测试

```python
# tests/test_budget_data.py

import pytest
from packy_usage.core.budget_data import BudgetData

def test_budget_data_from_api_response():
    """测试从API响应创建预算数据"""
    api_data = {
        'daily_budget_usd': 10.0,
        'daily_spent_usd': 6.5,
        'monthly_budget_usd': 100.0,
        'monthly_spent_usd': 42.8
    }
    
    budget_data = BudgetData.from_api_response(api_data)
    
    assert budget_data.daily.percentage == 65.0
    assert budget_data.daily.total == 10.0
    assert budget_data.daily.used == 6.5
```

### 构建和发布

#### 构建可执行文件

```bash
# 构建所有平台
python build.py

# 自定义构建选项
python build.py --platform windows --optimize
```

#### 版本发布

```bash
# 更新版本号
# packy_usage/__init__.py
__version__ = "1.1.0"

# 打标签
git tag v1.1.0
git push origin v1.1.0

# 创建发布包
python build.py
```

---

## 📄 附录

### A. 配置参数完整列表

| 参数路径 | 类型 | 默认值 | 说明 |
|----------|------|--------|------|
| `api.endpoint` | string | `https://www.packycode.com/api/backend/users/info` | API端点地址 |
| `api.timeout` | int | `10` | 请求超时时间（秒） |
| `api.retry_count` | int | `3` | 请求重试次数 |
| `polling.enabled` | bool | `true` | 启用自动轮询 |
| `polling.interval` | int | `30` | 轮询间隔（秒） |
| `polling.retry_on_failure` | int | `3` | 轮询失败重试 |
| `display.decimal_places` | int | `2` | 小数位数 |
| `display.currency_symbol` | string | `"$"` | 货币符号 |
| `alerts.daily_warning` | float | `75.0` | 日预算警告阈值 |
| `alerts.daily_critical` | float | `90.0` | 日预算严重阈值 |
| `alerts.monthly_warning` | float | `80.0` | 月预算警告阈值 |
| `alerts.monthly_critical` | float | `95.0` | 月预算严重阈值 |
| `notification.enabled` | bool | `true` | 启用通知 |
| `notification.quiet_hours_start` | string | `"22:00"` | 免打扰开始时间 |
| `notification.quiet_hours_end` | string | `"08:00"` | 免打扰结束时间 |
| `network.proxy` | string | `""` | HTTP代理地址 |
| `network.verify_ssl` | bool | `true` | SSL证书验证 |
| `logging.level` | string | `"INFO"` | 日志级别 |
| `logging.file` | string | `""` | 日志文件路径 |

### B. API响应格式

**成功响应**:
```json
{
  "daily_budget_usd": 10.00,
  "daily_spent_usd": 6.52,
  "monthly_budget_usd": 100.00,
  "monthly_spent_usd": 42.80,
  "last_updated": "2024-01-15T14:30:45Z"
}
```

**错误响应**:
```json
{
  "error": "Unauthorized",
  "message": "Invalid API token",
  "code": 401
}
```

### C. 系统要求

**最低要求**:
- Python 3.8+
- 100MB 可用磁盘空间
- 网络连接
- 系统托盘支持（桌面环境）

**推荐配置**:
- Python 3.10+
- 200MB 可用磁盘空间
- 稳定网络连接
- 通知权限

**操作系统支持**:
- Windows 10+ (x64)
- macOS 10.14+ (x64, ARM64)
- Ubuntu 18.04+ (x64)
- CentOS 7+ (x64)

---

**文档版本**: v1.0.0  
**最后更新**: 2024-01-15  
**维护者**: Packy Usage Team

如有问题或建议，请访问 [项目主页](https://github.com/packycode/packy-usage-monitor) 或提交 Issue。
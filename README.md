# Packy Usage Monitor

一个独立的预算监控工具，用于实时监控 Packy Code API 的预算使用情况。

## 🎯 30秒快速上手

### 🌟 推荐方法（Windows 用户）

**使用 PowerShell 交互式脚本（最佳体验）：**
1. 📁 下载/克隆本项目
2. 🖱️ 右键 `packy.ps1` → 选择"使用 PowerShell 运行"
3. 📝 在菜单中输入 `2` 配置 API Token
4. 🚀 输入 `7` 启动实时监控，或输入 `6` 启动系统托盘
5. ✅ 完成！享受美观的界面和流畅的体验

> 💡 **为什么推荐 PowerShell？**
> - ✨ 更好的中文显示支持
> - 🎨 完美的界面对齐和格式
> - 🚀 实时监控不会卡死
> - 📊 数据展示更清晰美观

### 备选方法

**批处理脚本：**
- 双击 `packy.bat` 使用传统批处理界面

**一键安装（可选）：**
- 运行 `install.bat` 将程序安装到系统，之后可在任意位置使用

## ✨ 功能特性

- 🖥️ **系统托盘应用** - 实时显示预算使用状态，类似VS Code状态栏体验
- 💻 **命令行工具** - 支持脚本化和自动化，多种显示格式
- ⚠️ **智能预警** - 超过阈值自动通知，支持免打扰模式
- 📊 **使用统计** - 详细的预算使用率分析和趋势显示
- 🔐 **安全存储** - API Token 系统密钥环加密保护
- 🌐 **代理支持** - 企业网络环境兼容，支持HTTP代理
- 🔄 **自动轮询** - 定期刷新预算数据，实时监控

## 🚀 快速开始

### 🎯 最快上手方式（强烈推荐）

**使用 PowerShell 交互式脚本：**

```powershell
# 方式1：图形界面操作
1. 找到 packy.ps1 文件
2. 右键点击 → 选择"使用 PowerShell 运行"
3. 在交互式菜单中选择功能

# 方式2：命令行运行
./packy.ps1
```

**交互式菜单功能：**
- `[1]` 检查使用状态 - 快速查看当前预算
- `[2]` 配置设置 - 设置 API Token（首次使用必须）
- `[3]` 系统诊断 - 检查环境和连接
- `[4]` 性能测试 - 测试响应速度
- `[5]` 显示当前状态 - 详细预算报告
- `[6]` 启动系统托盘 - 后台监控模式
- `[7]` 实时监控模式 - 终端实时显示（推荐体验）
- `[0]` 退出程序

> 🌟 **推荐工作流程：**
> 1. 首次使用选择 `[2]` 设置 Token
> 2. 选择 `[3]` 进行系统诊断确保一切正常
> 3. 选择 `[7]` 体验美观的实时监控界面
> 4. 或选择 `[6]` 启动系统托盘后台运行

### 备选方式

**批处理脚本（传统方式）：**
```bash
# 双击运行或命令行执行
packy.bat
```

**一键安装到系统：**
```bash
# 安装后可在任意位置使用
install.bat
```

### 从源码运行

```bash
# 0. 进入项目目录
cd packy-usage-script

# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Token
python packy_usage.py config set-token

# 3. 启动系统托盘应用
python packy_usage.py tray
```

### 方式3：使用打包版本

```bash
# 直接运行编译好的可执行文件
dist\packy-usage-monitor.exe --help  # Windows

# 或使用交互式脚本启动（推荐）
./packy.ps1  # 会自动调用 dist 目录下的 exe
```

## 📋 使用方式

### 系统托盘模式（推荐）

```bash
# 确保在项目目录下运行
cd /path/to/packy-usage-script

# 启动系统托盘应用
python packy_usage.py tray
```

- 显示实时预算使用率图标
- 右键菜单提供快速操作
- 自动预警通知
- 点击查看详细信息

### 命令行模式

```bash
# 确保在项目目录下运行
cd /path/to/packy-usage-script

# 查看当前预算状态
python packy_usage.py status

# 简要显示
python packy_usage.py status --brief
# 输出: [正常] 日预算: 65.2% | [警告] 月预算: 78.9%

# 详细显示（默认）
python packy_usage.py status

# JSON格式输出（便于集成其他工具）
python packy_usage.py status --json

# 仅显示警告状态
python packy_usage.py status --alert-only
```

### 实时监控模式（推荐体验）

```bash
# 使用 PowerShell 脚本启动（最佳体验）
./packy.ps1
# 选择 [7] 实时监控模式

# 或直接命令行启动
python packy_usage.py watch --interval 30

# 自定义刷新间隔（单位：秒）
python packy_usage.py watch --interval 10
```

**实时监控界面预览：**
```
============================================================
  Packy 预算监控 - 20:16:10 (刷新间隔: 30秒)
============================================================

             日预算             |            月预算
  ---------------------------+---------------------------
  ###########---------        | ###-----------------
    55.7% 已使用               |   17.3% 已使用

  已使用:     $55.68          | 已使用:    $517.99
  总额度:    $100.00          | 总额度:  $3,000.00
  剩余额:     $44.32          | 剩余额:  $2,482.01

  状态: ✅ 正常                | 状态: ✅ 正常
============================================================
```

### CI/CD 集成

```bash
# 确保在项目目录下或指定完整路径
cd /path/to/packy-usage-script

# 检查预算状态，适用于构建脚本
python packy_usage.py check --threshold 90

# 返回码：
# 0 = 正常
# 1 = 超过阈值
# 2 = 检查失败
```

## ⚙️ 配置管理

### Token 配置

支持两种 Token 类型：

1. **API Token（推荐）**
   ```bash
   cd /path/to/packy-usage-script
   python packy_usage.py config set-token
   # 输入以 'sk-' 开头的永久API Token
   ```

2. **JWT Token**
   ```bash
   # 从 PackyCode Dashboard Cookie 获取
   # 1. 访问 PackyCode Dashboard
   # 2. 按 F12 打开开发者工具
   # 3. Application > Cookies > 复制 'token' 值
   cd /path/to/packy-usage-script
   python packy_usage.py config set-token
   ```

### 查看和管理配置

```bash
# 确保在项目目录下运行
cd /path/to/packy-usage-script

# 显示当前配置
python packy_usage.py config show

# 重置为默认配置
python packy_usage.py config reset
```

### 配置文件

配置文件位置：`~/.packy-usage/config.yaml`

参考 `config.example.yaml` 了解所有配置选项。

## 🔧 系统托盘功能

- **图标状态**：
  - 🟢 绿色：使用率正常 (< 50%)
  - 🔵 蓝色：中等使用 (50-75%)
  - 🟡 黄色：警告状态 (75-90%)
  - 🔴 红色：严重状态 (≥ 90%)
  - ⚪ 灰色：初始化或错误

- **右键菜单**：
  - 📊 显示详情：查看详细预算信息
  - 🔄 刷新：立即更新数据
  - ⚙️ 设置：配置选项
  - ❌ 退出：关闭应用

## 📊 通知功能

### 智能预警
- 使用率超过75%：警告通知
- 使用率超过90%：严重警告通知
- 支持通知去重，避免重复打扰

### 免打扰模式
- 默认22:00-08:00静默时间
- 严重警告仍会发送通知
- 可通过配置文件自定义

## 🔧 开发和构建

### 开发环境

```bash
# 进入项目目录
cd /path/to/packy-usage-script

# 安装开发依赖
pip install -r requirements.txt

# 运行测试
pytest

# 代码格式化
black packy_usage/
flake8 packy_usage/
```

### 构建可执行文件

```bash
# 进入项目目录
cd /path/to/packy-usage-script

# 自动构建
python build.py

# 构建输出位置：dist/
# 包含：
# - 可执行文件 (Windows: .exe, Linux/Mac: 无扩展名)
# - 安装脚本
# - README
```

### 项目结构

```
packy-usage-script/
├── packy.bat              # Windows 交互式启动器
├── packy.ps1              # PowerShell 交互式启动器（中文支持）
├── install.bat            # Windows 一键安装脚本
├── packy_usage.py         # 主入口文件
├── requirements.txt       # 依赖列表
├── build.py              # 构建脚本
├── config.example.yaml   # 配置示例
├── dist/                 # 编译输出目录
│   └── packy-usage-monitor.exe  # 可执行文件
└── packy_usage/          # 主要代码包
    ├── cli/              # 命令行界面
    ├── core/             # 核心功能（API、数据模型）
    ├── config/           # 配置管理
    ├── security/         # 安全功能（Token存储）
    ├── ui/               # 用户界面（托盘、通知、显示）
    └── utils/            # 工具函数
```

## 🌐 网络和代理

### 代理配置

支持多种代理配置方式：

1. **配置文件**：
   ```yaml
   network:
     proxy: "http://proxy.company.com:8080"
   ```

2. **环境变量**：
   ```bash
   export HTTP_PROXY=http://proxy.company.com:8080
   export HTTPS_PROXY=http://proxy.company.com:8080
   ```

### SSL 证书

- 默认启用SSL验证
- 企业环境可通过配置禁用：
  ```yaml
  network:
    verify_ssl: false
  ```

## 🐛 问题排查

### 常见问题

1. **Token 无效**
   ```bash
   # 重新配置Token（确保在项目目录下）
   cd /path/to/packy-usage-script
   python packy_usage.py config set-token
   ```

2. **网络连接失败**
   - 检查网络连接
   - 确认代理设置
   - 检查防火墙规则

3. **系统托盘不显示**
   - 确保安装了所有GUI依赖
   - Linux需要系统托盘支持
   - macOS可能需要权限设置

4. **通知不工作**
   - 检查系统通知权限
   - 确认通知服务运行
   - 查看通知配置

### 日志调试

```bash
# 确保在项目目录下运行
cd /path/to/packy-usage-script

# 启用调试日志
python packy_usage.py --config-dir ~/.packy-usage-debug config show

# 查看日志文件
tail -f ~/.packy-usage/app.log  # Linux/Mac
type %USERPROFILE%\.packy-usage\app.log  # Windows
```

## 📚 文档

- **📖 [用户使用手册](docs/USER_GUIDE.md)** - 详细的使用说明和配置指南
- **🚀 [快速开始指南](docs/QUICK_START.md)** - 3分钟快速上手
- **🛠️ [开发者指南](docs/DEVELOPER_GUIDE.md)** - 架构设计和开发规范

## 🤝 贡献

欢迎提交Issue和Pull Request！

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 📄 许可证

MIT License - 详见 LICENSE 文件

## 🙏 致谢

- 基于 VS Code 扩展 `packy-usage-vsce` 的设计理念
- 使用 `pystray` 实现跨平台系统托盘功能
- 使用 `keyring` 提供安全的凭据存储
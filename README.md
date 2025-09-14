# Packy Usage Monitor

一个独立的预算监控工具，用于实时监控 Packy Code API 的预算使用情况。

## 🎯 30秒快速上手

**Windows 用户最快方法：**
1. 📁 下载/克隆本项目
2. 🖱️ 双击 `packy.bat` 或 `packy.ps1`
3. 📝 选择菜单 2 设置 API Token
4. 🚀 选择菜单 6 启动系统托盘监控
5. ✅ 完成！查看右下角系统托盘图标

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

### 🎯 最快上手方式（Windows 用户推荐）

1. **下载预编译版本**：
   - 进入 `dist` 目录，找到 `packy-usage-monitor.exe`
   - 或使用提供的交互式脚本（见下方）

2. **使用交互式脚本（无需记命令）**：
   ```bash
   # 方式1：使用批处理脚本（Windows）
   双击 packy.bat
   # 或在命令行运行：
   ./packy.bat

   # 方式2：使用 PowerShell 脚本（中文支持更好）
   右键 packy.ps1 -> 使用 PowerShell 运行
   # 或在 PowerShell 中运行：
   ./packy.ps1
   ```

   交互式界面会提供菜单选项，你可以：
   - 输入数字选择功能
   - 无需记住复杂的命令参数
   - 支持中文显示

3. **一键安装到系统**：
   ```bash
   # 双击运行安装脚本
   install.bat

   # 安装后可在任意位置运行：
   packy-usage-monitor status
   ```

### 方式1：使用便捷脚本（最简单）

```bash
# Windows 用户
1. 双击 packy.bat 或 packy.ps1
2. 在交互式菜单中选择功能
3. 首次使用选择 "2. 配置设置" 设置 Token
4. 然后选择 "6. 启动系统托盘应用"
```

### 方式2：从源码运行

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
# 0. 进入项目目录
cd packy-usage-script

# 1. 构建可执行文件
python build.py

# 2. 运行可执行文件
cd dist
./packy-usage-monitor --help  # Linux/Mac
packy-usage-monitor.exe --help  # Windows
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

### 实时监控模式

```bash
# 确保在项目目录下运行
cd /path/to/packy-usage-script

# 启动实时监控（类似 htop 风格）
python packy_usage.py watch --interval 30

# 自定义刷新间隔（单位：秒）
python packy_usage.py watch --interval 10
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
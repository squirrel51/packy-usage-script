# 快速开始指南

## 🚀 3分钟快速上手

### 第一步：安装依赖
```bash
pip install -r requirements.txt
```

### 第二步：配置 Token
```bash
python packy_usage.py config set-token
```
输入您的 API Token（推荐）或 JWT Token

### 第三步：选择使用方式

#### 选择A：系统托盘应用（推荐）
```bash
python packy_usage.py tray
```
- ✅ 系统托盘显示实时状态
- ✅ 自动预警通知  
- ✅ 右键菜单快速操作

#### 选择B：命令行查看
```bash
# 详细显示
python packy_usage.py status

# 简要显示
python packy_usage.py status --brief
```

#### 选择C：实时监控
```bash
python packy_usage.py watch
```

## 🎯 常用命令

```bash
# 查看帮助
python packy_usage.py --help

# 查看配置
python packy_usage.py config show

# JSON格式输出
python packy_usage.py status --json

# CI/CD检查
python packy_usage.py check --threshold 90
```

## 📦 获取 Token

### API Token（推荐）
1. 访问 [PackyCode Dashboard](https://www.packycode.com)
2. 导航到 API 设置
3. 生成 API Token（以 `sk-` 开头）

### JWT Token（临时）
1. 访问 PackyCode Dashboard
2. 按 F12 → Application → Cookies 
3. 复制 "token" Cookie 值

## 🐛 遇到问题？

```bash
# 重新配置 Token
python packy_usage.py config set-token

# 重置配置
python packy_usage.py config reset

# 查看详细文档
cat docs/USER_GUIDE.md
```

## 📄 更多信息

- 📖 **完整文档**: [docs/USER_GUIDE.md](./USER_GUIDE.md)
- 🐛 **问题反馈**: GitHub Issues
- 💬 **社区支持**: PackyCode 用户论坛

---

**需要帮助？** 查看完整的 [用户使用手册](./USER_GUIDE.md) 获取详细说明。
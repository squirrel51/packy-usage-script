#!/usr/bin/env python3
"""
构建脚本
使用 PyInstaller 将应用打包为可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# 项目信息
PROJECT_NAME = "packy-usage-monitor"
VERSION = "1.0.0"
AUTHOR = "Packy Usage Team"

# 路径配置
SCRIPT_DIR = Path(__file__).parent
DIST_DIR = SCRIPT_DIR / "dist"
BUILD_DIR = SCRIPT_DIR / "build"
SPEC_FILE = SCRIPT_DIR / f"{PROJECT_NAME}.spec"

def clean_build():
    """清理构建目录"""
    print("🧹 Cleaning build directories...")
    
    for dir_path in [DIST_DIR, BUILD_DIR]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"   Removed {dir_path}")
    
    if SPEC_FILE.exists():
        SPEC_FILE.unlink()
        print(f"   Removed {SPEC_FILE}")

def install_dependencies():
    """安装依赖"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, cwd=SCRIPT_DIR)
        print("   ✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to install dependencies: {e}")
        sys.exit(1)

def create_pyinstaller_spec():
    """创建 PyInstaller 配置文件"""
    print("📝 Creating PyInstaller spec file...")
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['packy_usage.py'],
    pathex=['{SCRIPT_DIR}'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'pystray._win32',
        'pystray._darwin', 
        'pystray._gtk',
        'PIL._tkinter_finder',
        'keyring.backends'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{PROJECT_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 保留控制台，便于调试和命令行使用
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)
'''
    
    with open(SPEC_FILE, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"   ✅ Spec file created: {SPEC_FILE}")

def create_version_info():
    """创建版本信息文件 (Windows)"""
    if sys.platform != 'win32':
        return
    
    print("📄 Creating version info file...")
    
    version_info = f'''VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({VERSION.replace('.', ', ')}, 0),
    prodvers=({VERSION.replace('.', ', ')}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'{AUTHOR}'),
         StringStruct(u'FileDescription', u'Packy Usage Monitor - Budget monitoring tool'),
         StringStruct(u'FileVersion', u'{VERSION}'),
         StringStruct(u'InternalName', u'{PROJECT_NAME}'),
         StringStruct(u'LegalCopyright', u'Copyright (C) 2024 {AUTHOR}'),
         StringStruct(u'OriginalFilename', u'{PROJECT_NAME}.exe'),
         StringStruct(u'ProductName', u'Packy Usage Monitor'),
         StringStruct(u'ProductVersion', u'{VERSION}')])
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    print("   ✅ Version info file created")

def build_executable():
    """构建可执行文件"""
    print("🔨 Building executable...")
    
    try:
        # 使用 PyInstaller 构建
        subprocess.run([
            sys.executable, "-m", "PyInstaller", 
            "--clean",
            str(SPEC_FILE)
        ], check=True, cwd=SCRIPT_DIR)
        
        print("   ✅ Build completed successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Build failed: {e}")
        sys.exit(1)

def create_installer_scripts():
    """创建安装脚本"""
    print("📦 Creating installer scripts...")
    
    # Windows 批处理安装脚本
    if sys.platform == 'win32':
        install_bat = f'''@echo off
echo Installing {PROJECT_NAME}...

REM 创建目标目录
if not exist "%LOCALAPPDATA%\\{PROJECT_NAME}" mkdir "%LOCALAPPDATA%\\{PROJECT_NAME}"

REM 复制可执行文件
copy "{PROJECT_NAME}.exe" "%LOCALAPPDATA%\\{PROJECT_NAME}\\"

REM 添加到PATH（需要管理员权限）
setx PATH "%PATH%;%LOCALAPPDATA%\\{PROJECT_NAME}"

echo Installation completed!
echo You can now run '{PROJECT_NAME}' from anywhere in the command line.
pause
'''
        
        with open(DIST_DIR / "install.bat", 'w', encoding='utf-8') as f:
            f.write(install_bat)
    
    # macOS/Linux 安装脚本
    else:
        install_sh = f'''#!/bin/bash
echo "Installing {PROJECT_NAME}..."

# 创建目标目录
mkdir -p ~/.local/bin

# 复制可执行文件
cp {PROJECT_NAME} ~/.local/bin/

# 设置可执行权限
chmod +x ~/.local/bin/{PROJECT_NAME}

# 检查PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc 2>/dev/null || true
    echo "Added ~/.local/bin to PATH in shell configuration files"
fi

echo "Installation completed!"
echo "Please restart your terminal or run 'source ~/.bashrc' to update PATH"
echo "You can now run '{PROJECT_NAME}' from anywhere"
'''
        
        install_script = DIST_DIR / "install.sh"
        with open(install_script, 'w', encoding='utf-8') as f:
            f.write(install_sh)
        
        # 设置可执行权限
        os.chmod(install_script, 0o755)
    
    print("   ✅ Installer scripts created")

def create_readme():
    """创建发布README"""
    print("📋 Creating release README...")
    
    readme_content = f'''# {PROJECT_NAME} v{VERSION}

独立的 Packy Code API 预算监控工具。

## 快速开始

### 1. 配置 API Token

```bash
{PROJECT_NAME} config set-token
```

### 2. 运行方式

```bash
# 系统托盘模式（推荐）
{PROJECT_NAME} tray

# 查看当前状态
{PROJECT_NAME} status

# 实时监控模式
{PROJECT_NAME} watch

# 简要显示
{PROJECT_NAME} status --brief

# JSON 输出
{PROJECT_NAME} status --json
```

### 3. 配置管理

```bash
# 查看配置
{PROJECT_NAME} config show

# 重置配置
{PROJECT_NAME} config reset
```

## 功能特性

- 🖥️ **系统托盘集成** - 实时显示预算状态
- 📊 **多种显示模式** - 命令行、监控、JSON输出
- ⚠️ **智能警报** - 自动通知预算超限
- 🔐 **安全存储** - API Token 加密保护  
- 🌐 **代理支持** - 适配企业网络环境
- 🔄 **自动轮询** - 定期刷新预算数据

## 安装方式

### Windows
运行 `install.bat` 将程序安装到系统路径。

### macOS/Linux  
运行 `install.sh` 将程序安装到 `~/.local/bin`。

## 配置文件

配置文件位置：`~/.packy-usage/config.yaml`

首次运行时会自动创建默认配置。

## 支持的 Token 类型

1. **API Token (推荐)**
   - 永久有效的访问令牌
   - 从 PackyCode Dashboard 获取 (以 'sk-' 开头)

2. **JWT Token** 
   - 临时令牌，从 PackyCode 网站 Cookie 获取
   - 需要定期更新

## 问题排查

- **Token 问题**: 使用 `{PROJECT_NAME} config set-token` 重新配置
- **网络问题**: 检查代理配置或防火墙设置
- **权限问题**: 确保有系统密钥环的访问权限

## 技术支持

- 问题反馈: https://github.com/packycode/packy-usage-monitor/issues
- 文档: https://docs.packycode.com
'''
    
    with open(DIST_DIR / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("   ✅ Release README created")

def print_build_summary():
    """打印构建摘要"""
    print("\n" + "="*50)
    print("🎉 BUILD COMPLETED SUCCESSFULLY!")
    print("="*50)
    
    exe_name = f"{PROJECT_NAME}.exe" if sys.platform == 'win32' else PROJECT_NAME
    exe_path = DIST_DIR / exe_name
    
    if exe_path.exists():
        size = exe_path.stat().st_size / (1024 * 1024)  # MB
        print(f"📦 Executable: {exe_path}")
        print(f"📏 Size: {size:.1f} MB")
    
    print(f"📂 Output directory: {DIST_DIR}")
    print("\n🚀 Quick start:")
    print(f"   cd {DIST_DIR}")
    print(f"   ./{exe_name} --help")
    
    print("\n💡 Next steps:")
    print("   1. Test the executable")
    print("   2. Run installer script for system-wide installation")
    print("   3. Configure API Token")

def main():
    """主构建流程"""
    print(f"🚀 Building {PROJECT_NAME} v{VERSION}")
    print("="*50)
    
    try:
        # 1. 清理
        clean_build()
        
        # 2. 安装依赖
        install_dependencies()
        
        # 3. 创建构建文件
        create_version_info()
        create_pyinstaller_spec()
        
        # 4. 构建
        build_executable()
        
        # 5. 创建附加文件
        create_installer_scripts()
        create_readme()
        
        # 6. 完成摘要
        print_build_summary()
        
    except KeyboardInterrupt:
        print("\n❌ Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
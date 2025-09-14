#!/usr/bin/env python3
"""
Packy Usage Monitor - 独立预算监控工具
"""

import sys
import click
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from packy_usage.cli.commands import cli


if __name__ == "__main__":
    cli()
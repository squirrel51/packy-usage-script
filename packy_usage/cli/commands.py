"""
命令行接口实现
"""

import click
import sys
from pathlib import Path

from ..config.manager import ConfigManager
from ..core.api_client import ApiClient
from ..security.token_manager import TokenManager
from ..ui.tray_app import TrayApp
from ..ui.cli_display import CliDisplay
from ..utils.logger import setup_logger


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='显示版本信息')
@click.option('--config-dir', help='指定配置目录路径')
@click.pass_context
def cli(ctx, version, config_dir):
    """Packy Usage Monitor - 预算监控工具"""
    
    if version:
        from .. import __version__
        click.echo(f"Packy Usage Monitor v{__version__}")
        return
    
    # 设置配置目录
    if config_dir:
        ConfigManager.set_config_dir(Path(config_dir))
    
    # 如果没有子命令，显示帮助
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.option('--brief', '-b', is_flag=True, help='简要显示')
@click.option('--json', 'output_json', is_flag=True, help='JSON格式输出')
@click.option('--alert-only', is_flag=True, help='仅显示警告状态')
@click.option('--debug', is_flag=True, help='启用详细调试信息')
def status(brief, output_json, alert_only, debug):
    """显示当前预算使用状态"""
    try:
        # 如果启用调试模式，设置详细日志
        if debug:
            import logging
            logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
            click.echo("🐛 调试模式已启用")
        
        config = ConfigManager()
        token_manager = TokenManager()
        api_client = ApiClient(config, token_manager)
        
        # 调试信息输出
        if debug:
            click.echo(f"🔧 API端点: {config.get_api_endpoint()}")
            token_info = token_manager.get_token_info()
            if token_info:
                click.echo(f"🔑 Token类型: {token_info.get('type', '未知')}")
                click.echo(f"🔑 Token状态: {'有效' if token_info.get('exists') else '无效'}")
            else:
                click.echo("🔑 未找到Token信息")
        
        # 获取预算数据
        budget_data = api_client.fetch_budget_data_sync()
        
        if not budget_data:
            click.echo("❌ 无法获取预算数据，请检查配置", err=True)
            sys.exit(1)
        
        # 显示数据
        display = CliDisplay()
        display.show_budget_data(budget_data, brief, output_json, alert_only)
        
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--interval', '-i', default=30, help='轮询间隔（秒）')
def watch(interval):
    """实时监控模式"""
    try:
        config = ConfigManager()
        token_manager = TokenManager()
        api_client = ApiClient(config, token_manager)
        display = CliDisplay()
        
        click.echo(">> 启动实时监控模式 (Ctrl+C 退出)")
        display.watch_mode(api_client, interval)
        
    except KeyboardInterrupt:
        click.echo("\n👋 监控已停止")
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--debug', is_flag=True, help='启用调试模式')
def tray(debug):
    """启动系统托盘应用"""
    try:
        # 如果启用调试模式，设置详细日志
        if debug:
            import logging
            logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')
            click.echo("🐛 调试模式已启用")
        
        config = ConfigManager()
        token_manager = TokenManager()
        api_client = ApiClient(config, token_manager)
        
        # 调试信息输出
        if debug:
            click.echo(f"🔧 API端点: {config.get_api_endpoint()}")
            token_info = token_manager.get_token_info()
            if token_info:
                click.echo(f"🔑 Token类型: {token_info.get('type', '未知')}")
                click.echo(f"🔑 Token状态: {'有效' if token_info.get('exists') else '无效'}")
            else:
                click.echo("🔑 未找到Token信息")
        
        app = TrayApp(config, token_manager, api_client)
        click.echo("🖥️  启动系统托盘应用...")
        
        if debug:
            click.echo("📊 正在测试API连接...")
            test_result = api_client.test_connection_sync()
            click.echo(f"🔗 API连接测试: {'成功' if test_result else '失败'}")
        
        app.run()
        
    except Exception as e:
        click.echo(f"❌ 托盘应用启动失败: {e}", err=True)
        sys.exit(1)


@cli.group()
def config():
    """配置管理"""
    pass


@config.command('show')
def config_show():
    """显示当前配置"""
    try:
        config = ConfigManager()
        config.show_config()
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)


@config.command('set-token')
def config_set_token():
    """设置 API Token"""
    try:
        token_manager = TokenManager()
        
        click.echo("📝 配置 API Token")
        click.echo("支持的 Token 类型：")
        click.echo("  • API Token (推荐): 以 'sk-' 开头的永久Token")
        click.echo("  • JWT Token: 从 PackyCode 网站 Cookie 获取的临时Token")
        click.echo()
        
        # 询问是否隐藏输入
        hide_input = click.confirm("是否隐藏Token输入？（推荐选择 No 以便检查输入内容）", default=False)
        
        if hide_input:
            token = click.prompt("请输入您的 Token", hide_input=True)
        else:
            click.echo("⚠️  Token将以明文显示，请确保周围环境安全")
            token = click.prompt("请输入您的 Token")
        
        
        if not token.strip():
            click.echo("❌ Token 不能为空", err=True)
            return
        
        # 验证并保存Token
        token_manager.save_token(token.strip())
        
        if token.startswith('sk-'):
            click.echo("✅ API Token 保存成功！（永久有效）")
        else:
            # 尝试解析JWT获取过期时间
            exp_info = token_manager.get_token_expiration(token)
            if exp_info:
                click.echo(f"✅ JWT Token 保存成功！将于 {exp_info} 过期")
            else:
                click.echo("✅ Token 保存成功！")
        
    except Exception as e:
        click.echo(f"❌ 保存失败: {e}", err=True)


@cli.command()
def diagnose():
    """运行系统诊断检查"""
    click.echo("🔍 Packy Usage Monitor 系统诊断")
    click.echo("=" * 50)
    
    try:
        # 1. 检查配置
        click.echo("1️⃣ 检查配置文件...")
        config = ConfigManager()
        click.echo(f"   ✅ 配置文件: {config.config_directory}/config.yaml")
        click.echo(f"   ✅ API端点: {config.get_api_endpoint()}")
        
        # 2. 检查Token
        click.echo("\n2️⃣ 检查Token状态...")
        token_manager = TokenManager()
        token_info = token_manager.get_token_info()
        
        if token_info:
            click.echo(f"   ✅ Token存在: {token_info.get('type', '未知')}")
            if token_info.get('expired'):
                click.echo(f"   ❌ Token已过期")
            else:
                click.echo(f"   ✅ Token有效")
        else:
            click.echo("   ❌ 未找到Token")
        
        # 3. 测试网络连接
        click.echo("\n3️⃣ 测试网络连接...")
        api_client = ApiClient(config, token_manager)
        
        if token_manager.is_token_available():
            try:
                test_result = api_client.test_connection_sync()
                if test_result:
                    click.echo("   ✅ API连接成功")
                else:
                    click.echo("   ❌ API连接失败")
            except Exception as e:
                click.echo(f"   ❌ 连接测试错误: {e}")
        else:
            click.echo("   ⚠️  跳过连接测试（无有效Token）")
        
        # 4. 检查依赖
        click.echo("\n4️⃣ 检查依赖库...")
        dependencies = [
            ('requests', 'HTTP请求'),
            ('pystray', '系统托盘'),
            ('plyer', '桌面通知'),
            ('keyring', '安全存储'),
            ('yaml', '配置解析'),
            ('click', '命令行界面'),
            ('PIL', '图像处理')
        ]
        
        for dep, desc in dependencies:
            try:
                __import__(dep)
                click.echo(f"   ✅ {dep}: {desc}")
            except ImportError:
                click.echo(f"   ❌ {dep}: {desc} - 未安装")
        
        # 5. 系统信息
        click.echo("\n5️⃣ 系统信息...")
        import sys
        import platform
        click.echo(f"   Python版本: {sys.version}")
        click.echo(f"   操作系统: {platform.system()} {platform.release()}")
        
        click.echo("\n✅ 诊断完成")
        
    except Exception as e:
        click.echo(f"\n❌ 诊断过程出错: {e}", err=True)


@cli.command()
@click.option('--iterations', '-n', default=10, help='测试迭代次数')
@click.option('--cached/--no-cached', default=True, help='是否使用缓存')
def perf_test(iterations, cached):
    """性能测试 - 测试连接池和缓存优化效果"""
    import time
    
    click.echo(">> Packy Usage Monitor 性能测试")
    click.echo("=" * 50)
    
    try:
        config = ConfigManager()
        token_manager = TokenManager()
        api_client = ApiClient(config, token_manager)
        
        # 如果不使用缓存，清空缓存
        if not cached:
            api_client.clear_cache()
            click.echo("已清空缓存，测试无缓存性能")
        else:
            click.echo("使用缓存进行测试")
        
        click.echo(f"测试参数: 迭代次数={iterations}, 缓存={cached}")
        click.echo()
        
        # 执行测试
        times = []
        for i in range(iterations):
            start_time = time.time()
            
            try:
                data = api_client.fetch_budget_data_sync()
                elapsed = time.time() - start_time
                times.append(elapsed)
                
                if data:
                    status = f"[OK] 第 {i+1}/{iterations} 次: {elapsed:.3f}秒"
                    if elapsed < 0.1:
                        status += " (缓存命中)"
                    click.echo(status)
                else:
                    click.echo(f"[!] 第 {i+1}/{iterations} 次: 无数据")
                    
            except Exception as e:
                elapsed = time.time() - start_time
                click.echo(f"[X] 第 {i+1}/{iterations} 次: {e}")
            
            # 如果不使用缓存，每次清空
            if not cached:
                api_client.clear_cache()
        
        # 统计结果
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            click.echo("\n== 性能统计 ==")
            click.echo("=" * 30)
            click.echo(f"平均响应时间: {avg_time:.3f} 秒")
            click.echo(f"最快响应时间: {min_time:.3f} 秒")
            click.echo(f"最慢响应时间: {max_time:.3f} 秒")
            click.echo(f"成功率: {len(times)}/{iterations} ({len(times)*100/iterations:.1f}%)")
            
            # 显示连接池状态
            stats = api_client.get_connection_stats()
            click.echo("\n== 连接池状态 ==")
            click.echo("=" * 30)
            click.echo(f"同步会话活跃: {stats.get('sync_session_active', False)}")
            click.echo(f"异步会话活跃: {stats.get('async_session_active', False)}")
            click.echo(f"缓存项数量: {stats.get('cache_size', 0)}")
            click.echo(f"缓存TTL: {stats.get('cache_ttl_seconds', 0)}秒")
            click.echo(f"连接池大小: {stats.get('pool_maxsize', 0)}")
            
            # 性能评价
            click.echo("\n== 性能评价 ==")
            click.echo("=" * 30)
            if avg_time < 0.5:
                click.echo("[OK] 优秀 - 响应速度极快")
            elif avg_time < 1.0:
                click.echo("[OK] 良好 - 响应速度正常")
            elif avg_time < 2.0:
                click.echo("[!] 一般 - 可能需要优化")
            else:
                click.echo("[X] 较差 - 建议检查网络或配置")
                
    except Exception as e:
        click.echo(f"[X] 性能测试失败: {e}", err=True)


@config.command('reset')
@click.confirmation_option(prompt='确定要重置所有配置吗？')
def config_reset():
    """重置配置为默认值"""
    try:
        config = ConfigManager()
        config.reset_to_defaults()
        click.echo("✅ 配置已重置为默认值")
    except Exception as e:
        click.echo(f"❌ 重置失败: {e}", err=True)


@cli.command()
@click.option('--threshold', default=90, help='预算使用率阈值（百分比）')
def check(threshold):
    """检查预算状态（适用于CI/CD）"""
    try:
        config = ConfigManager()
        token_manager = TokenManager()
        api_client = ApiClient(config, token_manager)
        
        budget_data = api_client.fetch_budget_data_sync()
        
        if not budget_data:
            click.echo("❌ 无法获取预算数据")
            sys.exit(2)
        
        daily_usage = budget_data.daily.percentage
        monthly_usage = budget_data.monthly.percentage
        
        max_usage = max(daily_usage, monthly_usage)
        
        if max_usage >= threshold:
            click.echo(f"❌ 预算使用率过高: {max_usage:.1f}% (阈值: {threshold}%)")
            sys.exit(1)
        else:
            click.echo(f"✅ 预算使用正常: {max_usage:.1f}%")
            sys.exit(0)
            
    except Exception as e:
        click.echo(f"❌ 检查失败: {e}", err=True)
        sys.exit(2)
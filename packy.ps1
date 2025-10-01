# Packy Usage Monitor - Interactive PowerShell Interface
# Created by: 浮浮酱 (猫娘工程师)
# Enhanced with comprehensive UTF-8 Chinese support

# Set comprehensive UTF-8 encoding for Chinese characters
try {
    # Set console encoding to UTF-8
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::InputEncoding = [System.Text.Encoding]::UTF8

    # Additional PowerShell specific encoding settings
    $OutputEncoding = [System.Text.Encoding]::UTF8
    $PSDefaultParameterValues['*:Encoding'] = 'utf8'

    # Set code page to UTF-8 for maximum compatibility
    cmd /c "chcp 65001 >nul 2>&1"

    Write-Host "[信息] UTF-8 编码已配置，支持中文字符显示" -ForegroundColor Green
} catch {
    Write-Host "[警告] 某些编码设置可能未完全应用" -ForegroundColor Yellow
}
$Host.UI.RawUI.WindowTitle = "Packy 使用监视器 - 交互模式"

$AppDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ExePath = Join-Path $AppDir "dist\packy-usage-monitor.exe"

# Check if executable exists
if (-not (Test-Path $ExePath)) {
    Write-Host "[错误] 在 dist 目录中找不到 packy-usage-monitor.exe" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# Define menu options
$menuOptions = @(
    @{ Number = 1; Command = "check"; Description = "检查使用状态 (用于 CI/CD)" },
    @{ Number = 2; Command = "config"; Description = "配置设置" },
    @{ Number = 3; Command = "diagnose"; Description = "系统诊断" },
    @{ Number = 4; Command = "perf-test"; Description = "性能测试" },
    @{ Number = 5; Command = "status"; Description = "显示当前使用状态" },
    @{ Number = 6; Command = "tray"; Description = "启动系统托盘应用" },
    @{ Number = 7; Command = "watch"; Description = "实时监控模式" },
    @{ Number = 8; Command = "scheduler"; Description = "任务调度器管理" },
    @{ Number = 9; Command = "state"; Description = "状态管理" },
    @{ Number = 10; Command = "token"; Description = "设置 API Token" },
    @{ Number = 11; Command = "version"; Description = "显示版本信息" },
    @{ Number = 12; Command = "help"; Description = "显示帮助信息" },
    @{ Number = 0; Command = "exit"; Description = "退出程序" }
)

$validCommands = @("check", "config", "diagnose", "perf-test", "status", "tray", "watch", "scheduler", "state", "token")

# Function to show menu
function Show-Menu {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "    Packy 使用监视器 - 交互式终端" -ForegroundColor Yellow
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "请选择操作：" -ForegroundColor Green
    Write-Host ""

    foreach ($option in $menuOptions) {
        if ($option.Number -eq 0) {
            Write-Host "  [$($option.Number)] $($option.Description)" -ForegroundColor Red
        } elseif ($option.Command -eq "help" -or $option.Command -eq "version") {
            Write-Host "  [$($option.Number)] $($option.Description)" -ForegroundColor Cyan
        } elseif ($option.Command -eq "token") {
            Write-Host "  [$($option.Number)] $($option.Description)" -ForegroundColor Magenta
        } else {
            Write-Host "  [$($option.Number)] $($option.Description)" -ForegroundColor White
        }
    }
    Write-Host ""
}

# Initial welcome and clear screen
Clear-Host

# Interactive loop
while ($true) {
    Show-Menu
    Write-Host "请输入选择 [0-12]: " -ForegroundColor Yellow -NoNewline
    $userInput = Read-Host

    # Handle empty input
    if ([string]::IsNullOrWhiteSpace($userInput)) {
        Write-Host ""
        Write-Host "[提示] 请输入有效的数字选项 (0-12)" -ForegroundColor Yellow
        Start-Sleep -Seconds 1
        Clear-Host
        continue
    }

    $userInput = $userInput.Trim()

    # Try to parse as number
    $selectedNumber = $null
    if ([int]::TryParse($userInput, [ref]$selectedNumber)) {
        # Find matching menu option
        $selectedOption = $menuOptions | Where-Object { $_.Number -eq $selectedNumber }

        if ($selectedOption) {
            $cmd = $selectedOption.Command
        } else {
            Write-Host ""
            Write-Host "[错误] 无效选择：$userInput (请输入 0-12)" -ForegroundColor Red
            Start-Sleep -Seconds 2
            Clear-Host
            continue
        }
    } else {
        # Handle direct command input (backward compatibility)
        $cmd = $userInput.ToLower()
        if (-not ($cmd -in @("check", "config", "diagnose", "perf-test", "status", "tray", "watch", "scheduler", "state", "version", "help", "exit", "quit", "q", "token"))) {
            Write-Host ""
            Write-Host "[错误] 无效选择：$userInput" -ForegroundColor Red
            Write-Host "[提示] 请输入数字 0-12 或直接输入命令名称" -ForegroundColor Yellow
            Start-Sleep -Seconds 2
            Clear-Host
            continue
        }
    }

    # Handle built-in commands
    switch ($cmd) {
        { $_ -in @("exit", "quit", "q") } {
            Clear-Host
            Write-Host ""
            Write-Host "================================================" -ForegroundColor Cyan
            Write-Host "感谢使用 Packy 使用监视器！再见！" -ForegroundColor Green
            Write-Host "================================================" -ForegroundColor Cyan
            Start-Sleep -Seconds 2
            exit 0
        }

        "help" {
            Clear-Host
            Write-Host ""
            Write-Host "================================================" -ForegroundColor Cyan
            Write-Host "         Packy 使用监视器 - 帮助信息" -ForegroundColor Yellow
            Write-Host "================================================" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "可用命令：" -ForegroundColor Green
            Write-Host ""
            foreach ($option in $menuOptions[0..10]) {  # Exclude help and exit from detailed list
                Write-Host "  $($option.Command.PadRight(12)) - $($option.Description)" -ForegroundColor White
            }
            Write-Host ""
            Write-Host "[提示] 您可以输入数字 [0-12] 或直接输入命令名称" -ForegroundColor Cyan
            Write-Host ""
            Read-Host "按回车键继续"
            Clear-Host
            continue
        }

        "token" {
            Clear-Host
            Write-Host ""
            Write-Host "================================================" -ForegroundColor Cyan
            Write-Host "         Packy 使用监视器 - Token 设置" -ForegroundColor Yellow
            Write-Host "================================================" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "请选择操作：" -ForegroundColor Green
            Write-Host "  [1] 设置新的 API Token" -ForegroundColor White
            Write-Host "  [2] 查看当前配置状态" -ForegroundColor White
            Write-Host "  [0] 返回主菜单" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "请输入选择 [0-2]: " -ForegroundColor Yellow -NoNewline
            $tokenChoice = Read-Host

            switch ($tokenChoice.Trim()) {
                "1" {
                    Write-Host ""
                    Write-Host "请输入您的 API Token:" -ForegroundColor Green
                    Write-Host "[提示] Token 将被安全存储，用于API认证" -ForegroundColor Cyan
                    Write-Host ""
                    Write-Host "Token: " -ForegroundColor Yellow -NoNewline

                    # Use Read-Host with -AsSecureString for secure input
                    $secureToken = Read-Host -AsSecureString

                    if ($secureToken.Length -eq 0) {
                        Write-Host ""
                        Write-Host "[提示] 未输入 Token，操作已取消" -ForegroundColor Yellow
                    } else {
                        # Convert SecureString to plain text for passing to executable
                        $plainToken = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken))

                        if ([string]::IsNullOrWhiteSpace($plainToken)) {
                            Write-Host ""
                            Write-Host "[提示] 未输入 Token，操作已取消" -ForegroundColor Yellow
                        } else {
                            Write-Host ""
                            Write-Host "正在设置 Token..." -ForegroundColor Gray
                            Write-Host "----------------------------------------" -ForegroundColor DarkGray
                            try {
                                # Use direct process execution with proper input handling
                                $processInfo = New-Object System.Diagnostics.ProcessStartInfo
                                $processInfo.FileName = $ExePath
                                $processInfo.Arguments = "config set-token"
                                $processInfo.UseShellExecute = $false
                                $processInfo.RedirectStandardInput = $true
                                $processInfo.RedirectStandardOutput = $true
                                $processInfo.RedirectStandardError = $true
                                $processInfo.StandardOutputEncoding = [System.Text.Encoding]::UTF8
                                $processInfo.StandardErrorEncoding = [System.Text.Encoding]::UTF8

                                $process = New-Object System.Diagnostics.Process
                                $process.StartInfo = $processInfo
                                $process.Start() | Out-Null

                                # Send responses: No (don't hide input), then the token, then enter
                                $process.StandardInput.WriteLine("N")  # Don't hide input
                                Start-Sleep -Milliseconds 500  # Wait a bit
                                $process.StandardInput.WriteLine($plainToken)  # Send the token
                                $process.StandardInput.Close()

                                $output = $process.StandardOutput.ReadToEnd()
                                $error = $process.StandardError.ReadToEnd()
                                $process.WaitForExit()

                                if ($output) {
                                    Write-Host $output
                                }
                                if ($error) {
                                    Write-Host $error -ForegroundColor Red
                                }

                                if ($process.ExitCode -eq 0) {
                                    Write-Host ""
                                    Write-Host "[成功] Token 已成功设置" -ForegroundColor Green
                                } else {
                                    Write-Host ""
                                    Write-Host "[错误] Token 设置失败，退出代码：$($process.ExitCode)" -ForegroundColor Red
                                }
                            } catch {
                                Write-Host "[错误] 设置 Token 失败：$($_.Exception.Message)" -ForegroundColor Red
                            } finally {
                                # Clear the plain text token from memory
                                $plainToken = $null
                            }
                            Write-Host "----------------------------------------" -ForegroundColor DarkGray
                        }
                    }
                }
                "2" {
                    Write-Host ""
                    Write-Host "正在获取当前配置..." -ForegroundColor Gray
                    Write-Host "----------------------------------------" -ForegroundColor DarkGray
                    try {
                        & $ExePath config show
                    } catch {
                        Write-Host "[错误] 获取配置失败：$($_.Exception.Message)" -ForegroundColor Red
                    }
                    Write-Host "----------------------------------------" -ForegroundColor DarkGray
                }
                "0" {
                    Write-Host ""
                    Write-Host "[信息] 返回主菜单" -ForegroundColor Green
                }
                default {
                    Write-Host ""
                    Write-Host "[错误] 无效选择：$tokenChoice" -ForegroundColor Red
                }
            }
            Write-Host ""
            Read-Host "按回车键继续"
            Clear-Host
            continue
        }

        "version" {
            Clear-Host
            Write-Host ""
            Write-Host "获取版本信息中..." -ForegroundColor Gray
            Write-Host "----------------------------------------" -ForegroundColor DarkGray
            try {
                & $ExePath --version
            } catch {
                Write-Host "[错误] 获取版本信息失败：$($_.Exception.Message)" -ForegroundColor Red
            }
            Write-Host "----------------------------------------" -ForegroundColor DarkGray
            Write-Host ""
            Read-Host "按回车键继续"
            Clear-Host
            continue
        }
    }

    # Handle main program commands
    if ($cmd -in $validCommands) {
        Clear-Host
        Write-Host ""

        # Find the option description for display
        $optionDesc = ($menuOptions | Where-Object { $_.Command -eq $cmd }).Description
        if (-not $optionDesc) {
            $optionDesc = $cmd  # Fallback to command name
        }

        Write-Host "执行命令：$optionDesc" -ForegroundColor Green
        Write-Host "正在执行：packy-usage-monitor.exe $cmd" -ForegroundColor Gray
        Write-Host "========================================" -ForegroundColor DarkCyan

        try {
            # Special handling for interactive commands (watch, tray)
            if ($cmd -in @("watch", "tray")) {
                Write-Host ""
                Write-Host "[提示] 这是一个持续运行的命令" -ForegroundColor Cyan
                Write-Host "[提示] 按 Ctrl+C 可以停止并返回菜单" -ForegroundColor Cyan
                Write-Host ""

                # For interactive commands, use Start-Process without capture
                $process = Start-Process -FilePath $ExePath -ArgumentList $cmd -NoNewWindow -PassThru -Wait

                if ($process.ExitCode -ne 0 -and $process.ExitCode -ne -1073741510) {  # -1073741510 is Ctrl+C
                    Write-Host ""
                    Write-Host "[警告] 命令已停止，退出代码：$($process.ExitCode)" -ForegroundColor Yellow
                } else {
                    Write-Host ""
                    Write-Host "[信息] 命令已停止" -ForegroundColor Green
                }
            } else {
                # For non-interactive commands, use the original method
                $processInfo = New-Object System.Diagnostics.ProcessStartInfo
                $processInfo.FileName = $ExePath
                $processInfo.Arguments = $cmd
                $processInfo.UseShellExecute = $false
                $processInfo.RedirectStandardOutput = $true
                $processInfo.RedirectStandardError = $true
                $processInfo.StandardOutputEncoding = [System.Text.Encoding]::UTF8
                $processInfo.StandardErrorEncoding = [System.Text.Encoding]::UTF8

                $process = New-Object System.Diagnostics.Process
                $process.StartInfo = $processInfo
                $process.Start() | Out-Null

                $output = $process.StandardOutput.ReadToEnd()
                $error = $process.StandardError.ReadToEnd()
                $process.WaitForExit()

                if ($output) {
                    Write-Host $output
                }
                if ($error) {
                    Write-Host $error -ForegroundColor Red
                }

                if ($process.ExitCode -ne 0) {
                    Write-Host ""
                    Write-Host "[警告] 命令执行完成，退出代码：$($process.ExitCode)" -ForegroundColor Yellow
                } else {
                    Write-Host ""
                    Write-Host "[成功] 命令执行完成" -ForegroundColor Green
                }
            }
        } catch {
            Write-Host "[错误] 命令执行失败：$($_.Exception.Message)" -ForegroundColor Red
        }

        Write-Host "========================================" -ForegroundColor DarkCyan
        Write-Host ""
        Read-Host "按回车键返回主菜单"
        Clear-Host
    } else {
        Write-Host ""
        Write-Host "[错误] 未知命令：$cmd" -ForegroundColor Red
        Write-Host "[提示] 请输入数字 0-12 或有效的命令名称" -ForegroundColor Yellow
        Start-Sleep -Seconds 2
        Clear-Host
    }
}
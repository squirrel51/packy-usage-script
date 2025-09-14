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
    @{ Number = 8; Command = "version"; Description = "显示版本信息" },
    @{ Number = 9; Command = "help"; Description = "显示帮助信息" },
    @{ Number = 0; Command = "exit"; Description = "退出程序" }
)

$validCommands = @("check", "config", "diagnose", "perf-test", "status", "tray", "watch")

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
    Write-Host "请输入选择 [0-9]: " -ForegroundColor Yellow -NoNewline
    $userInput = Read-Host

    # Handle empty input
    if ([string]::IsNullOrWhiteSpace($userInput)) {
        Write-Host ""
        Write-Host "[提示] 请输入有效的数字选项 (0-9)" -ForegroundColor Yellow
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
            Write-Host "[错误] 无效选择：$userInput (请输入 0-9)" -ForegroundColor Red
            Start-Sleep -Seconds 2
            Clear-Host
            continue
        }
    } else {
        # Handle direct command input (backward compatibility)
        $cmd = $userInput.ToLower()
        if (-not ($cmd -in @("check", "config", "diagnose", "perf-test", "status", "tray", "watch", "version", "help", "exit", "quit", "q"))) {
            Write-Host ""
            Write-Host "[错误] 无效选择：$userInput" -ForegroundColor Red
            Write-Host "[提示] 请输入数字 0-9 或直接输入命令名称" -ForegroundColor Yellow
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
            foreach ($option in $menuOptions[0..7]) {  # Exclude help and exit from detailed list
                Write-Host "  $($option.Command.PadRight(12)) - $($option.Description)" -ForegroundColor White
            }
            Write-Host ""
            Write-Host "[提示] 您可以输入数字 [0-9] 或直接输入命令名称" -ForegroundColor Cyan
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
            # Try to execute with proper encoding handling
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
        Write-Host "[提示] 请输入数字 0-9 或有效的命令名称" -ForegroundColor Yellow
        Start-Sleep -Seconds 2
        Clear-Host
    }
}
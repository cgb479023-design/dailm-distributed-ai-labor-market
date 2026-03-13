@echo off
setlocal enabledelayedexpansion
title PreBid Master AI - 企业级全栈交付引擎

:: 设置颜色：绿字黑底
color 0A

echo ================================================================
echo    PreBid Master AI (Distributed AI Labor Market)
echo          企业级售前与投标一体化平台 - 交付中心
echo ================================================================
echo.

:: 1. 环境自检模块
echo [1/5] 🔍 正在进行系统环境自检...
where python >nul 2>nul
if %errorlevel% neq 0 (echo ❌ 错误: 未检测到 Python，请先安装！ && pause && exit /b)

where node >nul 2>nul
if %errorlevel% neq 0 (echo ❌ 错误: 未检测到 Node.js，请先安装！ && pause && exit /b)

echo ✅ 环境检查通过：Python ^& Node.js 已就绪。
echo.

:: 2. 依赖自动补全
echo [2/5] 📦 正在同步跨语言依赖库...
echo --- 正在更新 Python 算力层...
pip install -r requirements.txt --quiet
echo --- 正在更新 Node.js 渲染层...
call npm install --loglevel error
echo ✅ 依赖同步完成。
echo.

:: 3. 执行 AI 核心审计流
echo [3/5] 🤖 正在启动分布式 AI 劳动力市场 (DAILM)...
echo 🚀 正在解析标书并生成 9:16 高仿真内容...
:: 运行主工作流脚本
python prebid_master_flow.py
if %errorlevel% neq 0 (echo ❌ AI 生成阶段出错，请检查 strike_log.txt && pause && exit /b)
echo ✅ AI 内容生成成功，已导出至 EXPANSION_RESULT.txt。
echo.

:: 4. 自动化 UI 封装与离线打包
echo [4/5] 🏗️ 正在执行前端工程化封装...
:: 调用之前编写的 Node.js 打包逻辑
node scripts/package_offline.js "HAINAN_BID_FINAL"
if %errorlevel% neq 0 (echo ❌ 离线包打包失败！ && pause && exit /b)
echo ✅ UI 渲染与 ZIP 归档完成。
echo.

:: 5. 交互式交付
echo [5/5] 🏁 交付准备就绪！
echo ================================================================
echo [A] 立即打开 9:16 高仿真预览工作台 (Workbench)
echo [B] 打开生成的 U 盘离线演示包 (.zip)
echo [C] 退出
echo ================================================================
set /p choice="请选择操作 (A/B/C): "

if /i "%choice%"=="A" (
    echo 正在启动预览...
    start prebid_workbench.html
)
if /i "%choice%"=="B" (
    echo 正在打开输出目录...
    start explorer.exe .
)

echo.
echo ✨ 感谢使用 PreBid Master AI。所有任务已 100%% 完成！
pause

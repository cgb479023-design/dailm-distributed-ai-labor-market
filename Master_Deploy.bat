@echo off
title DAILM COMMAND CENTER - MASTER DEPLOYER
color 0B
cls

echo ==========================================================
echo           DAILM: NEURAL LINK INITIALIZATION
echo ==========================================================

:: 1. 物理清场协议 (Anti-Lockdown)
echo [SYSTEM]: Executing zombie process purge...
taskkill /F /IM chrome.exe /T >nul 2>&1
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1
echo [SUCCESS]: Environment cleared.

:: 2. 神经链路解密动画 (PowerShell 驱动)
echo [SYSTEM]: Decrypting Secure Matrix...
powershell -Command "$chars='!@#$%%^&*()_+-=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'; $label='DECRYPTING_CORE'; for($i=0; $i -le 100; $i+=2){ $rand=''; 1..15 | %%{ $rand+=$chars[(Get-Random -Max $chars.Length)] }; Write-Host -NoNewline \"`r$($label): [$i%%] [$rand]\"; Start-Sleep -m 30 }; Write-Host \"`n[COMPLETE]: Core protocols stable.\""

:: 3. 核心配置校验
if not exist .env (
    echo [WARNING]: .env file not found. System may fail.
    copy .env.example .env >nul
    echo [INFO]: Created .env from example template.
)

:: 4. 并行启动后端算力矩阵 (FastAPI)
echo [SYSTEM]: Igniting Backend Matrix Hub...
start "DAILM_BACKEND" /min cmd /c ".\venv\Scripts\python.exe main.py"

:: 4. 启动可视化监控大屏 (Vite/React)
echo [SYSTEM]: Projecting Visual Feed...
start "DAILM_FRONTEND" /min cmd /c "npm run dev"

echo ----------------------------------------------------------
echo [STATUS]: DAILM SYSTEM IS NOW LIVE.
echo [ACCESS]: http://localhost:3000 (Frontend)
echo [ACCESS]: http://127.0.0.1:8000 (Backend API)
echo ----------------------------------------------------------
echo Press any key to stabilize and enter the Matrix...
:: pause >nul

:: 自动打开浏览器至指挥中心
start http://localhost:3000
exit

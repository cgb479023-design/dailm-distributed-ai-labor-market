import asyncio
import os
import random
import subprocess
from playwright.async_api import async_playwright
from loguru import logger

class BrowserEngine:
    def __init__(self, user_data_path="./.playwright_chrome_profile"):
        self.user_data_path = os.path.abspath(user_data_path)
        self.playwright = None
        self.browser_context = None

    async def _force_kill_zombies(self):
        """物理级清理：强制杀掉所有锁死目录的 Chrome 进程"""
        logger.warning("[SYSTEM]: 执行僵尸进程清理协议...")
        if os.name == 'nt': # Windows
            subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], capture_output=True)
        else:
            subprocess.run(["pkill", "-9", "chrome"], capture_output=True)

    def _shred_locks(self):
        """粉碎锁定文件：移除阻止持久化上下文启动的 SingletonLock"""
        lock_files = [
            os.path.join(self.user_data_path, "SingletonLock"),
            os.path.join(self.user_data_path, "lockfile")
        ]
        for lock in lock_files:
            if os.path.exists(lock):
                try:
                    os.remove(lock)
                    logger.info(f"[SYSTEM]: 已粉碎物理锁: {lock}")
                except Exception as e:
                    logger.error(f"[SYSTEM]: 锁粉碎失败: {e}")

    async def start(self, headless=False):
        """点火程序：具备自愈能力的引擎启动逻辑"""
        # 1. 环境准备
        await self._force_kill_zombies()
        self._shred_locks()

        if not os.path.exists(self.user_data_path):
            os.makedirs(self.user_data_path)

        self.playwright = await async_playwright().start()

        # 2. 深度伪装启动参数
        try:
            logger.info(f"[ENGINE]: 正在载入持久化矩阵: {self.user_data_path}")
            self.browser_context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_path,
                headless=headless,
                args=[
                    "--disable-blink-features=AutomationControlled", # 核心：隐藏 Playwright 特征
                    "--no-sandbox",
                    "--disable-infobars",
                    "--disable-dev-shm-usage",
                    "--start-maximized"
                ],
                ignore_default_args=["--enable-automation"], # 关键：移除“受自动控制”标题
                viewport=None
            )


            # 3. 注入防检测脚本
            page = self.browser_context.pages[0] if self.browser_context.pages else await self.browser_context.new_page()
            await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            logger.success("[ENGINE]: 神经链路已建立，环境自愈成功。")
            return self.browser_context

        except Exception as e:
            logger.critical(f"[ENGINE]: 启动失败，触发紧急泄压: {e}")
            await self.stop()
            raise e

    async def get_page(self, name):
        """路由寻址：快速定位或创建目标页面"""
        for page in self.browser_context.pages:
            if name in page.url:
                try:
                    # Attempt to reload the page to ensure it's active and responsive
                    await page.reload(wait_until="domcontentloaded")
                    logger.info(f"[ENGINE]: Re-activated existing page for {name}.")
                    return page
                except Exception as e:
                    logger.warning(f"[ENGINE]: Page {page.url} failed to reload ({e}). Closing and creating new page.")
                    # If reload fails, close the page and let a new one be created
                    await page.close()
                    # Continue to try other pages or create a new one outside the loop
                    continue
        # If no suitable existing page was found or successfully re-activated, create a new one
        new_page = await self.browser_context.new_page()
        logger.info(f"[ENGINE]: Created new page for {name}.")
        return new_page

    async def human_delay(self, min_s=1, max_s=3):
        """模拟真人随机延迟"""
        await asyncio.sleep(random.uniform(min_s, max_s))

    async def stop(self):
        """安全停机协议"""
        if self.browser_context:
            await self.browser_context.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("[ENGINE]: 引擎已安全离线。")

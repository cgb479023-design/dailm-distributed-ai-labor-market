import asyncio
import os
import random
import subprocess
from playwright.async_api import async_playwright
from loguru import logger

class BrowserEngine:
    def __init__(self, user_data_path="./.playwright_chrome_profile"):
        # 进化：支持原子级隔离。如果路径已存在且被锁定，将自动附加 PID 开启新位面。
        self.base_user_data_path = os.path.abspath(user_data_path)
        self.user_data_path = self.base_user_data_path
        self.playwright = None
        self.browser_context = None
        self._is_isolating = False

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

    async def start(self, headless=False, isolate=True):
        """点火程序：具备自愈能力的引擎启动逻辑 (支持原子级隔离)"""
        # 1. 环境准备
        if isolate:
            # 战术隔离：每个进程使用独立的 Profile 分片
            self.user_data_path = f"{self.base_user_data_path}_{os.getpid()}"
            self._is_isolating = True

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

    async def human_type(self, page, selector: str, text: str):
        """模拟人类非均匀打字速度"""
        await page.wait_for_selector(selector)
        for char in text:
            await page.type(selector, char, delay=random.randint(50, 250))
            # 模拟打字过程中的微小停顿
            if random.random() > 0.95:
                await asyncio.sleep(random.uniform(0.5, 1.5))

    async def human_scroll(self, page):
        """模拟人类随机滚动页面"""
        distance = random.randint(300, 700)
        await page.mouse.wheel(0, distance)
        await asyncio.sleep(random.uniform(1, 2))

    async def upload_rfp_attachment(self, page, file_path: str, upload_selector: str = "input[type='file']"):
        """
        进化版：模拟拖拽或文件选择器上传
        适用平台：ChatGPT, Claude, Kimi
        """
        if not os.path.exists(file_path):
            logger.error(f"[ENGINE]: Upload failed, file not found: {file_path}")
            return False
            
        try:
            # 等待上传按钮或图标出现
            # 注意：实际平台的回形针 selector 可能不同，这里按通用处理
            async with page.expect_file_chooser(timeout=10000) as fc_info:
                # 尝试点击通用上传图标 (button 包含 svg 或具有 class upload-icon)
                await page.click(upload_selector) 
            
            file_chooser = await fc_info.value
            await file_chooser.set_files(file_path)
            
            # 这里是通用等待，实际应用中可能需要根据特定平台的 DOM 元素等待
            logger.info(f"[ENGINE]: Initiated file upload for {file_path}")
            await asyncio.sleep(3) # Give it time to start
            return True
        except Exception as e:
            logger.error(f"[ENGINE]: Upload attachment failed: {e}")
            return False

    async def human_delay(self, min_s=1, max_s=3):
        """模拟真人随机延迟"""
        await asyncio.sleep(random.uniform(min_s, max_s))

    async def stop(self):
        """安全停机协议 (包含孤儿分片清理)"""
        try:
            if self.browser_context:
                await self.browser_context.close()
            if self.playwright:
                await self.playwright.stop()
            
            # 如果是隔离模式，任务完成后尝试清理分片以减少熵增
            if self._is_isolating and os.path.exists(self.user_data_path):
                # 给系统一点时间释放句柄
                await asyncio.sleep(1)
                try:
                    import shutil
                    shutil.rmtree(self.user_data_path, ignore_errors=True)
                    logger.info(f"[ENGINE]: 已回收原子分片: {self.user_data_path}")
                except:
                    pass
            
            logger.info("[ENGINE]: 引擎已安全离线。")
        except Exception as e:
            logger.warning(f"[ENGINE]: 停机阶段异常: {e}")

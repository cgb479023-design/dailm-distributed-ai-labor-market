# DAILM (Distributed AI Labor Market)

分布式 AI 算力调度系统。

## 核心功能
- **Persistent Context**: 使用 Playwright 持久化 Session，绕过登录验证。
- **Model Matrix**: 智能路由任务到最合适的 Web AI 节点。
- **DOM Slimming**: 语义化压缩网页 DOM，提升上下文效率。
- **JSON Handshake**: 标准化 Agent 通信协议。

## 快速开始
1. 安装依赖: `pip install -r requirements.txt`
2. 安装浏览器: `playwright install chromium`
3. 运行系统: `python main.py --url "https://news.ycombinator.com"`

## 目录结构
- `core/`: 浏览器引擎与 DOM 瘦身脚本。
- `agents/`: 调度矩阵与路由逻辑。
- `tasks/`: 预定义工作流。
- `adapters/`: 各 AI 平台的 Web 适配器（需根据 UI 变化持续维护）。

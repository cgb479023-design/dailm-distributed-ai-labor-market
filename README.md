# PreBid Master AI (Powered by DAILM)

PreBid Master AI 是一套企业级售前投标一体化平台，旨在通过分布式 AI 劳动力调度技术实现标书自动化审计与高保真 Demo 生成。

> [!TIP]
> 详细的技术架构、实现逻辑与交付规范请参阅 [WHITE_PAPER.md](file:///e:/dailm---distributed-ai-labor-market/WHITE_PAPER.md)。

## 🚀 快速交付 (Master Deploy)
系统已实现一键式交付流程：
- **一键部署:** 运行根目录下的 `Master_Deploy.bat`。该脚本将自动调度 Python 进行 AI 扩充，并使用 Node.js 进行工程化封装，最后启动预览工作台。
- **全自动流水线:** 执行 `python prebid_master_flow.py` 开启从 RFP 解析到 UI 合成的端到端任务。

## 核心架构：DAILM 引擎
分布式 AI 劳动力市场 (Distributed AI Labor Market) 是本系统的底层算力支撑：
- **Persistent Context**: 使用 Playwright 持久化 Session，确保长任务连续性。
- **Model Matrix**: 智能路由任务到最合适的 Web AI 节点。
- **JSON Handshake**: 标准化 Agent 间的通信协议，确保 100% 可解析。

## 功能模块
1. **深度标书审计**: `audit_rfp_deep.py` 提取关键红线条款。
2. **9:16 高仿真沙箱**: 基于 Vue 3 + TailwindCSS 的行业风格秒切工作台。
3. **演示教练**: 自动化话术与组件交互的毫秒级同步。

## 目录结构
- `prebid_master_flow.py`: PreBid Master 核心流水线控。
- `audit_rfp_deep.py`: 标书深度审计引擎。
- `Master_Deploy.bat`: 一键交付与集成脚本。
- `agents/`: 包含分布式 AI 劳动力 (DAILM) 的各种职能 Agent。
- `prebid_style_gallery/`: 行业视觉风格预设。
- `dist_package/`: 离线化部署的构建输出。

---
*Inspired by cgb479023-design | Empowering Enterprise Pre-sales with Distributed AI.*

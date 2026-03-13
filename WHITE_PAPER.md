# PreBid Master AI 开发与集成技术白皮书 (Final)

## 1. 项目概述与愿景
PreBid Master AI 旨在通过分布式 AI 劳动力调度技术，解决企业在售前演示准备周期长、标书审计风险大、演示缺乏针对性等核心痛点。

**核心目标：**
- **2小时**生成高保真 Demo
- **24小时**完成合规标书
- 实现 **100% 红线风控**

**系统定位：** 企业级售前投标一体化平台。

## 2. 总体架构设计
系统采用“分布式底座 + 场景化工作台”的解耦架构。

### 2.1 算力底座：DAILM 引擎
基于 DAILM (Distributed AI Labor Market) 的核心能力，系统实现了以下底层逻辑：
- **Model Matrix:** 智能路由任务至不同的 Web AI 节点。
- **Persistent Context:** 通过 Playwright 持久化 Session，确保复杂长任务的连续性。
- **JSON Handshake:** 定义了 Agent 间的通信协议，确保输出 100% 可解析。

### 2.2 数据流向模型
系统的端到端处理逻辑遵循以下公式：
$$Result_{Final} = \sum (Audit(RFP) \times Labor(Expansion)) \xrightarrow{Synthesis} UI_{9:16}$$

## 3. 核心功能模块实现手册

### 3.1 深度标书审计 (Audit RFP Deep)
- **实现逻辑:** 运行 `audit_rfp_deep.py` 解析原文。
- **关键技术:** 采用正则与 LLM 混合识别模式，强制提取带有 ★ 或 * 的条款，并生成结构化的 `compliance_matrix.json`。

### 3.2 9:16 高仿真沙箱 (Sandbox Evolution)
- **技术栈:** Vue 3 + TailwindCSS + Iframe。
- **视觉规范:** 强制锁定 9:16 画布，通过 CSS Variables 实现“政务、工业、SaaS”等 8 大行业风格秒切。
- **安全性:** Iframe 沙箱模式隔离了 AI 生成的业务脚本与平台管理层。

### 3.3 演示教练 (Presentation Coach)
- **自动化话术:** 根据页面组件复杂度动态分配演示时长。
- **同步机制:** 实现话术时间轴与 Demo 交互组件的毫秒级同步，确保售前人员“讲在点上”。

## 4. 交付与集成工程

### 4.1 离线化部署策略
为了满足“无网络现场演示”的需求，系统集成了 Node.js 打包引擎：
- **静态化:** 所有的业务逻辑被转化为 `schema.json`。
- **零依赖:** 离线 ZIP 包仅包含静态 HTML/JS，解压即用。

### 4.2 一键部署流程 (Master Deploy)
通过根目录下的 `Master_Deploy.bat` 脚本，实现了跨语言环境的统一调度：
- **Python 层:** 完成标书解析与 AI 扩充。
- **Node.js 层:** 执行工程化封装与压缩。
- **UI 层:** 启动预览工作台。

## 5. 质量保证与合规性
- **双屏审计:** 前端提供 PDF 原文与解析结果的实时对照。
- **风险报告:** 自动生成 `validation_report.md`，针对 21 项常见的废标红线进行自动化扫描。

## 6. 结论
PreBid Master AI 已成功从一系列断开的脚本进化为一套成熟、可交付的企业级资产。通过将 cgb479023-design 的分布式 AI 调度能力与严谨的售前业务流相结合，该平台在效率与合规性上均达到了行业领先水平。

---
**项目当前状态确认**
- **代码仓库:** `dailm-distributed-ai-labor-market`
- **最新提交:** `feat: complete prebid master e2e pipeline and UI synthesis integration`
- **全栈就绪:** ✅ 后端算力 ✅ 前端沙箱 ✅ 自动化打包 ✅ 一键部署

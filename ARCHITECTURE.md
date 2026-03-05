# 架构分析报告：4+1 协同模型

> 生成时间：2026-03-04

---

## 一、现状诊断（你现在有什么）

| 模块 | 现状 | 完成度 |
|---|---|---|
| **Scout Agent** | `scout_agent.py` 已实现自愈爬虫框架，含 LLM Healing Loop | ✅ 约60% |
| **Analyst Agent** | `analyst_service.py` 仅为纯算法函数，无 LLM 加持，无 Agent 化 | ⚠️ 约30% |
| **Linguistic Agent** | `linguistic_agent.py` 实现了 LLM 文案生成，逻辑清晰 | ✅ 约65% |
| **Creative Agent** | `creative_agent.py` 实现了 Prompt 增强，但图像生成是 Mock | ⚠️ 约40% |
| **Orchestrator (1)** | **完全缺失** —— 任务调度靠 `TaskManager` 硬编码，无意图解析 | ❌ 0% |
| **WebSocket 实时推送** | `websocket_manager.py` 已实现，但只在 SEO/Media 任务中用到 | ✅ 基础完成 |
| **数据库** | SQLite（通过 SQLAlchemy ORM），有任务状态、配置、日志模型 | ✅ 完整 |
| **前端 Views** | 有 MarketRadar、TaskCenter、CreativeStudio、Analysis 等，各自独立，缺乏统一任务指挥台 | ⚠️ 缺乏整合 |

---

## 二、目标架构（4+1 完整体）

### 核心思路：以 Orchestrator 为中枢，以 Mission 为数据单元

```
用户输入一句话
     ↓
🧠 Orchestrator Agent (Gemini/DeepSeek)
   - 意图解析 → 结构化工单
   - 任务调度 → 逐步激活专业 Agent
   - 质量守门 → 校验结果, 决定是否重跑
     ↓             ↓             ↓             ↓
🔍 Scout      📊 Analyst    ✍️ Linguistic  🎨 Creative
  自愈爬虫      UnifiedScore    俄语SEO文案    Flux.1渲染图
  VK+Ozon       热度归一化      RAG检索        俄式审美Prompt
     ↓             ↓             ↓             ↓
              🔌 WebSocket Manager
              实时日志广播 → 前端
```

---

## 三、后端改造方案

### P0 — 新建 OrchestratorAgent（最高优先级）

**文件**：`backend/agents/orchestrator_agent.py`

```python
class OrchestratorAgent(BaseAgent):
    # 1. 意图解析：自然语言 → 结构化工单 MissionPlan
    async def parse_intent(self, user_input: str) -> MissionPlan: ...

    # 2. 任务调度：按顺序激活 Scout → Analyst → Linguistic → Creative
    async def execute(self, mission_plan: MissionPlan) -> None: ...

    # 3. 质量守门：校验 Analyst 结果，不合理则要求重跑
    async def quality_check(self, result: dict) -> bool: ...
```

### P0 — 新建 Mission 数据模型

**文件**：`backend/models/mission.py`

```python
class Mission(Base):
    __tablename__ = "missions"
    id            # 主键
    user_input    # 原始用户输入
    status        # PENDING / RUNNING / DONE / FAILED
    scout_result  # JSON
    analyst_result
    linguistic_result
    creative_result
    created_at, updated_at
```

**新增 API 端点**：
- `POST /mission/run` — 接收用户意图，启动 Orchestrator
- `GET /mission/{id}` — 查询单个任务结果
- `GET /mission/history` — 历史任务列表

### P1 — 强化 WebSocket（按 mission_id 隔离）

```python
# 改造前：广播给所有连接
await ws_manager.broadcast(data)

# 改造后：按任务隔离推送
await ws_manager.broadcast_to(mission_id, {
    "type": "agent_log",
    "agent": "Scout",
    "step": "crawling_vk",
    "message": "正在抓取VK热议话题...",
    "progress": 0.2
})
```

### P1 — AnalystAgent 升级（LLM 赋能）

```python
class AnalystAgent(BaseAgent):
    # 1. 调用算法算分（复用现有 AnalystService）
    # 2. 用 LLM 解读数据："搜索量高、竞品少 → 蓝海品类"
    # 3. 输出结构化分析报告 + 关键词云数据
    async def run(self, scout_data: dict) -> AnalystReport: ...
```

---

## 四、前端改造方案

### 新增核心页面：`MissionControl.vue`

这是统一**任务指挥台**，整合所有 Agent 输出：

```
┌────────────────────────────────────────────────────┐
│ 🎯 任务指挥台                                       │
│ [输入框] 帮我分析VK上热议的智能喂食器...    [启动]  │
├────────────────────────────────────────────────────┤
│ 🔄 任务流水线状态                                   │
│  Orchestrator → Scout → Analyst → Linguistic → Creative │
│  [●完成]       [●运行中] [○等待]   [○等待]    [○等待] │
├──────────────────┬─────────────────────────────────┤
│ 📜 实时日志流    │ 📊 结果聚合面板                  │
│                  │                                  │
│ [Scout] 抓取    │  热词云图 / SEO文案 / 渲染图      │
│ VK数据...       │  (随任务完成逐步渲染)              │
│ [Analyst] 计    │                                  │
│ 算热度评分...   │                                  │
└──────────────────┴─────────────────────────────────┘
```

### 新增 Pinia Store：`missionStore.ts`

```typescript
export const useMissionStore = defineStore('mission', {
  state: () => ({
    currentMission: null,
    logs: [],
    agentStatus: { scout: 'idle', analyst: 'idle', linguistic: 'idle', creative: 'idle' }
  }),
  actions: {
    async startMission(userInput: string) {
      // POST /mission/run → 获取 mission_id
      // 建立 WebSocket 连接，订阅该 mission_id 的实时日志
    }
  }
})
```

### 前端路由追加

```typescript
// router/index.ts 追加
{ path: '/mission', component: MissionControl, meta: { requiresAuth: true } }
```

### 侧边栏追加入口

在 `Sidebar.vue` 添加"任务指挥台"导航入口，作为首要功能入口。

---

## 五、落地优先级

| 优先级 | 模块 | 预估工作量 | 效果 |
|---|---|---|---|
| **P0** | `OrchestratorAgent` + `Mission` 模型 + API | 2天 | 系统有了灵魂 |
| **P0** | `MissionControl.vue` + `missionStore.ts` | 1.5天 | 前端看到完整流程 |
| **P1** | WebSocket 按 mission_id 隔离 | 0.5天 | 实时日志更准确 |
| **P1** | `AnalystAgent` LLM 升级 | 1天 | 数据有了"智慧" |
| **P2** | 真实图像生成（Flux/Replicate API 接入） | 1天 | 视觉产出闭环 |
| **P2** | Scout 多平台适配（VK、YouTube） | 2天 | 数据源真实化 |

---

## 六、关键结论

**现在最缺的两件事**：
1. **Orchestrator（灵魂）** — 没有总控，4个 Agent 各自为战，无法形成协同
2. **MissionControl 前端页面** — 没有统一入口，用户体验割裂

其他 4 个 Agent 的骨架已经就位，只需补强 LLM 调用路径和 Agent 间数据传递管道。

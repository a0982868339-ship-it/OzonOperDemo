import { defineStore } from "pinia"
import { ref, computed } from "vue"

export interface AgentLog {
  id: string
  agent: string
  message: string
  timestamp: number
  type: "info" | "success" | "error"
}

export interface AgentStatus {
  name: string
  role: string
  status: "idle" | "active" | "completed" | "failed"
  icon: string // emoji or icon name
  color: string // tailwind color class
}

export const useMissionStore = defineStore("mission", () => {
  const isMissionRunning = ref(false)
  const socket = ref<WebSocket | null>(null)
  const logs = ref<AgentLog[]>([])
  
  // 5 Agents
  const agents = ref<AgentStatus[]>([
    { name: "市场侦察", role: "数据分析", status: "idle", icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" /></svg>`, color: "text-blue-400" },
    { name: "策略分析", role: "策略规划", status: "idle", icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" /></svg>`, color: "text-indigo-400" },
    { name: "语言专家", role: "文案撰写", status: "idle", icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" /></svg>`, color: "text-emerald-400" },
    { name: "创意总监", role: "视觉设计", status: "idle", icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M9.53 16.122a3 3 0 00-5.78 1.128 2.25 2.25 0 01-2.4 2.245 4.5 4.5 0 008.4-2.245c0-.399-.078-.78-.22-1.128zm0 0a15.998 15.998 0 003.388-1.62m-5.043-.025a15.994 15.994 0 011.622-3.395m3.42 3.42a15.995 15.995 0 004.764-4.648l3.876-5.814a1.151 1.151 0 00-1.597-1.597L14.146 6.32a15.996 15.996 0 00-4.649 4.763m3.42 3.42a6.776 6.776 0 00-3.42-3.42" /></svg>`, color: "text-purple-400" },
    { name: "运营管家", role: "执行落地", status: "idle", icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M15.59 14.37a6 6 0 01-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 006.16-12.12A14.98 14.98 0 009.631 8.41m5.96 5.96a14.926 14.926 0 01-5.841 2.58m-.119-8.54a6 6 0 00-7.381 5.84h4.8m2.581-5.84a14.927 14.927 0 00-2.58 5.84m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 01-2.448-2.448 14.9 14.9 0 01.06-.312m-2.24 2.39a4.493 4.493 0 00-1.757 4.306 4.493 4.493 0 004.306-1.758M16.5 9a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z" /></svg>`, color: "text-orange-400" }
  ])

  const progress = computed(() => {
    const completed = agents.value.filter(a => a.status === "completed").length
    const active = agents.value.filter(a => a.status === "active").length
    // Simple logic: completed * 20 + active * 10
    return Math.min(100, (completed * 20) + (active * 10))
  })

  const connectWebSocket = () => {
    if (socket.value?.readyState === WebSocket.OPEN) return

    // Use current host/port but switch protocol
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:"
    const wsUrl = `${protocol}//${window.location.hostname}:8000/ws/mission/client-${Date.now()}`
    
    socket.value = new WebSocket(wsUrl)
    
    socket.value.onopen = () => {
      console.log("Mission Control: Connected")
      addLog("System", "Uplink established. Ready for mission.", "info")
    }
    
    socket.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handleServerMessage(data)
      } catch (e) {
        console.error("Failed to parse WS message", e)
      }
    }
    
    socket.value.onerror = (err) => {
      console.error("WS Error", err)
      addLog("System", "Connection error.", "error")
    }
  }

  const handleServerMessage = (data: any) => {
    // Map backend agent names to frontend names
    // Backend: Linguistic, Creative
    // Frontend: Linguistic Expert, Creative Director
    
    let agentName = data.agent || "System"
    if (agentName === "Linguistic") agentName = "语言专家"
    if (agentName === "Creative") agentName = "创意总监"
    if (agentName === "Scout") agentName = "市场侦察" // Future proofing

    if (data.type === "log") {
      updateAgentStatus(agentName, "active")
      addLog(agentName, data.message, "info")
    } else if (data.type === "completion") {
      updateAgentStatus(agentName, "completed")
      addLog(agentName, "任务执行完成。", "success")
    } else if (data.type === "error") {
      updateAgentStatus(agentName, "failed")
      addLog(agentName, `错误: ${data.message}`, "error")
    }
  }

  const updateAgentStatus = (name: string, status: AgentStatus["status"]) => {
    const agent = agents.value.find(a => a.name === name)
    if (agent) {
      agent.status = status
    }
  }

  const addLog = (agent: string, message: string, type: "info" | "success" | "error" = "info") => {
    logs.value.push({
      id: Math.random().toString(36).substring(7),
      agent,
      message,
      timestamp: Date.now(),
      type
    })
    // Keep log size manageable
    if (logs.value.length > 100) logs.value.shift()
  }

  const startMission = () => {
    isMissionRunning.value = true
    logs.value = []
    agents.value.forEach(a => a.status = "idle")
    addLog("System", "Mission sequence initiated...", "info")
    
    // Simulate initial scan (Market Scout)
    updateAgentStatus("Market Scout", "active")
    setTimeout(() => {
      addLog("Market Scout", "Scanning market trends...", "info")
      setTimeout(() => {
        updateAgentStatus("Market Scout", "completed")
        updateAgentStatus("Strategy Analyst", "active")
        addLog("Strategy Analyst", "Formulating growth strategy...", "info")
      }, 1500)
    }, 500)
  }

  const stopMission = () => {
    isMissionRunning.value = false
  }

  return {
    isMissionRunning,
    agents,
    logs,
    progress,
    connectWebSocket,
    startMission,
    stopMission,
    addLog
  }
})

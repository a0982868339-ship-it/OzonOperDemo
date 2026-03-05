import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

export type AgentName = 'scout' | 'analyst' | 'linguistic' | 'creative'
export type AgentStatus = 'idle' | 'running' | 'done' | 'failed' | 'skipped'
export type MissionMode = 'pipeline' | 'manual'

export interface LogEntry {
  ts: string
  agent: string
  message: string
  type: 'agent_log' | 'agent_status' | 'mission_status' | 'error' | 'completion'
}

export interface AgentConfig {
  use_scout: boolean
  use_analyst: boolean
  use_linguistic: boolean
  use_creative: boolean
}

export interface MissionResult {
  scout?: Record<string, any> | null
  analyst?: Record<string, any> | null
  linguistic?: Record<string, any> | null
  creative?: Record<string, any> | null
}

export const useMissionStore = defineStore('mission', () => {
  const currentMissionId = ref<number | null>(null)
  const missionStatus = ref<string>('idle')
  const mode = ref<MissionMode>('pipeline')
  const logs = ref<LogEntry[]>([])
  const agentStatus = reactive<Record<AgentName, AgentStatus>>({
    scout: 'idle',
    analyst: 'idle',
    linguistic: 'idle',
    creative: 'idle',
  })
  const results = reactive<MissionResult>({})

  let ws: WebSocket | null = null

  function resetState() {
    logs.value = []
    missionStatus.value = 'idle'
    agentStatus.scout = 'idle'
    agentStatus.analyst = 'idle'
    agentStatus.linguistic = 'idle'
    agentStatus.creative = 'idle'
    results.scout = null
    results.analyst = null
    results.linguistic = null
    results.creative = null
  }

  function connectWebSocket(missionId: number) {
    if (ws) ws.close()
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    ws = new WebSocket(`${protocol}://${window.location.hostname}:8001/mission/${missionId}/ws`)

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      const entry: LogEntry = {
        ts: new Date().toLocaleTimeString(),
        agent: data.agent || 'System',
        message: data.message || JSON.stringify(data),
        type: data.type,
      }
      logs.value.push(entry)

      if (data.type === 'agent_status' && data.agent && data.status) {
        agentStatus[data.agent as AgentName] = data.status
      }
      if (data.type === 'mission_status' && data.status) {
        missionStatus.value = data.status
      }
    }

    ws.onerror = () => {
      logs.value.push({ ts: new Date().toLocaleTimeString(), agent: 'System', message: 'WebSocket error', type: 'error' })
    }
  }

  // ── Full pipeline ────────────────────────────────────────────────────────
  async function startPipeline(userInput: string, title: string, agentConfig: AgentConfig) {
    resetState()
    missionStatus.value = 'starting'

    const res = await fetch('/mission/pipeline', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ user_input: userInput, title, agent_config: agentConfig }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Pipeline start failed')

    currentMissionId.value = data.mission_id
    missionStatus.value = 'running'
    connectWebSocket(data.mission_id)
    return data
  }

  // ── Create empty manual mission ─────────────────────────────────────────
  async function createManualMission(): Promise<number> {
    resetState()
    const res = await fetch('/mission/manual', {
      method: 'POST',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    })
    const data = await res.json()
    currentMissionId.value = data.mission_id
    connectWebSocket(data.mission_id)
    return data.mission_id
  }

  // ── Run single agent ────────────────────────────────────────────────────
  async function runSingleAgent(
    agentName: AgentName,
    overrideData?: Record<string, any>
  ) {
    if (!currentMissionId.value) throw new Error('No active mission')
    agentStatus[agentName] = 'running'

    const res = await fetch(`/mission/${currentMissionId.value}/run-${agentName}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ override_data: overrideData || null }),
    })
    if (!res.ok) {
      agentStatus[agentName] = 'failed'
      throw new Error('Agent run failed')
    }
  }

  // ── Poll mission result ─────────────────────────────────────────────────
  async function fetchMissionResult(missionId?: number) {
    const id = missionId || currentMissionId.value
    if (!id) return
    const res = await fetch(`/mission/${id}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    })
    const data = await res.json()
    results.scout      = data.scout_result
    results.analyst    = data.analyst_result
    results.linguistic = data.linguistic_result
    results.creative   = data.creative_result
    missionStatus.value = data.status
    Object.assign(agentStatus, data.agent_status)
    return data
  }

  function disconnect() {
    if (ws) { ws.close(); ws = null }
  }

  return {
    currentMissionId, missionStatus, mode, logs, agentStatus, results,
    startPipeline, createManualMission, runSingleAgent, fetchMissionResult, disconnect, resetState,
  }
})

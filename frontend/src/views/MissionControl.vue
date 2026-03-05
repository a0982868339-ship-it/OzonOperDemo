<script setup lang="ts">
import { ref, onUnmounted, watch, computed } from 'vue'
import AgentCard from '../components/AgentCard.vue'
import LiveLog from '../components/LiveLog.vue'
import ResultPanel from '../components/ResultPanel.vue'
import { useMissionStore, type AgentName } from '../stores/missionStore'

const store = useMissionStore()

// ── Form state ──────────────────────────────────────────────────────────────
const userInput  = ref('')
const missionTitle = ref('')
const mode       = ref<'pipeline' | 'manual'>('pipeline')
const agentConfig = ref({ use_scout: true, use_analyst: true, use_linguistic: true, use_creative: true })
const isLoading  = ref(false)
const errorMsg   = ref('')

const isMissionComplete = computed(() => store.missionStatus === 'done' || store.missionStatus === 'failed')

// ── Agent definitions ────────────────────────────────────────────────────────
const agents = [
  { name: 'scout'      as AgentName, label: 'Scout 侦探',     icon: '🔍' },
  { name: 'analyst'    as AgentName, label: 'Analyst 精算',   icon: '📊' },
  { name: 'linguistic' as AgentName, label: 'Linguistic 文案', icon: '✍️' },
  { name: 'creative'   as AgentName, label: 'Creative 创意',  icon: '🎨' },
]

// ── Actions ──────────────────────────────────────────────────────────────────
async function handleStart() {
  if (!userInput.value.trim()) { errorMsg.value = '请输入您的任务描述'; return }
  errorMsg.value = ''
  isLoading.value = true
  try {
    if (mode.value === 'pipeline') {
      await store.startPipeline(userInput.value, missionTitle.value || userInput.value, agentConfig.value)
    } else {
      await store.createManualMission()
    }
  } catch (e: any) {
    errorMsg.value = e.message || '启动失败'
  } finally {
    isLoading.value = false
  }
}

async function handleAgentRun(agentName: AgentName, overrideData?: Record<string, any>) {
  try {
    await store.runSingleAgent(agentName, overrideData)
  } catch (e: any) {
    errorMsg.value = e.message || '执行失败'
  }
}

// Auto-fetch results when done
watch(() => store.missionStatus, async (val) => {
  if (val === 'done') await store.fetchMissionResult()
})

// Poll for partial results while running
let pollTimer: ReturnType<typeof setInterval> | null = null
watch(() => store.missionStatus, (val) => {
  if (val === 'running') {
    pollTimer = setInterval(() => store.fetchMissionResult(), 3000)
  } else {
    if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
  }
})

onUnmounted(() => {
  store.disconnect()
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-[#0f111a] p-6 font-sans flex gap-6 h-[calc(100vh-2rem)]">
    
    <!-- Left Column: Input Configuration & Control (1/3 width) -->
    <div class="w-1/3 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col overflow-hidden">
      <!-- Header -->
      <div class="p-6 border-b border-slate-100 dark:border-slate-700">
        <h2 class="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <span class="w-2 h-6 bg-blue-600 rounded-full"></span>
          任务指挥台
        </h2>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-2">一键执行全工作流 (Scout → Analyst → Linguistic → Creative)</p>
      </div>
      
      <!-- Scrollable Control Area -->
      <div class="flex-1 p-6 overflow-y-auto space-y-6">
        
        <!-- Input Textarea -->
        <div class="space-y-2">
          <label class="block text-sm font-bold text-slate-700 dark:text-slate-200">总体需求 / 链接</label>
          <textarea
            v-model="userInput"
            rows="3"
            class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-sm font-medium resize-none dark:text-white"
            placeholder="例如：帮我分析 VK 上热议的智能喂食器，并在 Ozon 准备一套高转化方案..."
          ></textarea>
          <p v-if="errorMsg" class="text-xs text-red-500">{{ errorMsg }}</p>
        </div>

        <!-- Mode Selection -->
        <div class="bg-slate-50 dark:bg-slate-900/50 p-5 rounded-xl border border-slate-100 dark:border-slate-700 space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">执行模式</span>
            <div class="flex items-center gap-1 bg-white dark:bg-slate-800 rounded-lg p-1 shadow-sm border border-slate-200 dark:border-slate-600">
              <button
                v-for="m in [{ v: 'pipeline', label: '🚀 全流程' }, { v: 'manual', label: '🔧 手动单步' }]"
                :key="m.v"
                :class="['px-3 py-1.5 rounded-md text-xs font-medium transition-all',
                  mode === m.v ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 shadow-sm' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200']"
                @click="mode = m.v as 'pipeline' | 'manual'"
              >{{ m.label }}</button>
            </div>
          </div>

          <!-- Pipeline Toggles -->
          <div v-if="mode === 'pipeline'" class="pt-2 border-t border-slate-200 dark:border-slate-700">
             <span class="text-xs font-bold text-slate-500 dark:text-slate-400 block mb-3">包含环节</span>
             <div class="grid grid-cols-2 gap-3">
               <label v-for="a in agents" :key="a.name" class="flex items-center gap-2 cursor-pointer group">
                  <input type="checkbox" v-model="agentConfig[`use_${a.name}` as keyof typeof agentConfig]" class="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500">
                  <span class="text-sm font-medium text-slate-700 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-white">{{ a.icon }} {{ a.label.split(' ')[0] }}</span>
               </label>
             </div>
          </div>
        </div>

        <!-- Stacked Agent Cards (Visible always, run button depends on manual mode and active mission) -->
        <div class="space-y-3">
          <span class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider pl-1">Agent 节点状态</span>
          <div class="flex flex-col gap-3">
            <AgentCard
              v-for="a in agents"
              :key="a.name"
              :name="a.name"
              :label="a.label"
              :icon="a.icon"
              :status="store.agentStatus[a.name]"
              :canRun="mode === 'manual' && !!store.currentMissionId"
              @run="handleAgentRun"
            />
          </div>
        </div>
      </div>

      <!-- Footer Action -->
      <div class="p-6 border-t border-slate-100 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800">
        <div class="flex gap-3">
          <button
            type="button"
            class="px-4 py-4 rounded-xl border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 font-bold hover:bg-white dark:hover:bg-slate-700 transition shadow-sm"
            @click="store.resetState(); userInput = ''; missionTitle = ''"
          >
            重置
          </button>
          <button 
            class="flex-1 py-4 bg-slate-900 dark:bg-blue-600 text-white rounded-xl font-bold text-lg hover:bg-slate-800 dark:hover:bg-blue-500 transition-all active:scale-[0.98] shadow-xl shadow-slate-900/10 dark:shadow-blue-900/20 flex items-center justify-center gap-3 disabled:opacity-70 disabled:cursor-not-allowed"
            :disabled="isLoading || store.missionStatus === 'running'"
            @click="handleStart"
          >
            <span v-if="isLoading || store.missionStatus === 'running'" class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></span>
            <span v-else>
              <svg v-if="mode === 'pipeline'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 inline-block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              {{ mode === 'pipeline' ? '启动全案生成' : '创建任务' }}
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- Right Column: Output & Logs (2/3 width) -->
    <div class="flex-1 flex flex-col gap-6 overflow-hidden">
      
      <!-- State 1: Live Terminal Log (Visible when running or idle without results) -->
      <div v-if="!isMissionComplete && store.missionStatus !== 'idle' || (store.missionStatus === 'idle' && !store.results.scout && !store.results.analyst)" class="flex-1 bg-slate-900 dark:bg-[#1e1e1e] rounded-2xl border border-slate-800 shadow-lg overflow-hidden flex flex-col animate-fade-in">
        <div class="px-4 py-3 border-b border-slate-800 bg-slate-900/50 flex justify-between items-center">
          <div class="flex items-center gap-2">
            <div class="flex gap-1.5">
              <div class="w-3 h-3 rounded-full bg-red-500"></div>
              <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div class="w-3 h-3 rounded-full bg-green-500"></div>
            </div>
            <span class="text-xs font-mono text-slate-400 ml-3">Agent Terminal Output</span>
            <span v-if="store.currentMissionId" class="text-xs font-mono text-slate-500 ml-2">| Mission #{{ store.currentMissionId }}</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-slate-500 mr-2">{{ store.logs.length }} records</span>
            <span v-if="store.missionStatus === 'running'" class="text-xs font-mono text-green-400 animate-pulse">● Running...</span>
          </div>
        </div>
        <div class="flex-1 relative p-4 bg-transparent text-gray-300 font-mono text-sm overflow-hidden">
           <LiveLog :logs="store.logs" />
        </div>
      </div>

      <!-- State 2: Results Gallery (Visible when complete or has results) -->
      <div v-else class="flex-1 flex flex-col bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden animate-fade-in">
        <!-- Result Header -->
        <div class="px-6 border-b border-slate-100 dark:border-slate-700 flex justify-between items-center bg-slate-50 dark:bg-slate-900">
           <h3 class="py-4 text-sm font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
              📊 任务执行结果
              <span v-if="store.missionStatus === 'done'" class="text-xs font-normal text-emerald-600 bg-emerald-100 px-2 py-0.5 rounded-full ml-2">已完成</span>
              <span v-else-if="store.missionStatus === 'failed'" class="text-xs font-normal text-red-600 bg-red-100 px-2 py-0.5 rounded-full ml-2">失败</span>
           </h3>
           <button class="text-xs text-blue-500 hover:underline" @click="store.fetchMissionResult()">刷新数据</button>
        </div>

        <!-- Tab Content using existing ResultPanel -->
        <div class="flex-1 p-6 overflow-y-auto bg-slate-50/50 dark:bg-slate-900/50">
           <ResultPanel :results="store.results" />
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.4s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

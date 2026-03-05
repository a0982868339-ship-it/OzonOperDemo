<template>
  <div class="min-h-screen bg-slate-50 p-8 font-sans">
    
    <!-- Title Section -->
    <div class="flex justify-between items-end mb-8">
      <div>
        <h1 class="text-3xl font-bold text-slate-900 tracking-tight">AI 策略中枢 (Strategy Center)</h1>
        <p class="text-slate-500 mt-2 text-sm font-medium">多智能体协同配置 & 数据权重策略管理</p>
      </div>
    </div>

    <!-- Main Grid -->
    <div class="grid grid-cols-12 gap-6">
      
      <!-- Left Column: Agent Configuration -->
      <div class="col-span-8 space-y-6">
        <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div class="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
            <h2 class="text-lg font-bold text-slate-900 flex items-center gap-2">
              <span class="w-2 h-6 bg-blue-600 rounded-full"></span>
              多智能体协同 (Multi-Agent Orchestration)
            </h2>
            <button @click="syncProvider" class="text-xs text-blue-600 font-bold hover:underline">
              一键同步配置到所有 Agent
            </button>
          </div>

          <!-- Agent Tabs -->
          <div class="flex border-b border-slate-100 overflow-x-auto">
            <button 
              v-for="agent in agents" 
              :key="agent.name"
              @click="activeAgent = agent.name"
              :class="[
                'px-6 py-4 text-sm font-bold border-b-2 transition-colors whitespace-nowrap',
                activeAgent === agent.name 
                  ? 'border-blue-600 text-blue-600 bg-blue-50/30' 
                  : 'border-transparent text-slate-500 hover:text-slate-800 hover:bg-slate-50'
              ]"
            >
              {{ agent.label }}
            </button>
          </div>

          <!-- Config Form -->
          <div class="p-8 animate-fade-in" v-if="currentAgentConfig">
            <div class="space-y-6">
              
              <!-- Provider & Model -->
              <div class="grid grid-cols-2 gap-6">
                <div>
                  <label class="block text-xs font-bold text-slate-500 uppercase mb-2">LLM 模型厂商 (Provider)</label>
                  <select v-model="currentAgentConfig.provider_name" class="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20">
                    <option value="OpenAI">OpenAI</option>
                    <option value="Anthropic">Anthropic (Claude)</option>
                    <option value="DeepSeek">DeepSeek</option>
                    <option value="Google">Google (Gemini)</option>
                    <option value="xAI">xAI (Grok)</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-bold text-slate-500 uppercase mb-2">模型 ID (Model ID)</label>
                  <input v-model="currentAgentConfig.model_id" type="text" class="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20">
                </div>
              </div>

              <!-- API Key -->
              <div>
                <label class="block text-xs font-bold text-slate-500 uppercase mb-2">API 密钥 (已加密)</label>
                <div class="relative">
                  <input 
                    v-model="currentAgentConfig.api_key" 
                    type="password" 
                    placeholder="sk-..."
                    class="w-full pl-4 pr-10 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  >
                  <div class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
                  </div>
                </div>
              </div>

              <!-- Temperature Slider -->
              <div>
                <div class="flex justify-between mb-2">
                  <label class="block text-xs font-bold text-slate-500 uppercase">创造性 (Temperature)</label>
                  <span class="text-xs font-mono font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">{{ currentAgentConfig.temperature }}</span>
                </div>
                <input 
                  v-model.number="currentAgentConfig.temperature" 
                  type="range" 
                  min="0" 
                  max="1" 
                  step="0.1"
                  class="w-full h-2 bg-slate-100 rounded-lg appearance-none cursor-pointer accent-blue-600"
                >
                <div class="flex justify-between text-[10px] text-slate-400 mt-1 font-medium uppercase tracking-wide">
                  <span>严谨 (Precise)</span>
                  <span>平衡 (Balanced)</span>
                  <span>创意 (Creative)</span>
                </div>
              </div>

              <!-- System Prompt -->
              <div>
                <label class="block text-xs font-bold text-slate-500 uppercase mb-2">系统预设提示词 (System Prompt / Persona)</label>
                <textarea 
                  v-model="currentAgentConfig.system_prompt" 
                  rows="6"
                  class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm leading-relaxed focus:outline-none focus:ring-2 focus:ring-blue-500/20 resize-none font-mono"
                ></textarea>
              </div>

              <div class="pt-4 flex justify-end">
                <button 
                  @click="saveAgentConfig" 
                  :disabled="saving"
                  class="px-6 py-2.5 bg-slate-900 text-white font-bold rounded-xl text-sm hover:bg-slate-800 transition-all flex items-center gap-2 disabled:opacity-70"
                >
                  <span v-if="saving" class="animate-spin w-4 h-4 border-2 border-white/30 border-t-white rounded-full"></span>
                  <span>保存配置</span>
                </button>
              </div>

            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Platform Weights & Score Preview -->
      <div class="col-span-4 space-y-6">
        
        <!-- Platform Weights -->
        <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <h2 class="text-lg font-bold text-slate-900 mb-6 flex items-center gap-2">
            <span class="w-2 h-6 bg-emerald-500 rounded-full"></span>
            数据权重策略 (Data Weighting)
          </h2>
          
          <div class="space-y-6">
            <div v-for="platform in platforms" :key="platform.name">
              <div class="flex justify-between mb-2">
                <span class="text-sm font-bold text-slate-700">{{ platform.name }}</span>
                <span class="text-xs font-mono font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">{{ platform.weight }}x</span>
              </div>
              <input 
                v-model.number="platform.weight" 
                @input="debouncedCalculateScore"
                type="range" 
                min="0.1" 
                max="2.0" 
                step="0.1"
                class="w-full h-1.5 bg-slate-100 rounded-lg appearance-none cursor-pointer accent-emerald-500"
              >
            </div>
          </div>
        </div>

        <!-- Formula Preview -->
        <div class="bg-slate-900 rounded-2xl border border-slate-800 shadow-lg p-6 text-white relative overflow-hidden">
          <div class="absolute top-0 right-0 p-4 opacity-10">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-24 w-24" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" /></svg>
          </div>
          
          <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">综合评分预览 (Unified Score)</h3>
          
          <div class="text-4xl font-bold font-mono tracking-tight mb-2 text-emerald-400">
            {{ simulatedScore.toFixed(2) }}
          </div>
          <div class="text-xs text-slate-500 mb-6">基于当前权重 & 模拟声量数据</div>

          <div class="space-y-2">
            <div v-for="(val, key) in scoreBreakdown" :key="key" class="flex justify-between text-xs">
              <span class="text-slate-400">{{ key }}</span>
              <span class="font-mono text-slate-200">+{{ val.toFixed(1) }}</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { apiGet, apiPatch } from '../api/client'
import { ElMessage } from 'element-plus'
import { debounce } from 'lodash'

// --- Agent Logic ---
const activeAgent = ref('orchestrator')
const agents = [
  { name: 'orchestrator', label: '🧠 总控调度 (Orchestrator)' },
  { name: 'scout', label: '🕵️ 市场侦探 (Scout)' },
  { name: 'analyst', label: '📊 数据精算 (Analyst)' },
  { name: 'linguistic', label: '✍️ 语言翻译 (Linguist)' },
  { name: 'creative', label: '🎨 创意设计 (Creative)' },
  { name: 'seo', label: '🛒 SEO文案 (SEO Agent)' },
  { name: 'image', label: '🖼️ 商品生图 (Image Agent)' },
  { name: 'video', label: '🎬 视频生成 (Video Agent)' },
  { name: 'prompt_engineer', label: '✨ 提示词工程 (Prompt Engineer)' }
]

const agentConfigs = ref<Record<string, any>>({})
const saving = ref(false)

const currentAgentConfig = computed(() => agentConfigs.value[activeAgent.value])

const normalizeAgentName = (name: string) => name.trim().toLowerCase()

const buildDefaults = () => {
  const mockData = {
    provider_name: 'OpenAI',
    model_id: 'gpt-4-turbo',
    temperature: 0.7,
    system_prompt: 'You are an AI assistant...',
    api_key: ''
  }
  agents.forEach(a => {
    agentConfigs.value[a.name] = { ...mockData, agent_name: a.name }
  })
  if (!agentConfigs.value[activeAgent.value] && agents.length > 0) {
    activeAgent.value = agents[0].name
  }
}

const fetchAgents = async () => {
  buildDefaults()
  try {
    const res = await apiGet<any[]>('/api/v1/admin/configs')
    const latestByAgent: Record<string, any> = {}
    res.forEach(item => {
      const key = normalizeAgentName(item.agent_name || '')
      if (!key || latestByAgent[key]) return
      latestByAgent[key] = item
    })
    Object.entries(latestByAgent).forEach(([key, item]) => {
      if (!agentConfigs.value[key]) return
      agentConfigs.value[key] = {
        ...agentConfigs.value[key],
        provider_name: item.provider_name ?? agentConfigs.value[key].provider_name,
        model_id: item.model_id ?? agentConfigs.value[key].model_id,
        agent_name: item.agent_name ?? agentConfigs.value[key].agent_name,
        api_key: ''
      }
    })
  } catch (e) {
    console.error(e)
  }
}

const saveAgentConfig = async () => {
  if (!currentAgentConfig.value) return
  saving.value = true
  try {
    const agentName = currentAgentConfig.value.agent_name || activeAgent.value
    await apiPatch(`/api/v1/admin/configs/${agentName}`, {
      provider_name: currentAgentConfig.value.provider_name,
      model_id: currentAgentConfig.value.model_id,
      api_key: currentAgentConfig.value.api_key || undefined
    })
    saving.value = false
    ElMessage.success(`${activeAgent.value} configuration saved.`)
  } catch (e) {
    saving.value = false
    ElMessage.error('Failed to save config')
  }
}

const syncProvider = () => {
  if (!currentAgentConfig.value) return
  const { provider_name, api_key } = currentAgentConfig.value
  const updates = Object.keys(agentConfigs.value).map(key => {
    agentConfigs.value[key].provider_name = provider_name
    if (api_key) agentConfigs.value[key].api_key = api_key
    const agentName = agentConfigs.value[key].agent_name || key
    return apiPatch(`/api/v1/admin/configs/${agentName}`, {
      provider_name,
      model_id: agentConfigs.value[key].model_id,
      api_key: api_key || undefined
    })
  })
  Promise.all(updates)
    .then(() => ElMessage.success(`Synced ${provider_name} settings to all agents.`))
    .catch(() => ElMessage.error('Failed to sync config'))
}

// --- Platform Weights Logic ---
const platforms = ref([
  { name: 'VK', weight: 1.2 },
  { name: 'OK', weight: 0.8 },
  { name: 'YouTube', weight: 1.5 },
  { name: 'Ozon', weight: 1.0 },
  { name: 'WB', weight: 1.0 },
  { name: 'Yandex', weight: 0.9 }
])

const simulatedScore = ref(0)
const scoreBreakdown = ref<Record<string, number>>({})

const calculateScore = () => {
  // Mock Volume Data
  const volumes = {
    'VK': 1200, 'OK': 800, 'YouTube': 3000, 
    'Ozon': 5000, 'WB': 4500, 'Yandex': 2000
  }
  
  let total = 0
  const breakdown: Record<string, number> = {}
  
  platforms.value.forEach(p => {
    const vol = volumes[p.name as keyof typeof volumes] || 0
    const contribution = vol * p.weight
    total += contribution
    breakdown[p.name] = contribution
  })
  
  // Apply Global Growth Rate (Mock 5%)
  simulatedScore.value = total * 1.05
  scoreBreakdown.value = breakdown
}

const debouncedCalculateScore = debounce(calculateScore, 100)

onMounted(() => {
  fetchAgents()
  calculateScore()
})
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

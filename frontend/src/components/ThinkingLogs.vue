<script setup lang="ts">
import { ref, watch, nextTick, onMounted } from "vue"
import { useMissionStore } from "../stores/mission"
import { storeToRefs } from "pinia"

const missionStore = useMissionStore()
const { logs } = storeToRefs(missionStore)
const logContainer = ref<HTMLElement | null>(null)

// Auto-scroll to bottom
watch(logs, () => {
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }
  })
}, { deep: true })

const getAgentColor = (agent: string) => {
  if (agent.includes("Scout") || agent.includes("市场侦察")) return "text-blue-400"
  if (agent.includes("Strategy") || agent.includes("策略分析")) return "text-indigo-400"
  if (agent.includes("Linguistic") || agent.includes("语言专家")) return "text-emerald-400"
  if (agent.includes("Creative") || agent.includes("创意总监")) return "text-purple-400"
  if (agent.includes("Operation") || agent.includes("运营管家")) return "text-orange-400"
  if (agent === "System") return "text-slate-400"
  return "text-white"
}

// Format timestamp
const formatTime = (ts: number) => {
  return new Date(ts).toLocaleTimeString("ru-RU", { hour12: false })
}
</script>

<template>
  <div class="h-full flex flex-col bg-black/80 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden shadow-2xl font-mono text-sm relative group">
    <!-- Header -->
    <div class="px-4 py-2 bg-white/5 border-b border-white/5 flex justify-between items-center">
      <div class="flex items-center gap-2">
        <div class="flex gap-1.5">
          <div class="w-2.5 h-2.5 rounded-full bg-red-500/50"></div>
          <div class="w-2.5 h-2.5 rounded-full bg-yellow-500/50"></div>
          <div class="w-2.5 h-2.5 rounded-full bg-green-500/50"></div>
        </div>
        <span class="text-xs text-slate-500 ml-2">终端日志 (Terminal Output)</span>
      </div>
      <div class="flex items-center gap-2 text-[10px] text-slate-600">
        <span class="animate-pulse">●</span> 实时数据流
      </div>
    </div>

    <!-- Logs Area -->
    <div 
      ref="logContainer"
      class="flex-1 overflow-y-auto p-4 space-y-2 scrollbar-hide"
    >
      <div 
        v-for="log in logs" 
        :key="log.id"
        class="animate-slide-up flex gap-3 group/log"
      >
        <span class="text-slate-600 shrink-0 select-none">[{{ formatTime(log.timestamp) }}]</span>
        
        <div class="flex flex-col">
          <span :class="['font-bold text-xs uppercase tracking-wider mb-0.5', getAgentColor(log.agent)]">
            {{ log.agent }} $
          </span>
          <span :class="[
            'typing-effect break-all',
            log.type === 'error' ? 'text-red-400' : 
            log.type === 'success' ? 'text-green-400' : 'text-slate-300'
          ]">
            {{ log.message }}
          </span>
        </div>
      </div>

      <!-- Cursor -->
      <div class="h-4 w-2 bg-blue-500/50 animate-pulse mt-2"></div>
    </div>

    <!-- Scanlines Overlay -->
    <div class="absolute inset-0 pointer-events-none bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] z-10 bg-[length:100%_2px,3px_100%]"></div>
  </div>
</template>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
    display: none;
}
.scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-slide-up {
  animation: slide-up 0.3s ease-out forwards;
}

/* Optional typing effect for text appearance */
.typing-effect {
  display: inline-block;
  overflow: hidden;
  white-space: pre-wrap;
}
</style>

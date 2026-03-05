<script setup lang="ts">
import { useMissionStore } from "../stores/mission"
import { storeToRefs } from "pinia"

const missionStore = useMissionStore()
const { isMissionRunning, agents } = storeToRefs(missionStore)
</script>

<template>
  <div v-if="isMissionRunning" class="absolute inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm transition-all duration-500">
    <div class="relative w-full max-w-4xl h-[600px] flex items-center justify-center">
      
      <!-- Central Hub -->
      <div class="absolute z-20 w-32 h-32 bg-blue-600/20 rounded-full border border-blue-500/50 flex items-center justify-center shadow-[0_0_50px_rgba(37,99,235,0.3)] animate-pulse">
        <div class="w-24 h-24 bg-blue-500/10 rounded-full border border-blue-400/30 animate-[spin_10s_linear_infinite]"></div>
        <div class="absolute text-blue-300 font-mono text-xs tracking-widest animate-pulse">核心 AI</div>
      </div>

      <!-- Connecting Lines (SVG) -->
      <svg class="absolute inset-0 w-full h-full pointer-events-none z-10">
        <defs>
          <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="rgba(59, 130, 246, 0)" />
            <stop offset="50%" stop-color="rgba(59, 130, 246, 0.8)" />
            <stop offset="100%" stop-color="rgba(59, 130, 246, 0)" />
          </linearGradient>
        </defs>
        
        <!-- Lines to Agents (Calculated roughly based on position) -->
        <!-- Top Left -->
        <path d="M 450 300 L 150 150" stroke="url(#lineGradient)" stroke-width="2" fill="none" class="animate-dash" />
        <!-- Top Right -->
        <path d="M 450 300 L 750 150" stroke="url(#lineGradient)" stroke-width="2" fill="none" class="animate-dash-reverse" />
        <!-- Bottom Left -->
        <path d="M 450 300 L 150 450" stroke="url(#lineGradient)" stroke-width="2" fill="none" class="animate-dash" />
        <!-- Bottom Right -->
        <path d="M 450 300 L 750 450" stroke="url(#lineGradient)" stroke-width="2" fill="none" class="animate-dash-reverse" />
        <!-- Top Center -->
        <path d="M 450 300 L 450 100" stroke="url(#lineGradient)" stroke-width="2" fill="none" class="animate-dash" />
      </svg>

      <!-- Agent Nodes -->
      <!-- 1. Market Scout (Top Left) -->
      <div class="absolute top-[100px] left-[100px] flex flex-col items-center gap-2">
        <div class="w-16 h-16 rounded-xl bg-slate-900 border border-blue-500/30 flex items-center justify-center text-2xl shadow-lg relative overflow-hidden group">
          <div class="absolute inset-0 bg-blue-500/10 group-hover:bg-blue-500/20 transition-colors"></div>
          🔍
          <div v-if="agents[0].status === 'active'" class="absolute inset-0 border-2 border-blue-500 rounded-xl animate-ping"></div>
        </div>
        <span class="text-xs text-blue-300 font-mono bg-slate-900/80 px-2 py-1 rounded">市场侦察</span>
      </div>

      <!-- 2. Strategy Analyst (Top Right) -->
      <div class="absolute top-[100px] right-[100px] flex flex-col items-center gap-2">
        <div class="w-16 h-16 rounded-xl bg-slate-900 border border-indigo-500/30 flex items-center justify-center text-2xl shadow-lg relative overflow-hidden group">
          <div class="absolute inset-0 bg-indigo-500/10 group-hover:bg-indigo-500/20 transition-colors"></div>
          📊
           <div v-if="agents[1].status === 'active'" class="absolute inset-0 border-2 border-indigo-500 rounded-xl animate-ping"></div>
        </div>
        <span class="text-xs text-indigo-300 font-mono bg-slate-900/80 px-2 py-1 rounded">策略分析</span>
      </div>

      <!-- 3. Linguistic Expert (Bottom Left) -->
      <div class="absolute bottom-[100px] left-[100px] flex flex-col items-center gap-2">
        <div class="w-16 h-16 rounded-xl bg-slate-900 border border-emerald-500/30 flex items-center justify-center text-2xl shadow-lg relative overflow-hidden group">
          <div class="absolute inset-0 bg-emerald-500/10 group-hover:bg-emerald-500/20 transition-colors"></div>
          ✍️
           <div v-if="agents[2].status === 'active'" class="absolute inset-0 border-2 border-emerald-500 rounded-xl animate-ping"></div>
        </div>
        <span class="text-xs text-emerald-300 font-mono bg-slate-900/80 px-2 py-1 rounded">语言专家</span>
      </div>

      <!-- 4. Creative Director (Bottom Right) -->
      <div class="absolute bottom-[100px] right-[100px] flex flex-col items-center gap-2">
        <div class="w-16 h-16 rounded-xl bg-slate-900 border border-purple-500/30 flex items-center justify-center text-2xl shadow-lg relative overflow-hidden group">
          <div class="absolute inset-0 bg-purple-500/10 group-hover:bg-purple-500/20 transition-colors"></div>
          🎨
           <div v-if="agents[3].status === 'active'" class="absolute inset-0 border-2 border-purple-500 rounded-xl animate-ping"></div>
        </div>
        <span class="text-xs text-purple-300 font-mono bg-slate-900/80 px-2 py-1 rounded">创意总监</span>
      </div>

      <!-- 5. Operation Manager (Top Center) -->
      <div class="absolute top-[50px] left-1/2 -translate-x-1/2 flex flex-col items-center gap-2">
        <div class="w-16 h-16 rounded-xl bg-slate-900 border border-orange-500/30 flex items-center justify-center text-2xl shadow-lg relative overflow-hidden group">
          <div class="absolute inset-0 bg-orange-500/10 group-hover:bg-orange-500/20 transition-colors"></div>
          🚀
           <div v-if="agents[4].status === 'active'" class="absolute inset-0 border-2 border-orange-500 rounded-xl animate-ping"></div>
        </div>
        <span class="text-xs text-orange-300 font-mono bg-slate-900/80 px-2 py-1 rounded">运营管家</span>
      </div>

    </div>
  </div>
</template>

<style scoped>
.animate-dash {
  stroke-dasharray: 10;
  animation: dash 1s linear infinite;
}
.animate-dash-reverse {
  stroke-dasharray: 10;
  animation: dash-reverse 1s linear infinite;
}

@keyframes dash {
  to {
    stroke-dashoffset: -20;
  }
}
@keyframes dash-reverse {
  to {
    stroke-dashoffset: 20;
  }
}
</style>

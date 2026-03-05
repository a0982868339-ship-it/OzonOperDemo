<script setup lang="ts">
import { useMissionStore } from "../stores/mission"
import { storeToRefs } from "pinia"

const missionStore = useMissionStore()
const { agents, progress } = storeToRefs(missionStore)
</script>

<template>
  <div class="bg-slate-900/50 backdrop-blur-md rounded-2xl p-6 border border-white/10 shadow-xl">
    <div class="flex justify-between items-center mb-6">
      <h3 class="text-white font-semibold flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
        任务控制中心 (Mission Control)
      </h3>
      <span class="text-xs font-mono text-slate-400">系统: 在线</span>
    </div>

    <!-- Agents Grid -->
    <div class="grid grid-cols-5 gap-4 mb-8">
      <div 
        v-for="agent in agents" 
        :key="agent.name"
        class="flex flex-col items-center gap-2 p-3 rounded-xl transition-all duration-300 group"
        :class="[
          agent.status === 'active' ? 'bg-white/10 shadow-lg scale-105 border-blue-500/50 border' : 'bg-white/5 border border-transparent',
          agent.status === 'completed' ? 'border-green-500/30 bg-green-500/10' : ''
        ]"
      >
        <div class="relative">
          <div class="w-8 h-8 text-white/80 filter drop-shadow-lg transition-transform duration-500 flex items-center justify-center"
               :class="{ 'animate-bounce': agent.status === 'active', 'text-blue-400': agent.status === 'active' }"
               v-html="agent.icon">
          </div>
          <div v-if="agent.status === 'active'" class="absolute -top-1 -right-1 w-2 h-2 bg-blue-500 rounded-full animate-ping"></div>
        </div>
        
        <div class="text-center">
          <div class="text-xs font-bold text-white group-hover:text-blue-400 transition-colors">{{ agent.name }}</div>
          <div class="text-[10px] text-slate-400 uppercase tracking-wider">{{ agent.role }}</div>
        </div>

        <!-- Status Indicator -->
        <div class="mt-1 px-2 py-0.5 rounded-full text-[10px] font-mono border"
             :class="{
               'bg-slate-800 text-slate-500 border-slate-700': agent.status === 'idle',
               'bg-blue-500/20 text-blue-300 border-blue-500/30 animate-pulse': agent.status === 'active',
               'bg-green-500/20 text-green-300 border-green-500/30': agent.status === 'completed',
               'bg-red-500/20 text-red-300 border-red-500/30': agent.status === 'failed'
             }">
          {{ agent.status === 'idle' ? '待命' : agent.status === 'active' ? '运行中' : agent.status === 'completed' ? '完成' : '失败' }}
        </div>
      </div>
    </div>

    <!-- Global Progress -->
    <div class="space-y-2">
      <div class="flex justify-between text-xs text-slate-400 font-mono">
        <span>任务进度</span>
        <span>{{ Math.round(progress) }}%</span>
      </div>
      <div class="h-2 bg-slate-800 rounded-full overflow-hidden">
        <div 
          class="h-full bg-gradient-to-r from-blue-600 via-indigo-500 to-purple-500 transition-all duration-700 ease-out relative"
          :style="{ width: `${progress}%` }"
        >
          <div class="absolute inset-0 bg-white/30 animate-[shimmer_2s_infinite]"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
</style>

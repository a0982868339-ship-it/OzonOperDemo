<script setup lang="ts">
import type { LogEntry } from '../stores/missionStore'

defineProps<{ logs: LogEntry[] }>()

const agentColor: Record<string, string> = {
  Scout:       'text-violet-500',
  Analyst:     'text-blue-500',
  Linguistic:  'text-emerald-500',
  Creative:    'text-amber-500',
  Orchestrator:'text-pink-500',
  System:      'text-slate-400',
}
</script>

<template>
  <div class="flex flex-col gap-0.5 font-mono text-xs overflow-y-auto h-full pr-1">
    <div v-if="!logs.length" class="text-slate-400 dark:text-slate-500 py-4 text-center">
      等待任务启动...
    </div>
    <TransitionGroup name="log-fade" tag="div">
      <div
        v-for="(log, i) in logs"
        :key="i"
        class="flex gap-2 py-0.5 border-b border-slate-50 dark:border-slate-800/50"
      >
        <span class="text-slate-400 w-16 flex-shrink-0">{{ log.ts }}</span>
        <span :class="['font-semibold w-20 flex-shrink-0', agentColor[log.agent] || 'text-slate-500']">
          [{{ log.agent }}]
        </span>
        <span
          :class="[
            'flex-1',
            log.type === 'error' ? 'text-red-500' : 'text-slate-600 dark:text-slate-300'
          ]"
        >{{ log.message }}</span>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.log-fade-enter-active { transition: opacity 0.3s, transform 0.3s; }
.log-fade-enter-from   { opacity: 0; transform: translateY(-4px); }
</style>

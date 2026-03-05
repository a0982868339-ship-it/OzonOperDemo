<script setup lang="ts">
import { ref } from 'vue'
import type { AgentName, AgentStatus } from '../stores/missionStore'

const props = defineProps<{
  name: AgentName
  label: string
  icon: string
  status: AgentStatus
  canRun: boolean
}>()

const emit = defineEmits<{
  (e: 'run', name: AgentName, overrideData?: Record<string, any>): void
}>()

const showOverride = ref(false)
const overrideText = ref('')
const isImagePrompt = props.name === 'creative'
const isScoutData   = props.name === 'scout'

function runAgent() {
  const override: Record<string, any> = {}
  if (overrideText.value.trim()) {
    if (props.name === 'linguistic') override.copy = overrideText.value
    else if (props.name === 'creative') override.image_prompt = overrideText.value
    else if (props.name === 'scout') {
      try { override.scout_data = JSON.parse(overrideText.value) } catch { override.scout_data = null }
    }
  }
  emit('run', props.name, Object.keys(override).length ? override : undefined)
}

const statusColor: Record<AgentStatus, string> = {
  idle:    'bg-slate-400',
  running: 'bg-blue-500 animate-pulse',
  done:    'bg-emerald-500',
  failed:  'bg-red-500',
  skipped: 'bg-amber-400',
}
const statusLabel: Record<AgentStatus, string> = {
  idle: '等待', running: '运行中', done: '完成', failed: '失败', skipped: '已跳过',
}
</script>

<template>
  <div
    class="relative flex flex-col gap-2 rounded-xl border p-3 transition-all duration-300"
    :class="[
      status === 'running' ? 'border-blue-400 shadow-blue-100 shadow-sm dark:shadow-blue-900/30' :
      status === 'done'    ? 'border-emerald-400' :
      status === 'failed'  ? 'border-red-400' :
      'border-slate-200 dark:border-slate-700'
    ]"
  >
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-1.5">
        <span class="text-lg">{{ icon }}</span>
        <span class="font-bold text-xs text-slate-800 dark:text-slate-200">{{ label }}</span>
      </div>
      <div class="flex items-center gap-1.5">
        <span :class="['h-1.5 w-1.5 rounded-full', statusColor[status]]"></span>
        <span class="text-[10px] uppercase font-bold text-slate-500 dark:text-slate-400">{{ statusLabel[status] }}</span>
      </div>
    </div>

    <!-- Progress bar -->
    <div class="h-1 w-full rounded-full bg-slate-100 dark:bg-slate-700 overflow-hidden">
      <div
        class="h-full rounded-full transition-all duration-700"
        :class="status === 'done' ? 'bg-emerald-500 w-full' :
                status === 'running' ? 'bg-blue-500 w-3/4 animate-pulse' :
                status === 'failed'  ? 'bg-red-500 w-full' :
                status === 'skipped' ? 'bg-amber-400 w-full' : 'w-0'"
      ></div>
    </div>

    <!-- Override toggle -->
    <button
      v-if="canRun"
      class="text-xs text-slate-400 hover:text-blue-500 dark:hover:text-blue-400 underline text-left transition-colors"
      @click="showOverride = !showOverride"
    >
      {{ showOverride ? '收起' : '使用自定义数据覆盖 ▾' }}
    </button>

    <div v-if="showOverride && canRun" class="flex flex-col gap-2">
      <textarea
        v-model="overrideText"
        rows="3"
        class="w-full rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 text-xs p-2 resize-none focus:outline-none focus:ring-2 focus:ring-blue-400"
        :placeholder="
          name === 'linguistic' ? '粘贴您的文案（将跳过 AI 生成）...' :
          name === 'creative'   ? '输入 Prompt（如：冬日温馨风格的智能猫碗）...' :
          name === 'scout'      ? '粘贴 JSON 数据（将跳过爬虫）...' :
          '输入覆盖数据...'"
      ></textarea>
    </div>

    <!-- Run button -->
    <button
      v-if="canRun"
      :disabled="status === 'running'"
      class="mt-1 w-full rounded-lg py-1 text-[10px] font-bold uppercase tracking-wider transition-all duration-200"
      :class="status === 'running'
        ? 'bg-slate-100 dark:bg-slate-700 text-slate-400 cursor-not-allowed'
        : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-900 dark:hover:bg-blue-600 hover:text-white pointer'"
      @click="runAgent"
    >
      {{ status === 'running' ? '运行中...' : '单独执行' }}
    </button>
  </div>
</template>

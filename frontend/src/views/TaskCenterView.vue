<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue"
import { apiGet } from "../api/client"

interface AIAsset {
  id: number
  task_id: string
  asset_type: string
  status: string
  result_data?: any
  created_at: string
}

const tasks = ref<AIAsset[]>([])
const timer = ref<number | null>(null)

const fetchTasks = async () => {
  tasks.value = await apiGet<AIAsset[]>("/ai/tasks")
}

onMounted(() => {
  fetchTasks()
  // Poll every 5 seconds
  timer.value = window.setInterval(fetchTasks, 5000)
})

onUnmounted(() => {
  if (timer.value) clearInterval(timer.value)
})

// Pipeline stages for visualization
const getStages = (type: string, status: string) => {
  const isCompleted = status === 'COMPLETED'
  const isFailed = status === 'FAILED'
  const isGenerating = status === 'GENERATING'
  
  const baseStages = [
    { label: '提交任务', done: true },
    { label: 'AI 推理', done: isGenerating || isCompleted || isFailed, active: isGenerating },
    { label: '后期渲染', done: isCompleted || isFailed, active: isGenerating && type === 'media' },
    { label: '结果交付', done: isCompleted, error: isFailed }
  ]
  return baseStages
}
</script>

<template>
  <div class="space-y-6">
    <header class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 tracking-tight">任务中心 (Task Center)</h1>
        <p class="text-sm text-slate-500 mt-1">AI 自动化流水线监控 · 实时进度追踪</p>
      </div>
      <el-button @click="fetchTasks" icon="Refresh" circle />
    </header>

    <div class="grid gap-4">
      <div 
        v-for="task in tasks" 
        :key="task.id" 
        class="bg-white rounded-xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden"
      >
        <!-- Status Stripe -->
        <div class="absolute left-0 top-0 bottom-0 w-1" :class="{
          'bg-blue-500 animate-pulse': task.status === 'GENERATING',
          'bg-green-500': task.status === 'COMPLETED',
          'bg-red-500': task.status === 'FAILED',
          'bg-slate-300': task.status === 'PENDING'
        }"></div>

        <div class="flex flex-col lg:flex-row gap-6">
          <!-- Info Section -->
          <div class="lg:w-1/4 space-y-2">
             <div class="flex items-center gap-2">
               <span class="text-2xl">{{ task.asset_type === 'media' ? '🎨' : '✍️' }}</span>
               <div>
                 <div class="font-bold text-slate-800 capitalize">{{ task.asset_type === 'media' ? 'AI 视觉生成' : 'SEO 文案优化' }}</div>
                 <div class="text-xs font-mono text-slate-400">{{ task.task_id.split('-').slice(0,2).join('-') }}...</div>
               </div>
             </div>
             <div class="text-xs text-slate-500 flex items-center gap-1">
               <span>🕒 提交于:</span>
               <span>{{ new Date(task.created_at).toLocaleString() }}</span>
             </div>
          </div>

          <!-- Pipeline Visualizer -->
          <div class="lg:w-2/4 flex items-center justify-between px-4">
            <div 
              v-for="(stage, idx) in getStages(task.asset_type, task.status)" 
              :key="idx"
              class="flex flex-col items-center gap-2 relative z-10 w-full"
            >
               <!-- Connecting Line -->
               <div v-if="idx > 0" class="absolute top-3 -left-1/2 w-full h-0.5 bg-slate-100 -z-10">
                 <div 
                   class="h-full bg-blue-500 transition-all duration-500" 
                   :style="{ width: stage.done ? '100%' : '0%' }"
                 ></div>
               </div>

               <!-- Dot -->
               <div 
                 class="w-6 h-6 rounded-full flex items-center justify-center border-2 transition-colors bg-white"
                 :class="{
                   'border-blue-500 text-blue-500': stage.active,
                   'border-green-500 bg-green-500 text-white': stage.done && !stage.error,
                   'border-red-500 bg-red-500 text-white': stage.error,
                   'border-slate-200 text-slate-300': !stage.done && !stage.active && !stage.error
                 }"
               >
                 <span v-if="stage.error">✕</span>
                 <span v-else-if="stage.done">✓</span>
                 <span v-else-if="stage.active" class="animate-spin text-xs">↻</span>
                 <span v-else class="text-xs">{{ idx + 1 }}</span>
               </div>
               
               <!-- Label -->
               <span class="text-xs font-medium" :class="stage.active || stage.done ? 'text-slate-700' : 'text-slate-400'">
                 {{ stage.label }}
               </span>
            </div>
          </div>

          <!-- Result/Action Area -->
          <div class="lg:w-1/4 flex items-center justify-end pl-4 border-l border-slate-100">
             <div v-if="task.status === 'COMPLETED' && task.result_data" class="text-right w-full">
                <!-- Media Result -->
                <div v-if="task.asset_type === 'media' && task.result_data.urls" class="flex justify-end gap-2">
                   <div v-for="(url, idx) in task.result_data.urls" :key="idx" class="relative group cursor-pointer">
                      <img v-if="!String(url).endsWith('.mp4')" :src="String(url)" class="w-16 h-16 rounded-lg object-cover border border-slate-200 shadow-sm group-hover:scale-105 transition-transform" />
                      <div v-else class="w-16 h-16 rounded-lg bg-slate-900 flex items-center justify-center text-white text-xs">Video</div>
                      <a :href="String(url)" target="_blank" class="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 group-hover:opacity-100 rounded-lg transition-opacity text-white text-xs">
                        查看
                      </a>
                   </div>
                </div>
                <!-- Text Result -->
                <div v-else-if="task.asset_type === 'seo'" class="text-left bg-slate-50 p-3 rounded-lg border border-slate-100 w-full">
                  <div class="font-bold text-sm text-slate-800 truncate" :title="task.result_data.title_seo">{{ task.result_data.title_seo }}</div>
                  <div class="text-xs text-slate-500 mt-1 line-clamp-2">{{ task.result_data.short_description }}</div>
                  <el-button type="primary" link size="small" class="mt-2">复制文案</el-button>
                </div>
             </div>
             
             <div v-else-if="task.status === 'FAILED'" class="text-red-500 text-sm flex items-center gap-1">
               <span>⚠️</span> 任务失败
             </div>
             
             <div v-else class="text-slate-400 text-sm italic">
               Agent 工作中...
             </div>
          </div>
        </div>
      </div>

      <div v-if="tasks.length === 0" class="text-center py-20 bg-slate-50 rounded-xl border border-dashed border-slate-200">
        <div class="text-4xl mb-4">📭</div>
        <h3 class="text-slate-500 font-medium">暂无任务记录</h3>
        <p class="text-slate-400 text-sm mt-1">去创意工厂提交第一个任务吧</p>
      </div>
    </div>
  </div>
</template>

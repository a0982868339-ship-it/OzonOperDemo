<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-end">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">任务中心 (Task Center)</h1>
        <p class="text-slate-500 dark:text-slate-400 mt-2 font-medium">后台异步任务监控与管理</p>
      </div>
      <div class="flex gap-3">
        <button class="px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
          清除已完成
        </button>
        <button class="px-4 py-2 bg-slate-900 dark:bg-blue-600 text-white rounded-lg text-sm font-bold hover:bg-slate-800 dark:hover:bg-blue-700 transition-colors">
          刷新列表
        </button>
      </div>
    </div>

    <!-- Task Stats -->
    <div class="grid grid-cols-4 gap-6">
      <div v-for="stat in stats" :key="stat.label" class="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm transition-colors duration-300">
        <div class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-2">{{ stat.label }}</div>
        <div class="text-3xl font-bold font-mono" :class="stat.color">{{ stat.value }}</div>
      </div>
    </div>

    <!-- Task List -->
    <div v-if="tasks.length > 0" class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden transition-colors duration-300">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead class="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-700">
            <tr>
              <th class="px-6 py-4 font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-xs">Task ID</th>
              <th class="px-6 py-4 font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-xs">Type</th>
              <th class="px-6 py-4 font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-xs">Status</th>
              <th class="px-6 py-4 font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-xs">Progress</th>
              <th class="px-6 py-4 font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-xs">Created At</th>
              <th class="px-6 py-4 font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-xs text-right">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-700">
            <tr v-for="task in tasks" :key="task.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
              <td class="px-6 py-4 font-mono text-slate-600 dark:text-slate-300">{{ task.id }}</td>
              <td class="px-6 py-4 font-bold text-slate-900 dark:text-white">{{ task.type }}</td>
              <td class="px-6 py-4">
                <span class="px-2.5 py-1 rounded-full text-xs font-bold" :class="getStatusColor(task.status)">
                  {{ task.status }}
                </span>
              </td>
              <td class="px-6 py-4">
                <div class="w-32 h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                  <div class="h-full bg-blue-500 rounded-full transition-all duration-500" :style="{ width: task.progress + '%' }"></div>
                </div>
              </td>
              <td class="px-6 py-4 text-slate-500 dark:text-slate-400">{{ task.createdAt }}</td>
              <td class="px-6 py-4 text-right">
                <button class="text-blue-600 dark:text-blue-400 font-bold hover:underline text-xs">Details</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-12 flex flex-col items-center justify-center text-center transition-colors duration-300">
      <div class="w-16 h-16 bg-slate-100 dark:bg-slate-700 rounded-full flex items-center justify-center mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-slate-400 dark:text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>
      </div>
      <h3 class="text-lg font-bold text-slate-900 dark:text-white">暂无任务记录</h3>
      <p class="text-slate-500 dark:text-slate-400 mt-1 max-w-sm">去创意工坊提交一个新任务吧</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const stats = [
  { label: 'Running', value: '12', color: 'text-blue-600 dark:text-blue-400' },
  { label: 'Pending', value: '5', color: 'text-orange-500' },
  { label: 'Completed', value: '842', color: 'text-emerald-500' },
  { label: 'Failed', value: '3', color: 'text-red-500' },
]

const tasks = ref([
  { id: 'TASK-8821', type: 'Product Analysis', status: 'Running', progress: 45, createdAt: '2 mins ago' },
  { id: 'TASK-8820', type: 'Image Generation', status: 'Completed', progress: 100, createdAt: '15 mins ago' },
  { id: 'TASK-8819', type: 'Copywriting', status: 'Failed', progress: 80, createdAt: '1 hour ago' },
  { id: 'TASK-8818', type: 'Video Rendering', status: 'Running', progress: 12, createdAt: '1 hour ago' },
  { id: 'TASK-8817', type: 'Keyword Scout', status: 'Completed', progress: 100, createdAt: '2 hours ago' },
])

const getStatusColor = (status: string) => {
  switch (status) {
    case 'Running': return 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
    case 'Completed': return 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300'
    case 'Failed': return 'bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-300'
    default: return 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300'
  }
}
</script>

<script setup lang="ts">
import type { MissionResult } from '../stores/missionStore'

defineProps<{ results: MissionResult }>()

function asList(val: any): string[] {
  if (Array.isArray(val)) return val
  if (typeof val === 'string') return [val]
  return []
}
</script>

<template>
  <div class="flex flex-col gap-4 h-full overflow-y-auto pr-1">
    <div v-if="!results.scout && !results.analyst && !results.linguistic && !results.creative"
         class="text-slate-400 dark:text-slate-500 py-8 text-center text-sm">
      结果将在各 Agent 完成后逐步展示...
    </div>

    <!-- Scout -->
    <div v-if="results.scout" class="result-card">
      <h4 class="result-title">🔍 Scout 情报</h4>
      <pre class="result-pre">{{ JSON.stringify(results.scout, null, 2) }}</pre>
    </div>

    <!-- Analyst -->
    <div v-if="results.analyst" class="result-card">
      <h4 class="result-title">📊 Analyst 评分</h4>
      <div class="flex flex-wrap gap-3 mb-2">
        <div class="stat-badge">
          <span class="stat-label">UnifiedScore</span>
          <span class="stat-value text-blue-600 dark:text-blue-400">{{ results.analyst.unified_score }}</span>
        </div>
        <div class="stat-badge">
          <span class="stat-label">竞争程度</span>
          <span class="stat-value"
            :class="results.analyst.competition_level === 'low' ? 'text-emerald-600' : results.analyst.competition_level === 'medium' ? 'text-amber-600' : 'text-red-600'"
          >{{ results.analyst.competition_level }}</span>
        </div>
      </div>
      <p v-if="results.analyst.insight" class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed italic">
        {{ results.analyst.insight }}
      </p>
    </div>

    <!-- Linguistic -->
    <div v-if="results.linguistic" class="result-card">
      <h4 class="result-title">✍️ Linguistic 文案</h4>
      <div class="space-y-2">
        <div v-if="results.linguistic.seo_title || results.linguistic.title_seo">
          <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">SEO 标题</p>
          <div v-for="(t, i) in asList(results.linguistic.seo_title || results.linguistic.title_seo)" :key="i"
               class="text-xs bg-slate-50 dark:bg-slate-800 rounded p-2 border-l-2 border-blue-400">
            {{ t }}
          </div>
        </div>
        <div v-if="results.linguistic.short_description">
          <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">简短描述</p>
          <p class="text-xs text-slate-700 dark:text-slate-300">{{ results.linguistic.short_description }}</p>
        </div>
      </div>
    </div>

    <!-- Creative -->
    <div v-if="results.creative" class="result-card">
      <h4 class="result-title">🎨 Creative 创意</h4>
      <div class="space-y-2">
        <div v-if="results.creative.image_prompt">
          <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">图像 Prompt</p>
          <p class="text-xs bg-slate-50 dark:bg-slate-800 rounded p-2 text-slate-700 dark:text-slate-300">
            {{ results.creative.image_prompt }}
          </p>
        </div>
        <div v-if="results.creative.urls && results.creative.urls.length">
          <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">生成图片</p>
          <div class="flex flex-wrap gap-2">
            <img v-for="(url, i) in results.creative.urls" :key="i"
                 :src="url" class="h-32 rounded-lg object-cover shadow" alt="generated" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.result-card {
  @apply rounded-xl border border-slate-200 dark:border-slate-700 p-4 bg-white dark:bg-slate-800/60;
}
.result-title {
  @apply text-sm font-semibold text-slate-800 dark:text-slate-100 mb-3;
}
.result-pre {
  @apply text-xs bg-slate-50 dark:bg-slate-900 rounded-lg p-3 overflow-x-auto text-slate-600 dark:text-slate-400 max-h-40;
}
.stat-badge {
  @apply flex flex-col items-center bg-slate-50 dark:bg-slate-900 rounded-lg px-3 py-2 min-w-[80px];
}
.stat-label { @apply text-xs text-slate-400 mb-1; }
.stat-value { @apply text-sm font-bold; }
</style>

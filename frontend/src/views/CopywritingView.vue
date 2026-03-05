<script setup lang="ts">
import { ref } from "vue"

const productName = ref("Ozon 智能猫砂盆")
const keywords = ref("除臭, 自动铲屎, 静音, APP远程")
const language = ref("Russian (俄语)")
const tone = ref("专业严谨")
const loading = ref(false)
const result = ref<any>(null)

const generateCopy = () => {
  loading.value = true
  setTimeout(() => {
    result.value = {
      title: "Автоматический лоток для кошек Ozon Smart Clean с управлением через приложение | Умный туалет с ионизацией",
      description: "Забудьте о неприятном запахе и ежедневной уборке! Умный лоток Ozon Smart Clean оснащен системой автоматической очистки и ионизации воздуха. \n\n✅ УПРАВЛЕНИЕ СО СМАРТФОНА: Следите за здоровьем питомца и настраивайте график уборки.\n✅ БЕЗОПАСНОСТЬ: 5 уровней защиты, инфракрасные датчики мгновенно останавливают работу при приближении кошки.\n✅ ТИХАЯ РАБОТА: Уровень шума менее 35 дБ, не пугает животных.\n\nИдеально подходит для кошек весом от 1.5 до 10 кг.",
      tags: ["товары для животных", "умный дом", "кошачий туалет", "ozon", "автоматический лоток"]
    }
    loading.value = false
  }, 2000)
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 p-8 font-sans transition-colors duration-300">
    <header class="mb-8 flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-slate-900 dark:text-white">AI 营销文案 (Copywriting)</h1>
        <p class="text-slate-500 dark:text-slate-400 mt-1">GPT-4 Turbo 驱动 · SEO 优化与多语言适配</p>
      </div>
      <div class="flex gap-3">
        <span class="px-3 py-1 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 text-xs font-bold rounded-full border border-emerald-100 dark:border-emerald-800">剩 450 Credits</span>
      </div>
    </header>

    <div class="grid grid-cols-12 gap-8 h-[600px]">
      <!-- Input Panel -->
      <div class="col-span-5 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-8 shadow-sm flex flex-col transition-colors duration-300">
        <div class="space-y-6 flex-1">
          <label class="block">
            <span class="text-sm font-bold text-slate-700 dark:text-slate-300 block mb-2">商品名称</span>
            <input v-model="productName" class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/20" placeholder="输入商品核心名称...">
          </label>

          <label class="block">
            <span class="text-sm font-bold text-slate-700 dark:text-slate-300 block mb-2">核心关键词 / 卖点</span>
            <textarea v-model="keywords" rows="4" class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-white resize-none focus:outline-none focus:ring-2 focus:ring-emerald-500/20" placeholder="例如：防水, 耐磨, 适合户外..."></textarea>
          </label>

          <div class="grid grid-cols-2 gap-4">
            <label class="block">
              <span class="text-sm font-bold text-slate-700 dark:text-slate-300 block mb-2">目标语言</span>
              <select v-model="language" class="w-full px-4 py-3 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-white focus:outline-none">
                <option>Russian (俄语)</option>
                <option>English (英语)</option>
                <option>Chinese (中文)</option>
              </select>
            </label>
            <label class="block">
              <span class="text-sm font-bold text-slate-700 dark:text-slate-300 block mb-2">文案风格</span>
              <select v-model="tone" class="w-full px-4 py-3 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-white focus:outline-none">
                <option>专业严谨</option>
                <option>种草亲和</option>
                <option>促销紧迫</option>
              </select>
            </label>
          </div>
        </div>

        <button 
          @click="generateCopy" 
          :disabled="loading"
          class="w-full py-4 mt-8 bg-slate-900 dark:bg-emerald-600 text-white font-bold rounded-xl hover:bg-slate-800 dark:hover:bg-emerald-700 transition-all active:scale-[0.98] disabled:opacity-70 flex items-center justify-center gap-2"
        >
          <span v-if="loading" class="animate-spin w-4 h-4 border-2 border-white/30 border-t-white rounded-full"></span>
          <span>{{ loading ? '正在撰写...' : '生成 SEO 文案' }}</span>
        </button>
      </div>

      <!-- Result Panel -->
      <div class="col-span-7 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-8 shadow-sm overflow-y-auto relative transition-colors duration-300">
        <div v-if="result" class="space-y-8 animate-fade-in">
          
          <!-- Title -->
          <div class="group relative">
            <div class="flex justify-between items-center mb-2">
               <span class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase">SEO Title (标题)</span>
               <button class="text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-300 text-xs font-bold opacity-0 group-hover:opacity-100 transition-opacity">复制内容</button>
            </div>
            <div class="p-4 bg-slate-50 dark:bg-slate-700/50 border border-slate-100 dark:border-slate-600 rounded-xl text-lg font-bold text-slate-900 dark:text-white leading-snug">
              {{ result.title }}
            </div>
          </div>

          <!-- Description -->
          <div class="group relative">
            <div class="flex justify-between items-center mb-2">
               <span class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase">Product Description (详情)</span>
               <button class="text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-300 text-xs font-bold opacity-0 group-hover:opacity-100 transition-opacity">复制内容</button>
            </div>
            <div class="p-6 bg-slate-50 dark:bg-slate-700/50 border border-slate-100 dark:border-slate-600 rounded-xl text-sm text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-wrap">
              {{ result.description }}
            </div>
          </div>

          <!-- Tags -->
          <div>
            <div class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase mb-2">Keywords (标签)</div>
            <div class="flex flex-wrap gap-2">
              <span v-for="tag in result.tags" :key="tag" class="px-3 py-1.5 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 rounded-lg text-sm font-medium border border-emerald-100 dark:border-emerald-800">
                #{{ tag }}
              </span>
            </div>
          </div>

        </div>

        <div v-else class="h-full flex flex-col items-center justify-center text-slate-400 dark:text-slate-600">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mb-4 opacity-20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
          <p class="font-bold text-lg text-slate-500 dark:text-slate-400">文案生成就绪</p>
          <p class="text-sm mt-2 opacity-60">请在左侧填写商品信息，AI 将自动生成符合平台规范的文案</p>
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

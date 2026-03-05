<script setup lang="ts">
import { ref } from "vue"

const prompt = ref("Ошейник для кошек со стразами (镶钻猫项圈)")
const aspectRatio = ref("1:1")
const style = ref("摄影写实")
const loading = ref(false)
const generatedImages = ref<string[]>([])

const generate = () => {
  loading.value = true
  setTimeout(() => {
    generatedImages.value = [
      "https://images.unsplash.com/photo-1574158622682-e40e69881006?auto=format&fit=crop&q=80&w=600",
      "https://images.unsplash.com/photo-1615751072497-5f5169febe17?auto=format&fit=crop&q=80&w=600",
      "https://images.unsplash.com/photo-1605639156481-244775d6f803?auto=format&fit=crop&q=80&w=600",
      "https://images.unsplash.com/photo-1548802673-380ab8ebc7b7?auto=format&fit=crop&q=80&w=600"
    ]
    loading.value = false
  }, 3000)
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 p-8 font-sans transition-colors duration-300">
    <header class="mb-8 flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-slate-900 dark:text-white">AI 商品生图 (Image Gen)</h1>
        <p class="text-slate-500 dark:text-slate-400 mt-1">Midjourney v6 模型驱动 · 电商场景化主图生成</p>
      </div>
      <div class="flex gap-3">
        <span class="px-3 py-1 bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 text-xs font-bold rounded-full border border-purple-100 dark:border-purple-800">剩 150 Credits</span>
      </div>
    </header>

    <div class="flex gap-8 h-[600px]">
      <!-- Control Panel -->
      <div class="w-1/3 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 flex flex-col shadow-sm transition-colors duration-300">
        <div class="space-y-6 flex-1">
          <label class="block">
            <span class="text-sm font-bold text-slate-700 dark:text-slate-300 block mb-2">画面描述 (Prompt)</span>
            <textarea 
              v-model="prompt" 
              class="w-full h-32 px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-white resize-none focus:outline-none focus:ring-2 focus:ring-purple-500/20"
              placeholder="输入俄语或中文描述..."
            ></textarea>
          </label>

          <div class="grid grid-cols-2 gap-4">
            <label class="block">
              <span class="text-sm font-bold text-slate-700 dark:text-slate-300 block mb-2">图片比例</span>
              <select v-model="aspectRatio" class="w-full px-4 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-white focus:outline-none">
                <option>1:1 (主图)</option>
                <option>3:4 (详情)</option>
                <option>9:16 (Story)</option>
              </select>
            </label>
            <label class="block">
              <span class="text-sm font-bold text-slate-700 dark:text-slate-300 block mb-2">风格预设</span>
              <select v-model="style" class="w-full px-4 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-white focus:outline-none">
                <option>摄影写实</option>
                <option>3D 渲染</option>
                <option>插画风格</option>
              </select>
            </label>
          </div>
          
          <div class="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-xl border border-purple-100 dark:border-purple-800 text-xs text-purple-800 dark:text-purple-300 leading-relaxed">
            <strong>提示：</strong> 包含具体的材质（如丝绸、皮革）、光线（自然光、影棚光）和背景描述（纯色、生活场景）效果更佳。
          </div>
        </div>

        <button 
          @click="generate" 
          :disabled="loading"
          class="w-full py-4 mt-6 bg-slate-900 dark:bg-purple-600 text-white font-bold rounded-xl hover:bg-slate-800 dark:hover:bg-purple-700 transition-all active:scale-[0.98] disabled:opacity-70 flex items-center justify-center gap-2"
        >
          <span v-if="loading" class="animate-spin w-4 h-4 border-2 border-white/30 border-t-white rounded-full"></span>
          <span>{{ loading ? '生成中...' : '立即生成 (消耗 4 Credits)' }}</span>
        </button>
      </div>

      <!-- Result Gallery -->
      <div class="flex-1 bg-slate-100 dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 overflow-y-auto transition-colors duration-300">
        <div v-if="generatedImages.length > 0" class="grid grid-cols-2 gap-6">
          <div v-for="(img, i) in generatedImages" :key="i" class="group relative aspect-square bg-white dark:bg-slate-700 rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition-all cursor-zoom-in">
            <img :src="img" class="w-full h-full object-cover" />
            <div class="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex justify-end gap-2">
              <button class="p-2 bg-white/20 backdrop-blur-md rounded-lg text-white hover:bg-white hover:text-slate-900 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
              </button>
            </div>
          </div>
        </div>
        <div v-else class="h-full flex flex-col items-center justify-center text-slate-400 dark:text-slate-600">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mb-4 opacity-20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
          <p>暂无生成记录，请在左侧输入描述开始创作</p>
        </div>
      </div>
    </div>
  </div>
</template>

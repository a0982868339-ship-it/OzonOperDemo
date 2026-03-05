<script setup lang="ts">
import { ref } from "vue"
import axios from "axios"

const basePrompt = ref("智能猫砂盆 自动清理 除臭 APP控制")
const duration = ref("15s")
const style = ref("cinematic")
const loading = ref(false)
const result = ref<any>(null)
const error = ref("")

const styleOptions = [
  { value: "cinematic", label: "电影感" },
  { value: "minimal", label: "简约白底" },
  { value: "energetic", label: "活力快剪" },
  { value: "lifestyle", label: "生活场景" },
]

const generateVideo = async () => {
  if (!basePrompt.value.trim()) return
  loading.value = true
  error.value = ""
  result.value = null

  try {
    const res = await axios.post("/ai/video", {
      base_prompt: basePrompt.value,
      duration: duration.value,
      style: style.value,
      platform: "Ozon",
    })
    result.value = res.data
  } catch (e: any) {
    error.value = e?.response?.data?.detail || "生成失败，请检查 AI 配置"
  } finally {
    loading.value = false
  }
}

const copyText = (text: string) => {
  navigator.clipboard.writeText(text)
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 p-8 font-sans transition-colors duration-300">
    <header class="mb-8">
      <h1 class="text-3xl font-bold text-slate-900 dark:text-white">AI 视频 Prompt 生成</h1>
      <p class="text-slate-500 dark:text-slate-400 mt-1">LLM 驱动 · 电商短视频 Prompt 增强 · 适配 Runway / Sora / Kling</p>
    </header>

    <div class="grid grid-cols-12 gap-8">
      <!-- 控制面板 -->
      <div class="col-span-4 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 flex flex-col shadow-sm">
        <div class="space-y-5 flex-1">
          <label class="block">
            <span class="text-sm font-bold text-slate-700 dark:text-slate-300 block mb-2">商品/场景描述</span>
            <textarea
              v-model="basePrompt"
              rows="4"
              class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-white resize-none focus:outline-none focus:ring-2 focus:ring-amber-500/30"
              placeholder="例：智能猫砂盆，白色简约外观，猫咪正在使用..."
            ></textarea>
          </label>

          <div class="grid grid-cols-2 gap-4">
            <label class="block">
              <span class="text-sm font-bold text-slate-700 dark:text-slate-300 block mb-2">时长</span>
              <select v-model="duration" class="w-full px-3 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-white focus:outline-none">
                <option value="5s">5s (GIF)</option>
                <option value="15s">15s (Story)</option>
                <option value="30s">30s (广告)</option>
                <option value="60s">60s (详情页)</option>
              </select>
            </label>
            <label class="block">
              <span class="text-sm font-bold text-slate-700 dark:text-slate-300 block mb-2">视觉风格</span>
              <select v-model="style" class="w-full px-3 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-white focus:outline-none">
                <option v-for="o in styleOptions" :key="o.value" :value="o.value">{{ o.label }}</option>
              </select>
            </label>
          </div>

          <div v-if="error" class="px-4 py-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-xl text-sm">
            {{ error }}
          </div>
        </div>

        <button
          @click="generateVideo"
          :disabled="loading || !basePrompt.trim()"
          class="w-full py-4 mt-6 bg-slate-900 dark:bg-amber-600 text-white font-bold rounded-xl hover:bg-slate-800 dark:hover:bg-amber-700 transition-all active:scale-[0.98] disabled:opacity-50 flex items-center justify-center gap-2"
        >
          <span v-if="loading" class="animate-spin w-4 h-4 border-2 border-white/30 border-t-white rounded-full"></span>
          <span>{{ loading ? 'AI 正在增强 Prompt...' : '生成视频 Prompt' }}</span>
        </button>
      </div>

      <!-- 结果区域 -->
      <div class="col-span-8 space-y-4">
        <!-- 等待状态 -->
        <div v-if="!result && !loading" class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-16 flex flex-col items-center justify-center text-slate-400 dark:text-slate-600 shadow-sm">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-20 w-20 mb-4 opacity-20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
          <p class="font-bold text-lg text-slate-500 dark:text-slate-400">填写描述，AI 为你生成专业视频 Prompt</p>
          <p class="text-sm mt-1 opacity-60">支持中文输入，输出英文专业 Prompt 供 Runway / Sora / Kling 使用</p>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-16 flex flex-col items-center justify-center shadow-sm">
          <div class="w-16 h-16 border-4 border-amber-500/30 border-t-amber-500 rounded-full animate-spin mx-auto mb-6"></div>
          <div class="text-amber-500 font-mono text-sm tracking-widest animate-pulse">LLM ENHANCING PROMPT...</div>
        </div>

        <!-- 结果 -->
        <template v-if="result">
          <!-- 主 Prompt -->
          <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm group">
            <div class="flex justify-between items-center mb-3">
              <span class="text-xs font-bold text-amber-600 dark:text-amber-400 uppercase tracking-wider">Enhanced Video Prompt</span>
              <button @click="copyText(result.enhanced_prompt)" class="text-xs font-bold text-slate-400 hover:text-amber-500 transition-colors px-3 py-1 rounded-lg hover:bg-amber-50 dark:hover:bg-amber-900/20">
                复制
              </button>
            </div>
            <p class="text-sm text-slate-700 dark:text-slate-300 leading-relaxed font-mono bg-slate-50 dark:bg-slate-700/50 p-4 rounded-xl">{{ result.enhanced_prompt }}</p>
          </div>

          <!-- 分镜脚本 -->
          <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
            <div class="flex justify-between items-center mb-3">
              <span class="text-xs font-bold text-blue-600 dark:text-blue-400 uppercase tracking-wider">Shot List 分镜脚本</span>
              <button @click="copyText(result.shot_list?.join('\n'))" class="text-xs font-bold text-slate-400 hover:text-blue-500 transition-colors px-3 py-1 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20">
                复制全部
              </button>
            </div>
            <div class="space-y-2">
              <div
                v-for="(shot, i) in result.shot_list"
                :key="i"
                class="text-sm text-slate-700 dark:text-slate-300 py-2 px-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg font-mono"
              >{{ shot }}</div>
            </div>
          </div>

          <!-- 俄语旁白 -->
          <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
            <div class="flex justify-between items-center mb-3">
              <span class="text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">Narration 俄语旁白</span>
              <button @click="copyText(result.narration_ru)" class="text-xs font-bold text-slate-400 hover:text-emerald-500 transition-colors px-3 py-1 rounded-lg hover:bg-emerald-50 dark:hover:bg-emerald-900/20">
                复制
              </button>
            </div>
            <p class="text-sm text-slate-700 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-700/50 p-4 rounded-xl">{{ result.narration_ru }}</p>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

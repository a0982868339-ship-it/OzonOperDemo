<script setup lang="ts">
import { computed, reactive } from "vue"
import { useTaskStore } from "../stores/tasks"
import type { TaskItem } from "../types"

const taskStore = useTaskStore()

const formState = reactive({
  name: "",
  features: "",
  style: ""
})

const latestMedia = computed(() => taskStore.tasks.find((task: TaskItem) => task.type === "media"))
const latestSeo = computed(() => taskStore.tasks.find((task: TaskItem) => task.type === "seo"))

const submit = async () => {
  const basePrompt = `${formState.name} ${formState.features} ${formState.style}`.trim()
  if (!basePrompt) return
  await taskStore.createMediaTask({ base_prompt: basePrompt })
  await taskStore.createSeoTask({
    product_name: formState.name || "Новый продукт",
    category: "Creative Studio"
  })
}
</script>

<template>
  <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
    <div class="flex items-center justify-between mb-4">
      <div>
        <h2 class="text-lg font-semibold">AI 创意工坊</h2>
        <p class="text-sm text-slate-500">生成俄语素材，实时查看状态</p>
      </div>
      <el-tag type="info">AI 任务流水线</el-tag>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="space-y-4">
        <el-form label-position="top" class="space-y-4">
          <el-form-item label="商品名称">
            <el-input v-model="formState.name" placeholder="例如：智能喂食器" />
          </el-form-item>
          <el-form-item label="卖点/特性">
            <el-input v-model="formState.features" placeholder="静音、自动补给、智能定时" />
          </el-form-item>
          <el-form-item label="风格">
            <el-input v-model="formState.style" placeholder="现代、冬季温馨内饰" />
          </el-form-item>
        </el-form>
        <el-button type="primary" class="w-full" @click="submit">生成素材</el-button>
        <div v-if="latestSeo?.result" class="rounded-xl border border-slate-200 p-4 bg-slate-50 text-sm">
          <div class="font-semibold text-slate-700 mb-2">SEO 文案草稿</div>
          <div class="font-medium text-slate-900">{{ latestSeo.result.title_seo }}</div>
          <div class="text-slate-600 mt-1">{{ latestSeo.result.short_description }}</div>
          <ul class="list-disc ml-4 mt-2 text-slate-600">
            <li v-for="point in latestSeo.result.bullet_points_ru" :key="point">{{ point }}</li>
          </ul>
        </div>
      </div>

      <div class="rounded-xl border border-slate-200 p-4 bg-slate-50 min-h-[320px]">
        <div class="text-sm font-semibold text-slate-700">预览</div>
        <div v-if="latestMedia?.status === 'GENERATING' || latestMedia?.status === 'PENDING'" class="mt-4">
          <el-skeleton :rows="4" animated />
        </div>
        <div v-else-if="latestMedia?.status === 'COMPLETED'" class="mt-4 space-y-3">
          <div class="text-xs text-slate-500">提示词: {{ latestMedia.result?.prompt_text }}</div>
          <div class="grid grid-cols-2 gap-2">
            <template v-for="url in latestMedia.result?.urls" :key="url">
              <img v-if="!String(url).endsWith('.mp4')" :src="String(url)" class="rounded-lg" />
              <video v-else controls class="rounded-lg">
                <source :src="String(url)" />
              </video>
            </template>
          </div>
        </div>
        <div v-else class="mt-4 text-sm text-slate-400">暂无素材，请开始生成任务。</div>
      </div>
    </div>
  </div>
</template>

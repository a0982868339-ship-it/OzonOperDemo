<script setup lang="ts">
import { RouterLink, useRoute, useRouter } from "vue-router"
import { useUserStore } from "../stores/user"
import { computed, ref, watch } from "vue"
import { storeToRefs } from "pinia"
import { useThemeStore } from "../stores/theme"

const themeStore = useThemeStore()
const { isDark } = storeToRefs(themeStore)

const user = useUserStore()
const route = useRoute()
const router = useRouter()

// Track expanded menus
const expandedMenus = ref<string[]>([])

interface MenuItem {
  name: string
  path: string
  icon: string
  children?: MenuItem[]
}

// Modern SaaS Icons (Stroke based, clean)
const icons = {
  dashboard: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" /></svg>`,
  stars: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" /></svg>`,
  radar: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" /></svg>`, // Bolt icon for radar/activity
  creative: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" /></svg>`,
  task: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M6 6.878V6a2.25 2.25 0 012.25-2.25h7.5A2.25 2.25 0 0118 6v.878m-12 0c.235-.083.487-.128.75-.128h10.5c.263 0 .515.045.75.128m-12 0A2.25 2.25 0 004.5 9v.878m13.5-3A2.25 2.25 0 0119.5 9v.878m0 0a2.246 2.246 0 00-.75-.128H5.25c-.263 0-.515.045-.75.128m15 0A2.25 2.25 0 0121 12v6a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 18v-6c0-.98.626-1.813 1.5-2.122" /></svg>`,
  analysis: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" /></svg>`,
  image: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" /></svg>`,
  video: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 10.5l4.72-4.72a.75.75 0 011.28.53v11.38a.75.75 0 01-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 002.25-2.25v-9a2.25 2.25 0 00-2.25-2.25h-9A2.25 2.25 0 002.25 7.5v9a2.25 2.25 0 002.25 2.25z" /></svg>`,
  copy: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" /></svg>`,
  settings: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>`,
  // Sub-menu icons
  ai: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12h1.5m12 0h1.5m-1.5 3.75h1.5m-1.5 3.75h-1.5m-12 0h-1.5m7.5-3.75h1.5M12 3v2.25m0 13.5V21M6 7.5l2.25 2.25m13.5-2.25L15.75 7.5M6 16.5l2.25-2.25m13.5 2.25L15.75 16.5" /></svg>`,
  user: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" /></svg>`,
  chart: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4"><path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" /></svg>`,
  chevron: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-3 h-3"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" /></svg>`,
  key: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 5.25a3 3 0 013 3m3 0a6 6 0 01-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1121.75 8.25z" /></svg>`,
  notice: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4"><path stroke-linecap="round" stroke-linejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" /></svg>`,
  audit: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25zM6.75 12h.008v.008H6.75V12zm0 3h.008v.008H6.75V15zm0 3h.008v.008H6.75V18z" /></svg>`,
  info: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4"><path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" /></svg>`,
  prompt: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4"><path stroke-linecap="round" stroke-linejoin="round" d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5" /></svg>`
}

const menus = computed<MenuItem[]>(() => {
  const items: MenuItem[] = [
    { name: "仪表盘", path: "/", icon: icons.dashboard },
    { name: "任务指挥台", path: "/mission", icon: icons.stars },
    { name: "选品雷达", path: "/market-radar", icon: icons.radar }, // Added Market Radar
    { name: "数据选品", path: "/analysis", icon: icons.analysis },
    { 
      name: "AI 创作工具", 
      path: "/tools", // Virtual parent
      icon: icons.task,
      children: [
        { name: "文案生成", path: "/copywriting", icon: icons.copy },
        { name: "商品生图", path: "/image-gen", icon: icons.image },
        { name: "视频生成", path: "/video-gen", icon: icons.video },
      ]
    },
    { name: "任务中心", path: "/task-center", icon: icons.task }
  ]
  if (user.role === "admin") {
    items.push({
      name: "系统设置",
      path: "/admin", // Parent path
      icon: icons.settings,
      children: [
        { name: "AI 代理配置", path: "/admin/configs",     icon: icons.ai },
        { name: "提示词工程", path: "/admin/prompts",      icon: icons.prompt },
        { name: "环境配置",   path: "/admin/env-config",  icon: icons.key },
        { name: "用户管理",   path: "/admin/users",        icon: icons.user },
        { name: "用量统计",   path: "/admin/usage",        icon: icons.chart },
        { name: "系统公告",   path: "/admin/notices",      icon: icons.notice },
        { name: "审计日志",   path: "/admin/audit-log",    icon: icons.audit },
        { name: "系统信息",   path: "/admin/system-info",  icon: icons.info },
      ]
    })
  }
  return items
})

const handleLogout = () => {
  user.setToken(null)
  router.push("/login")
}

const isExpanded = (item: MenuItem) => {
  if (!item.children) return false
  return expandedMenus.value.includes(item.path)
}

const toggleExpand = (item: MenuItem) => {
  if (!item.children) return
  
  const index = expandedMenus.value.indexOf(item.path)
  if (index === -1) {
    expandedMenus.value.push(item.path)
  } else {
    expandedMenus.value.splice(index, 1)
  }
}

// Automatically expand menu if current route is a child
watch(() => route.path, (newPath) => {
  menus.value.forEach(item => {
    if (item.children) {
      const hasActiveChild = item.children.some(child => newPath.startsWith(child.path)) || newPath.startsWith(item.path + '/')
      if (hasActiveChild && !expandedMenus.value.includes(item.path)) {
        expandedMenus.value.push(item.path)
      }
    }
  })
}, { immediate: true })
</script>

<template>
  <aside class="w-64 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 flex flex-col border-r border-slate-200 dark:border-slate-800 relative z-20 transition-colors duration-300">
    <!-- Brand -->
    <div class="px-6 py-8">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center text-white shadow-lg shadow-blue-200 dark:shadow-blue-900/20">
          <span class="text-xl font-bold">O</span>
        </div>
        <div>
          <div class="text-xl font-bold text-slate-900 dark:text-white tracking-wide">OZON</div>
          <div class="text-[10px] text-slate-400 dark:text-slate-500 font-mono uppercase tracking-[0.2em]">AI 智能运营</div>
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-4 space-y-1">
      <template v-for="item in menus" :key="item.path">
        
        <!-- Standard Menu Item -->
        <RouterLink
          v-if="!item.children"
          :to="item.path"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group"
          :class="route.path === item.path 
            ? 'bg-slate-900 dark:bg-blue-600 text-white shadow-md shadow-slate-200 dark:shadow-blue-900/20' 
            : 'text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-200'"
        >
          <span class="w-5 h-5 transition-colors duration-200" v-html="item.icon"></span>
          <span>{{ item.name }}</span>
          
          <span v-if="route.path === item.path" class="ml-auto w-1.5 h-1.5 rounded-full bg-white/30"></span>
        </RouterLink>

        <!-- Parent Menu Item -->
        <div v-else class="space-y-1 pt-4">
          <div class="px-3 text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-2">{{ item.name }}</div>
          
          <RouterLink
            v-for="sub in item.children"
            :key="sub.path"
            :to="sub.path"
            class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 group ml-2"
            :class="route.path === sub.path 
              ? 'bg-blue-50 dark:bg-slate-800 text-blue-700 dark:text-blue-400' 
              : 'text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-200'"
          >
            <span class="w-4 h-4 opacity-70" v-html="sub.icon"></span>
            <span>{{ sub.name }}</span>
          </RouterLink>
        </div>

      </template>
    </nav>

    <!-- Footer -->
    <div class="p-4 mt-auto space-y-4">
      
      <!-- User Profile & Theme Toggle -->
      <div class="bg-slate-50 dark:bg-slate-800 rounded-xl p-4 border border-slate-100 dark:border-slate-700 transition-colors duration-300">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-lg font-bold text-slate-600 dark:text-slate-300">
              {{ user.role === 'admin' ? 'A' : 'U' }}
            </div>
            <div>
              <div class="text-sm font-bold text-slate-900 dark:text-white">Admin User</div>
              <div class="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold uppercase tracking-wider bg-emerald-100 dark:bg-emerald-900/30 px-1.5 py-0.5 rounded w-fit">
                {{ user.role === 'admin' ? 'Super Admin' : 'User' }}
              </div>
            </div>
          </div>
        </div>

        <button
          @click="themeStore.toggleTheme()"
          class="w-full flex items-center justify-between px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-700 dark:text-slate-200 font-semibold hover:bg-slate-50 dark:hover:bg-slate-600 transition-colors"
        >
          <span>主题切换</span>
          <span class="flex items-center gap-2 text-xs font-bold">
            <span v-if="isDark">🌙 深色</span>
            <span v-else>☀️ 浅色</span>
          </span>
        </button>

        <button @click="handleLogout" class="flex items-center gap-2 text-xs font-bold text-slate-500 dark:text-slate-400 hover:text-red-500 dark:hover:text-red-400 transition-colors w-full">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" /></svg>
          <span>退出登录</span>
        </button>
      </div>

      <!-- System Status -->
      <div class="px-2 flex items-center justify-between text-[10px] text-slate-400 dark:text-slate-600 font-mono">
        <div class="flex items-center gap-1.5">
          <span class="relative flex h-1.5 w-1.5">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-1.5 w-1.5 bg-green-500"></span>
          </span>
          <span>SYSTEM ONLINE</span>
        </div>
        <span>v1.2.0</span>
      </div>

    </div>
  </aside>
</template>

<style scoped>
/* No specific styles needed, Tailwind handles it */
</style>

<script setup lang="ts">
import { RouterView, useRoute } from "vue-router"
import Sidebar from "./components/Sidebar.vue"
import { computed } from "vue"
import { useThemeStore } from "./stores/theme"

// Initialize theme store to activate dark/light mode logic immediately
const themeStore = useThemeStore()

const route = useRoute()
const showSidebar = computed(() => route.path !== "/login")
</script>

<template>
  <div
    class="flex h-screen bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 font-inter selection:bg-blue-100 dark:selection:bg-blue-900 selection:text-blue-900 dark:selection:text-blue-100 transition-colors duration-300 overflow-hidden"
    :class="themeStore.isDark ? 'dark' : 'light'"
  >
    <!-- Sidebar is now sticky/fixed within the flex container -->
    <Sidebar v-if="showSidebar" class="flex-shrink-0 h-full overflow-y-auto" />

    <!-- Main Content Area scrolls independently -->
    <main class="flex-1 h-full overflow-y-auto" :class="{ 'p-8': showSidebar }">
      <div v-if="showSidebar" class="max-w-7xl mx-auto pb-12">
        <RouterView />
      </div>
      <RouterView v-else />
    </main>
  </div>
</template>

<style>
/* Global Premium Styles */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --el-color-primary: #0f172a; /* slate-900 */
  --el-bg-color: #ffffff;
  --el-text-color-primary: #0f172a;
  --el-border-color: #e2e8f0;
}

html.dark {
  --el-color-primary: #f8fafc; /* slate-50 */
  --el-bg-color: #0f172a; /* slate-900 */
  --el-text-color-primary: #f8fafc;
  --el-border-color: #334155; /* slate-700 */
  --el-fill-color-blank: #1e293b; /* slate-800 input bg */
}

body {
  @apply bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 transition-colors duration-300;
  -webkit-font-smoothing: antialiased;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

h1, h2, h3 {
  font-weight: 600;
  letter-spacing: -0.025em;
  @apply text-slate-900 dark:text-white;
}

.font-inter {
  font-family: 'Inter', sans-serif;
}

/* Customizing Element Plus for Modern SaaS Theme */
.el-button--primary {
  --el-button-bg-color: #0f172a !important;
  --el-button-border-color: #0f172a !important;
  --el-button-hover-bg-color: #334155 !important;
  --el-button-hover-border-color: #334155 !important;
  
  /* Dark mode overrides for primary button */
  html.dark & {
    --el-button-bg-color: #3b82f6 !important; /* blue-500 */
    --el-button-border-color: #3b82f6 !important;
    --el-button-hover-bg-color: #2563eb !important; /* blue-600 */
    --el-button-hover-border-color: #2563eb !important;
    color: #ffffff !important;
  }

  border-radius: 8px !important;
  font-weight: 500 !important;
  letter-spacing: normal !important;
  text-transform: none !important;
}

.el-input__wrapper {
  background-color: #fff !important;
  box-shadow: 0 0 0 1px #e2e8f0 inset !important; /* slate-200 */
  border-radius: 8px !important;
}

html.dark .el-input__wrapper {
  background-color: #1e293b !important; /* slate-800 */
  box-shadow: 0 0 0 1px #334155 inset !important; /* slate-700 */
}

.el-input__wrapper.is-focus {
  box-shadow: 0 0 0 2px #0f172a inset !important;
}

html.dark .el-input__wrapper.is-focus {
  box-shadow: 0 0 0 2px #3b82f6 inset !important; /* blue-500 */
}
</style>

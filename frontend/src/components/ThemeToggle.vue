<script setup lang="ts">
import { useThemeStore } from '../stores/theme'
import { computed } from 'vue'

const themeStore = useThemeStore()

const toggle = () => {
  themeStore.toggleTheme()
}

// Icon paths
const sunPath = "M12 3v1.5M12 19.5V21M4.22 4.22l1.06 1.06M18.72 18.72l1.06 1.06M3 12h1.5M19.5 12H21M4.22 19.78l1.06-1.06M18.72 5.28l1.06-1.06M12 8a4 4 0 100 8 4 4 0 000-8z"
const moonPath = "M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z"
</script>

<template>
  <button 
    @click="toggle"
    class="relative w-12 h-6 rounded-full bg-slate-200 dark:bg-slate-700 transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:focus:ring-offset-slate-900"
    title="Toggle Theme"
  >
    <span class="sr-only">Toggle Dark Mode</span>
    <span
      class="absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white dark:bg-slate-800 shadow-md transform transition-transform duration-300 flex items-center justify-center"
      :class="themeStore.isDark ? 'translate-x-6' : 'translate-x-0'"
    >
      <svg 
        v-if="!themeStore.isDark" 
        xmlns="http://www.w3.org/2000/svg" 
        fill="none" 
        viewBox="0 0 24 24" 
        stroke-width="2" 
        stroke="currentColor" 
        class="w-3 h-3 text-amber-500 animate-spin-slow"
      >
        <path stroke-linecap="round" stroke-linejoin="round" :d="sunPath" />
      </svg>
      <svg 
        v-else 
        xmlns="http://www.w3.org/2000/svg" 
        fill="currentColor" 
        viewBox="0 0 24 24" 
        class="w-3 h-3 text-indigo-400"
      >
        <path stroke-linecap="round" stroke-linejoin="round" :d="moonPath" />
      </svg>
    </span>
  </button>
</template>

<style scoped>
.animate-spin-slow {
  animation: spin 3s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>

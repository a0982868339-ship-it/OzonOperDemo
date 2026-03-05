import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const getInitialTheme = () => {
    const saved = localStorage.getItem('ozon-theme-preference')
    if (saved) return saved === 'dark'
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  }

  const isDark = ref(getInitialTheme())
  const echartsTheme = ref(isDark.value ? 'dark' : 'light')

  const applyTheme = (dark: boolean) => {
    const html = document.documentElement
    const body = document.body
    html.classList.toggle('dark', dark)
    html.classList.toggle('light', !dark)
    body.classList.toggle('dark', dark)
    body.classList.toggle('light', !dark)
    echartsTheme.value = dark ? 'dark' : 'light'
    localStorage.setItem('ozon-theme-preference', dark ? 'dark' : 'light')
    window.dispatchEvent(new Event('theme-changed'))
  }

  const setTheme = (dark: boolean) => {
    isDark.value = dark
    applyTheme(dark)
  }

  const toggleTheme = () => {
    setTheme(!isDark.value)
  }

  setTheme(isDark.value)

  return {
    isDark,
    toggleTheme,
    echartsTheme
  }
})

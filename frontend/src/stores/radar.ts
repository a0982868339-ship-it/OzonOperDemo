import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiGet } from '../api/client'

export interface RadarWord {
  name: string
  value: number
  growth_rate: number
  source: 'ozon' | 'vk' | 'mixed'
  platform: string[] // List of platforms this word appears on
  category?: string
}

export const useRadarStore = defineStore('radar', () => {
  // Platform Filters
  const platforms = ref([
    { name: 'VK', active: true, color: '#0077FF' },
    { name: 'OK', active: true, color: '#F2720C' },
    { name: 'YouTube', active: true, color: '#FF0000' },
    { name: 'Ozon', active: true, color: '#005BFF' },
    { name: 'WB', active: true, color: '#CB11AB' },
    { name: 'Yandex', active: true, color: '#FC3F1D' }
  ])

  // Mock Data (In reality, this would come from Analyst Agent backend)
  const rawWords = ref<RadarWord[]>([
    { name: 'Умная кормушка', value: 95, growth_rate: 1.2, source: 'mixed', platform: ['Ozon', 'VK', 'YouTube'] },
    { name: 'Когтеточка', value: 88, growth_rate: 0.5, source: 'ozon', platform: ['Ozon', 'WB'] },
    { name: 'Игрушка рыба', value: 72, growth_rate: 0.8, source: 'mixed', platform: ['Ozon', 'VK'] },
    { name: 'Шлейка', value: 65, growth_rate: 0.3, source: 'ozon', platform: ['Ozon'] },
    { name: 'Лежанка', value: 60, growth_rate: 0.1, source: 'ozon', platform: ['WB', 'Yandex'] },
    { name: 'Сумка-переноска', value: 55, growth_rate: 0.4, source: 'ozon', platform: ['Ozon', 'WB'] },
    { name: 'Автопоилка', value: 92, growth_rate: 1.5, source: 'vk', platform: ['VK', 'YouTube'] },
    { name: 'GPS ошейник', value: 85, growth_rate: 1.1, source: 'mixed', platform: ['Ozon', 'VK'] },
    { name: 'Фурминатор', value: 45, growth_rate: -0.1, source: 'ozon', platform: ['Ozon'] },
    { name: 'Лакомства', value: 80, growth_rate: 0.6, source: 'ozon', platform: ['Ozon', 'WB', 'Yandex'] },
    { name: 'Наполнитель', value: 98, growth_rate: 0.2, source: 'ozon', platform: ['Ozon', 'WB'] },
    { name: 'Лоток', value: 75, growth_rate: 0.3, source: 'ozon', platform: ['Ozon'] },
    { name: 'Одежда для собак', value: 82, growth_rate: 0.9, source: 'vk', platform: ['VK', 'OK'] },
    { name: 'Витамины', value: 68, growth_rate: 0.4, source: 'ozon', platform: ['Ozon', 'Yandex'] },
    { name: 'Шампунь', value: 50, growth_rate: 0.2, source: 'ozon', platform: ['WB'] },
    { name: 'Когтерез', value: 40, growth_rate: 0.1, source: 'ozon', platform: ['Ozon'] },
    { name: 'Миска керамическая', value: 62, growth_rate: 0.5, source: 'mixed', platform: ['Ozon', 'VK'] },
    { name: 'Домик', value: 78, growth_rate: 0.6, source: 'ozon', platform: ['WB'] },
    { name: 'Туннель', value: 58, growth_rate: 0.7, source: 'vk', platform: ['VK', 'YouTube'] },
    { name: 'Интерактивный мяч', value: 88, growth_rate: 1.3, source: 'mixed', platform: ['Ozon', 'YouTube'] },
  ])

  // Computed: Filtered Words based on active platforms
  const filteredWords = computed(() => {
    const activePlatformNames = platforms.value.filter(p => p.active).map(p => p.name)

    return rawWords.value.filter(word => {
      // Check if word appears on ANY active platform
      return word.platform.some(p => activePlatformNames.includes(p))
    })
  })

  const isLoading = ref(false)
  const dataSource = ref<'live' | 'mock'>('mock')
  const lastUpdated = ref<string>('')

  const fetchRadarData = async (snapshotDate?: string) => {
    isLoading.value = true
    try {
      const params = snapshotDate ? `?snapshot_date=${snapshotDate}` : ''
      const res = await apiGet(`/trends/radar${params}`)
      if (res && res.words && res.words.length > 0) {
        rawWords.value = res.words
        dataSource.value = res.source === 'live' ? 'live' : 'mock'
        lastUpdated.value = res.date || ''
      }
    } catch (e) {
      console.warn('[RadarStore] Failed to fetch radar data, using mock', e)
    } finally {
      isLoading.value = false
    }
  }

  const togglePlatform = (index: number) => {
    platforms.value[index].active = !platforms.value[index].active
  }

  return {
    platforms,
    rawWords,
    filteredWords,
    isLoading,
    dataSource,
    lastUpdated,
    fetchRadarData,
    togglePlatform
  }
})

import { defineStore } from "pinia"
import { ref } from "vue"
import { apiGet } from "../api/client"
import type { RadarItem } from "../types"

interface QuadrantResponse {
  items: RadarItem[]
  median_demand: number
  median_supply: number
}

export const useMarketStore = defineStore("market", () => {
  const radarItems = ref<RadarItem[]>([])
  const selected = ref<RadarItem | null>(null)

  const fetchRadar = async (): Promise<void> => {
    const data = await apiGet<QuadrantResponse>("/api/analysis/quadrant")
    radarItems.value = data.items
    if (!selected.value && data.items.length > 0) {
      selected.value = data.items[0]
    }
  }

  const select = (item: RadarItem): void => {
    selected.value = item
  }

  return {
    radarItems,
    selected,
    fetchRadar,
    select
  }
})

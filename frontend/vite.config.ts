import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 9006,
    proxy: {
      "/api": "http://localhost:8001",
      "/ai": "http://localhost:8001",
      "/analysis": "http://localhost:8001",
      "/market-trends": "http://localhost:8001",
      "/shop-performance": "http://localhost:8001",
      "/admin": "http://localhost:8001",
      "/auth": "http://localhost:8001"
    }
  }
})

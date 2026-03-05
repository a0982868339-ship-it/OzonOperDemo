import type { Config } from "tailwindcss"

export default {
  darkMode: 'class', // Enable class-based dark mode
  content: ["./index.html", "./src/**/*.{vue,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ozon: {
          500: "#005bff",
          600: "#0049cc"
        },
        // Custom semantic colors for charts
        chart: {
            up: '#10b981', // emerald-500
            down: '#ef4444', // red-500
            neutral: '#64748b' // slate-500
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    }
  },
  plugins: []
} satisfies Config
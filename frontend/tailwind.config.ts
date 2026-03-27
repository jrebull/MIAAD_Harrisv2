import type { Config } from 'tailwindcss'

export default <Config>{
  content: [],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#003CA6',
          50: '#E6EEFF',
          100: '#CCddFF',
          200: '#99BBFF',
          300: '#6699FF',
          400: '#3377FF',
          500: '#003CA6',
          600: '#003090',
          700: '#002470',
          800: '#001850',
          900: '#0a0a1a',
        },
        accent: {
          yellow: '#FFD600',
          green: '#00E5A0',
          red: '#FF3366',
          blue: '#60a5fa',
        },
        dark: {
          bg1: '#0a0a1a',
          bg2: '#0d1b2a',
          bg3: '#1b2838',
          card: 'rgba(255,255,255,0.04)',
          border: 'rgba(255,255,255,0.08)',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}

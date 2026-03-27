export default defineNuxtConfig({
  compatibilityDate: '2025-01-01',
  future: { compatibilityVersion: 4 },
  devtools: { enabled: true },

  modules: [
    '@nuxtjs/tailwindcss',
    '@nuxt/fonts',
  ],

  components: [
    { path: '~/components', pathPrefix: false },
  ],

  app: {
    head: {
      title: 'Visa Predict AI — MOHHO Optimizer',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Multi-Objective Harris Hawks Optimization for US EB Visa Allocation' },
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
      ],
    },
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
    },
  },

  tailwindcss: {
    cssPath: '~/assets/css/main.css',
  },

  fonts: {
    families: [
      { name: 'Inter', provider: 'google', weights: [300, 400, 500, 600, 700, 900] },
      { name: 'JetBrains Mono', provider: 'google', weights: [400, 700] },
    ],
  },

  routeRules: {
    '/modelo': { prerender: true },
  },
})

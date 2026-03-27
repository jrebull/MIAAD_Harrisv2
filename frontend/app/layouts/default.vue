<template>
  <div class="min-h-screen bg-gradient-to-br from-dark-bg1 via-dark-bg2 to-dark-bg3">
    <AppNavbar />
    <div class="flex">
      <ScenarioSidebar class="hidden lg:block" />
      <main class="flex-1 max-w-[1300px] mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <slot />
      </main>
    </div>
    <AppFooter />
  </div>
</template>

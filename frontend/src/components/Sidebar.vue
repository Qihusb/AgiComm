<template>
  <aside
    :class="[
      'fixed inset-y-0 left-0 z-40 flex h-full max-h-[100dvh] w-72 max-w-[min(18rem,88vw)] shrink-0 flex-col border-r transition-transform duration-200 ease-out md:static md:z-auto md:max-h-none md:max-w-none md:translate-x-0',
      'border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900',
      sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0',
    ]"
  >
    <div class="p-4 sm:p-6 md:p-8">
      <div class="flex items-center space-x-3">
        <div
          class="flex h-10 w-10 items-center justify-center overflow-hidden rounded-xl bg-blue-600 shadow-lg shadow-blue-500/20"
        >
          <img src="../assets/icon.png" alt="logo-icon" class="h-full w-full object-cover" />
        </div>
        <div class="min-w-0">
          <h1 class="truncate text-lg font-bold tracking-tighter text-slate-900 sm:text-xl dark:text-white">
            AgiComm
          </h1>
          <p class="font-mono text-[10px] text-slate-500 dark:text-slate-500">GSS Simulation Platform</p>
        </div>
      </div>
    </div>

    <nav class="flex-1 space-y-1 overflow-y-auto px-3 py-2 md:px-4 md:py-4">
      <div
        class="mb-3 px-3 text-[10px] font-bold uppercase tracking-widest text-slate-400 dark:text-slate-600 md:px-4 md:mb-4"
      >
        核心仿真模块
      </div>

      <router-link
        to="/"
        class="group flex items-center space-x-3 rounded-xl px-3 py-3 transition-all hover:bg-slate-100 dark:hover:bg-slate-800"
        @click="onNav"
      >
        <span class="text-xl transition-transform group-hover:scale-110">🎙️</span>
        <span class="font-medium text-slate-800 dark:text-slate-200">媒体提问仿真</span>
      </router-link>

      <router-link
        to="/news"
        class="group flex items-center space-x-3 rounded-xl px-3 py-3 opacity-60 transition-all hover:bg-slate-100 dark:hover:bg-slate-800"
        @click="onNav"
      >
        <span class="text-xl transition-transform group-hover:scale-110">📰</span>
        <span class="font-medium text-slate-800 dark:text-slate-200">多维报道生成</span>
      </router-link>

      <router-link
        to="/social"
        class="group flex items-center space-x-3 rounded-xl px-3 py-3 opacity-60 transition-all hover:bg-slate-100 dark:hover:bg-slate-800"
        @click="onNav"
      >
        <span class="text-xl transition-transform group-hover:scale-110">🌐</span>
        <span class="font-medium text-slate-800 dark:text-slate-200">受众传播仿真</span>
      </router-link>
    </nav>

    <div class="border-t border-slate-200 p-4 dark:border-slate-800 md:p-6">
      <div class="rounded-lg bg-slate-100 p-3 dark:bg-slate-800/50 md:p-4">
        <p class="text-xs text-slate-500 dark:text-slate-500">当前仿真事件</p>
        <p class="mt-1 truncate text-sm text-slate-700 dark:text-slate-300">未设定...</p>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { inject, computed } from 'vue'

const sidebar = inject('sidebar', null)
const sidebarOpen = computed(() => Boolean(sidebar?.open?.value))

function onNav() {
  if (typeof window !== 'undefined' && window.matchMedia('(max-width: 767px)').matches) {
    sidebar?.close?.()
  }
}
</script>

<style scoped>
.router-link-active {
  @apply border border-blue-500/20 bg-blue-600/10 text-blue-600 dark:text-blue-500;
}
</style>

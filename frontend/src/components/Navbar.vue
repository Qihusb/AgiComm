<template>
  <nav
    class="sticky top-0 z-50 flex h-14 shrink-0 items-center justify-between gap-2 border-b px-3 sm:h-16 sm:px-4 md:px-6 lg:px-8 border-slate-200 bg-white/80 backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50"
  >
    <div class="flex min-w-0 flex-1 items-center gap-2 sm:gap-3">
      <button
        type="button"
        class="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-slate-600 hover:bg-slate-100 md:hidden dark:text-slate-300 dark:hover:bg-slate-800"
        aria-label="打开菜单"
        @click="sidebar?.toggle?.()"
      >
        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 6h16M4 12h16M4 18h16"
          />
        </svg>
      </button>

      <div
        :class="[
          'flex min-w-0 max-w-full items-center gap-1.5 rounded-full border px-2 py-1 text-[10px] transition-all sm:gap-2 sm:px-3 sm:text-xs',
          backendConnected
            ? 'border-green-500/20 bg-green-500/10'
            : 'border-red-500/20 bg-red-500/10',
        ]"
      >
        <span
          :class="[
            'h-1.5 w-1.5 shrink-0 rounded-full sm:h-2 sm:w-2',
            backendConnected ? 'animate-pulse bg-green-500' : 'bg-red-500',
          ]"
        />
        <span
          :class="[
            'truncate font-mono',
            backendConnected ? 'text-green-600 dark:text-green-500' : 'text-red-600 dark:text-red-500',
          ]"
        >
          <span class="hidden sm:inline">Backend: </span>
          {{ backendConnected ? 'Connected' : 'Disconnected' }}
        </span>
      </div>

      <button
        v-if="!backendConnected"
        type="button"
        class="shrink-0 rounded bg-slate-200 px-2 py-1 text-[10px] text-slate-700 transition hover:bg-slate-300 disabled:opacity-50 dark:bg-slate-700/50 dark:text-slate-300 dark:hover:bg-slate-600 sm:text-xs"
        :disabled="isChecking"
        @click="checkBackendConnection"
      >
        {{ isChecking ? '检测中' : '重试' }}
      </button>
    </div>

    <div class="flex shrink-0 items-center gap-2 sm:gap-4 md:gap-6">
      <!-- 模型状态检查按钮 -->
      <router-link
        to="/model-status"
        class="hidden sm:flex items-center gap-1.5 px-3 py-2 rounded-lg transition-all text-xs sm:text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 dark:text-slate-400 dark:hover:text-white dark:hover:bg-slate-800"
        title="查看模型服务状态"
      >
        <span class="text-base">🔧</span>
        <span class="hidden md:inline">模型监控</span>
      </router-link>

      <!-- 深色模式 滑块开关 -->
      <label class="relative inline-flex h-8 w-12 items-center rounded-full bg-slate-200 p-1 transition-colors duration-200 peer-checked:bg-slate-700 dark:bg-slate-700">
        <input
          type="checkbox"
          v-model="isDark"
          @change="toggleTheme"
          class="sr-only peer"
        />
        <!-- 滑动圆点 -->
        <div
          class="flex h-6 w-6 items-center justify-center rounded-full bg-white shadow-md transition-transform duration-200 peer-checked:translate-x-4"
        >
          <span v-if="isDark" class="text-[12px]">🌙</span>
          <span v-else class="text-[12px]">☀️</span>
        </div>
      </label>

      <span
        class="hidden cursor-pointer text-xs text-slate-500 transition-colors hover:text-slate-800 sm:inline sm:text-sm dark:text-slate-400 dark:hover:text-white"
        >实验指南</span>
      <a
        href="https://github.com/Qihusb/AgiComm"
        target="_blank"
        rel="noopener noreferrer"
        class="hidden items-center gap-1.5 text-xs text-slate-500 transition-colors hover:text-slate-800 sm:inline-flex sm:text-sm dark:text-slate-400 dark:hover:text-white"
      >
        <svg class="h-4 w-4 shrink-0" fill="currentColor" viewBox="0 0 24 24">
          <path
            d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"
          />
        </svg>
        GitHub
      </a>
      <a
        href="https://github.com/Qihusb/AgiComm"
        target="_blank"
        rel="noopener noreferrer"
        class="inline-flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 bg-slate-900 text-xs font-bold text-white sm:hidden dark:border-slate-700"
        aria-label="GitHub"
      >GH</a>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted, inject } from 'vue'

const sidebar = inject('sidebar', null)

const API_HEALTH = import.meta.env.VITE_API_BASE
  ? `${import.meta.env.VITE_API_BASE.replace(/\/$/, '')}/health`
  : `${window.location.protocol}//${window.location.hostname}:8001/health`

const backendConnected = ref(false)
const isChecking = ref(false)
const isDark = ref(true)

function readDark() {
  isDark.value = document.documentElement.classList.contains('dark')
}

function toggleTheme() {
  const root = document.documentElement
  root.classList.toggle('dark')
  readDark()
  localStorage.setItem('agicomm-theme', isDark.value ? 'dark' : 'light')
}

const checkBackendConnection = async () => {
  isChecking.value = true
  try {
    const response = await fetch(API_HEALTH, {
      method: 'GET',
      signal: AbortSignal.timeout(8000),
    })
    backendConnected.value = response.ok
  } catch {
    backendConnected.value = false
  } finally {
    isChecking.value = false
  }
}

let intervalId

onMounted(() => {
  readDark()
  checkBackendConnection()
  intervalId = setInterval(checkBackendConnection, 180000)
})

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId)
})
</script>
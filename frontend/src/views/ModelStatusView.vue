<template>
  <div class="min-h-screen overflow-x-hidden bg-gradient-to-br from-slate-100 via-white to-slate-100 p-4 text-slate-900 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 dark:text-slate-100 sm:p-6 md:p-8">
    <div class="mx-auto max-w-7xl space-y-6">
      <!-- 标题头 -->
      <header class="border-b border-slate-200/80 pb-6 dark:border-slate-700/50">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div class="min-w-0">
            <h1 class="flex flex-wrap items-center gap-2 text-2xl font-bold tracking-tight text-slate-900 dark:text-white sm:gap-3 sm:text-3xl md:text-4xl">
              <span class="text-3xl sm:text-4xl md:text-5xl">🔧</span> 模型服务监控
            </h1>
            <p class="mt-2 text-sm text-slate-600 dark:text-slate-400 sm:mt-3 sm:text-base">
              实时检查可用的 LLM 模型及服务状态
            </p>
          </div>
        </div>
      </header>

      <!-- 主内容区 -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <!-- 左侧：状态摘要卡片 -->
        <div class="lg:col-span-1">
          <div v-if="loading" class="rounded-2xl border border-slate-200/80 bg-gradient-to-br from-white to-slate-50 p-6 shadow-lg backdrop-blur dark:border-slate-700/50 dark:from-slate-800 dark:to-slate-900">
            <div class="flex flex-col items-center justify-center space-y-4 py-8">
              <div class="h-8 w-8 animate-spin rounded-full border-4 border-slate-300 border-t-blue-500 dark:border-slate-600 dark:border-t-blue-400"></div>
              <p class="text-sm text-slate-500 dark:text-slate-400">加载中...</p>
            </div>
          </div>

          <div v-else-if="error" class="rounded-2xl border border-red-200/50 bg-gradient-to-br from-red-50 to-red-50/50 p-6 shadow-lg backdrop-blur dark:border-red-900/30 dark:from-red-950/20 dark:to-red-950/10">
            <div class="flex items-start gap-3">
              <span class="text-2xl">❌</span>
              <div class="min-w-0 flex-1">
                <h3 class="font-semibold text-red-900 dark:text-red-300">加载失败</h3>
                <p class="mt-1 text-sm text-red-700 dark:text-red-400">{{ error }}</p>
                <button
                  @click="fetchStatus"
                  class="mt-3 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-700"
                >
                  🔄 重试
                </button>
              </div>
            </div>
          </div>

          <div v-else-if="statusData" class="space-y-4">
            <!-- 状态卡片 -->
            <div class="rounded-2xl border border-slate-200/80 bg-gradient-to-br from-white to-slate-50 p-6 shadow-lg backdrop-blur dark:border-slate-700/50 dark:from-slate-800 dark:to-slate-900">
              <div class="space-y-4">
                <div>
                  <p class="text-xs font-semibold uppercase tracking-widest text-slate-500 dark:text-slate-400">
                    {{ statusData.summary.title }}
                  </p>
                </div>

                <!-- 状态指示器 -->
                <div class="flex items-center gap-3">
                  <div
                    :class="[
                      'h-12 w-12 rounded-full flex items-center justify-center text-lg font-bold',
                      isHealthy ? 'bg-green-100 dark:bg-green-950/30' : 'bg-red-100 dark:bg-red-950/30'
                    ]"
                  >
                    {{ isHealthy ? '✅' : '❌' }}
                  </div>
                  <div class="flex-1">
                    <p class="font-semibold" :class="isHealthy ? 'text-green-700 dark:text-green-400' : 'text-red-700 dark:text-red-400'">
                      {{ statusData.summary.status_icon }}
                    </p>
                    <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
                      {{ statusData.summary.last_check }}
                    </p>
                  </div>
                </div>

                <!-- 健康度统计 -->
                <div class="flex items-center justify-between rounded-lg bg-slate-100/50 p-3 dark:bg-slate-700/30">
                  <span class="text-sm font-medium text-slate-600 dark:text-slate-300">可用模型</span>
                  <span class="font-bold text-lg" :class="isHealthy ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
                    {{ statusData.summary.health_rate }}
                  </span>
                </div>

                <!-- 最后检查 -->
                <button
                  @click="fetchStatus"
                  :disabled="loading"
                  class="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  🔄 {{ loading ? '检查中...' : '立即检查' }}
                </button>
              </div>
            </div>

            <!-- 最后更新时间 -->
            <div class="text-sm text-slate-500 dark:text-slate-400 text-center">
              最后更新: {{ lastUpdateTime }}
            </div>
          </div>
        </div>

        <!-- 右侧：活跃模型列表和错误日志 -->
        <div class="lg:col-span-2 space-y-6">
          <!-- 活跃模型 -->
          <div class="rounded-2xl border border-slate-200/80 bg-gradient-to-br from-white to-slate-50 p-6 shadow-lg backdrop-blur dark:border-slate-700/50 dark:from-slate-800 dark:to-slate-900">
            <div class="mb-4">
              <h2 class="flex items-center gap-2 text-lg font-bold text-slate-900 dark:text-white">
                <span class="text-2xl">🟢</span> 活跃模型
              </h2>
              <p class="mt-1 text-sm text-slate-600 dark:text-slate-400">
                {{ statusData?.active_pool?.count || 0 }} 个可用
              </p>
            </div>

            <div v-if="statusData?.active_pool?.models?.length === 0" class="py-12 text-center">
              <p class="text-lg text-slate-500 dark:text-slate-400">
                <span class="text-3xl">⚠️</span>
              </p>
              <p class="mt-2 text-sm font-medium text-slate-700 dark:text-slate-300">
                当前没有可用的模型
              </p>
              <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
                请检查 API 密钥配置和网络连接
              </p>
            </div>

            <div v-else class="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div
                v-for="model in statusData?.active_pool?.models || []"
                :key="model"
                class="rounded-lg border border-green-200/50 bg-gradient-to-br from-green-50 to-green-50/50 p-4 dark:border-green-900/30 dark:from-green-950/20 dark:to-green-950/10"
              >
                <div class="flex items-center gap-3">
                  <span class="text-2xl">🚀</span>
                  <div class="min-w-0 flex-1">
                    <p class="truncate font-mono text-sm font-semibold text-green-900 dark:text-green-300">
                      {{ model }}
                    </p>
                    <p class="text-xs text-green-700 dark:text-green-400 mt-1">
                      ✓ 在线
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 错误日志 -->
          <div class="rounded-2xl border border-slate-200/80 bg-gradient-to-br from-white to-slate-50 p-6 shadow-lg backdrop-blur dark:border-slate-700/50 dark:from-slate-800 dark:to-slate-900">
            <div class="mb-4">
              <h2 class="flex items-center gap-2 text-lg font-bold text-slate-900 dark:text-white">
                <span class="text-2xl">📋</span> 错误日志
              </h2>
              <p class="mt-1 text-sm text-slate-600 dark:text-slate-400">
                服务异常情况记录
              </p>
            </div>

            <div v-if="!statusData?.error_log || statusData?.error_log === '无异常'" class="py-8 text-center">
              <p class="text-lg text-green-600 dark:text-green-400">
                <span class="text-3xl">✨</span>
              </p>
              <p class="mt-2 text-sm font-medium text-slate-700 dark:text-slate-300">
                无异常记录
              </p>
              <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
                所有服务运行正常
              </p>
            </div>

            <div v-else class="space-y-3 max-h-96 overflow-y-auto">
              <div
                v-for="(error, index) in (Array.isArray(statusData?.error_log) ? statusData.error_log : [])"
                :key="index"
                class="rounded-lg border border-red-200/50 bg-gradient-to-br from-red-50 to-red-50/50 p-4 dark:border-red-900/30 dark:from-red-950/20 dark:to-red-950/10"
              >
                <div class="flex items-start gap-3">
                  <span class="text-lg">⚠️</span>
                  <div class="min-w-0 flex-1">
                    <p class="font-mono text-sm font-semibold text-red-900 dark:text-red-300">
                      {{ error.model }}
                    </p>
                    <p class="text-xs text-red-700 dark:text-red-400 mt-1 break-words">
                      {{ error.reason }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 信息提示 -->
      <div class="rounded-xl border border-blue-200/50 bg-gradient-to-r from-blue-50 to-blue-50/50 p-4 dark:border-blue-900/30 dark:from-blue-950/20 dark:to-blue-950/10">
        <div class="flex items-start gap-3">
          <span class="text-lg flex-shrink-0">ℹ️</span>
          <div class="text-sm text-blue-900 dark:text-blue-300">
            <p class="font-semibold">模型服务说明</p>
            <ul class="mt-2 space-y-1 text-xs opacity-80">
              <li>• 系统支持多个 LLM 供应商（智谱、DeepSeek、OpenAI 等）</li>
              <li>• 当某个模型不可用时，会自动切换到其他可用模型</li>
              <li>• 绿灯表示模型在线，红灯表示模型离线或出错</li>
              <li>• 实时检查间隔为 3 分钟，也可手动检查</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE
  ? `${import.meta.env.VITE_API_BASE.replace(/\/$/, '')}`
  : `${window.location.protocol}//${window.location.hostname}:8001`

const statusData = ref(null)
const loading = ref(false)
const error = ref(null)
const lastUpdateTime = ref('未检查')

const isHealthy = computed(() => {
  if (!statusData.value) return false
  return statusData.value?.active_pool?.count > 0
})

const fetchStatus = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await fetch(`${API_BASE}/llm/status`, {
      method: 'GET',
      signal: AbortSignal.timeout(15000),
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const result = await response.json()
    
    // 判断返回格式：是否包含 data 字段
    if (result.data) {
      statusData.value = result.data
    } else if (result.summary) {
      // 直接返回的情况
      statusData.value = result
    } else {
      throw new Error('返回数据格式不正确')
    }

    // 更新时间
    const now = new Date()
    lastUpdateTime.value = now.toLocaleTimeString('zh-CN')
  } catch (err) {
    error.value = err.message || '加载模型状态失败'
    console.error('Failed to fetch LLM status:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStatus()
})
</script>

<style scoped>
/* 平滑的滚动 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(100, 116, 139, 0.3);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(100, 116, 139, 0.5);
}

@media (prefers-color-scheme: dark) {
  ::-webkit-scrollbar-thumb {
    background: rgba(71, 85, 105, 0.4);
  }

  ::-webkit-scrollbar-thumb:hover {
    background: rgba(71, 85, 105, 0.6);
  }
}
</style>

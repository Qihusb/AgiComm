<template>
  <nav class="h-16 border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50 px-8 flex items-center justify-between">
    <div class="flex items-center space-x-4">
      <div :class="[
        'flex items-center space-x-2 px-3 py-1 rounded-full border transition-all',
        backendConnected
          ? 'bg-green-500/10 border-green-500/20'
          : 'bg-red-500/10 border-red-500/20'
      ]">
        <span :class="[
          'w-2 h-2 rounded-full',
          backendConnected
            ? 'bg-green-500 animate-pulse'
            : 'bg-red-500'
        ]"></span>
        <span :class="[
          'text-xs font-mono',
          backendConnected
            ? 'text-green-500'
            : 'text-red-500'
        ]">
          Backend: {{ backendConnected ? 'Connected' : 'Disconnected' }}
        </span>
      </div>
      <button 
        v-if="!backendConnected"
        @click="checkBackendConnection"
        class="text-xs px-2 py-1 bg-slate-700/50 hover:bg-slate-600 text-slate-300 rounded transition"
        :disabled="isChecking"
      >
        {{ isChecking ? '检测中...' : '重试' }}
      </button>
    </div>

    <div class="flex items-center space-x-6">
      <div class="text-slate-400 text-sm hover:text-white cursor-pointer transition-colors">实验指南</div>
      <div class="text-slate-400 text-sm hover:text-white cursor-pointer transition-colors">GitHub</div>
      <div class="h-8 w-8 rounded-full bg-gradient-to-tr from-blue-600 to-purple-600 border border-slate-700"></div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const backendConnected = ref(false)
const isChecking = ref(false)

// 检查后端连接
const checkBackendConnection = async () => {
  isChecking.value = true
  try {
    const response = await fetch('http://localhost:8000/health', {
      method: 'GET',
      timeout: 5000
    })
    backendConnected.value = response.ok
  } catch (error) {
    backendConnected.value = false
  } finally {
    isChecking.value = false
  }
}

// 组件挂载时检查连接
onMounted(() => {
  checkBackendConnection()
  
  // 每30秒检查一次后端状态
  const interval = setInterval(checkBackendConnection, 30000)
  
  // 组件卸载时清除定时器
  return () => clearInterval(interval)
})
</script>
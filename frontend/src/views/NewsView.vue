<template>
  <div class="min-h-screen overflow-x-hidden bg-gradient-to-br from-slate-100 via-white to-slate-100 p-4 text-slate-900 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 dark:text-slate-100 sm:p-6 md:p-8">
    <div class="mx-auto max-w-7xl space-y-4 sm:space-y-6">
      <!-- 标题头 -->
      <header class="border-b border-slate-200/80 pb-4 dark:border-slate-700/50 sm:pb-6">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div class="min-w-0">
            <h1 class="flex flex-wrap items-center gap-2 text-2xl font-bold tracking-tight text-slate-900 dark:text-white sm:gap-3 sm:text-3xl md:text-4xl">
              <span class="text-3xl sm:text-4xl md:text-5xl">📰</span> 媒体报道生成
            </h1>
            <p class="mt-2 text-sm text-slate-600 dark:text-slate-400 sm:mt-3 sm:text-base">基于时间轴与媒体选择，模拟全球媒体对科技事件的报道生成与传播</p>
          </div>
        </div>
      </header>

      <!-- 输入面板 -->
      <div class="rounded-2xl border border-slate-200/80 bg-gradient-to-br from-white to-slate-50 p-4 shadow-xl backdrop-blur dark:border-slate-700/50 dark:from-slate-800 dark:to-slate-900 sm:p-6 md:p-8">
        <div class="grid grid-cols-1 gap-6 lg:grid-cols-3 lg:gap-8">
          <!-- 左侧：输入与媒体选择 -->
          <div class="lg:col-span-2 space-y-6">
            <!-- 事件描述 -->
            <div>
              <label class="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-800 dark:text-slate-200">
                <span class="text-lg">📝</span> 事件描述 (Event Description)
              </label>
              <textarea 
                v-model="eventText"
                class="h-32 w-full rounded-xl border border-slate-200 bg-white p-4 text-slate-900 transition placeholder-slate-400 outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/50 dark:border-slate-600/50 dark:bg-slate-700/30 dark:text-slate-100 dark:placeholder-slate-500"
                placeholder="请输入需要报道的科技事件内容，如：'2026年3月，中国成功登陆月球南极...'"
              ></textarea>
            </div>

            <!-- 日期输入 -->
            <div>
              <label class="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-800 dark:text-slate-200">
                <span class="text-lg">📅</span> 事件发生日期
              </label>
              <input
                v-model="eventDate"
                type="date"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-900 transition outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/50 dark:border-slate-600/50 dark:bg-slate-700/30 dark:text-slate-100"
              />
            </div>

            <!-- 媒体搜索与选择 -->
            <div>
              <label class="mb-3 flex items-center justify-between text-sm font-semibold text-slate-800 dark:text-slate-200">
                <span class="flex items-center gap-2"><span class="text-lg">🎬</span> 媒体选择 (最多10个)</span>
                <span v-if="selectedMedia.length > 0" class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full dark:bg-blue-900/40 dark:text-blue-300">
                  已选 {{ selectedMedia.length }}/10
                </span>
              </label>
              <input
                v-model="mediaSearchText"
                type="text"
                placeholder="搜索媒体名称或国家..."
                class="mb-3 w-full rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm text-slate-900 placeholder-slate-400 outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/50 dark:border-slate-600/50 dark:bg-slate-700/30 dark:text-slate-100 dark:placeholder-slate-500"
              />
              <div class="grid gap-2 max-h-48 overflow-y-auto rounded-lg border border-slate-200 bg-white p-3 dark:border-slate-600/50 dark:bg-slate-700/20">
                <div v-if="filteredMediaList.length === 0" class="text-sm text-slate-500 dark:text-slate-400">
                  暂无匹配的媒体
                </div>
                <label v-for="media in filteredMediaList" :key="media.media_id" class="flex items-center gap-2 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-700/30 p-2 rounded">
                  <input
                    type="checkbox"
                    :checked="selectedMedia.includes(media.media_id)"
                    @change="toggleMediaSelection(media.media_id)"
                    :disabled="selectedMedia.length >= MEDIA_LIMIT && !selectedMedia.includes(media.media_id)"
                    class="rounded"
                  />
                  <span class="text-sm">
                    <span class="font-semibold text-slate-800 dark:text-slate-200">{{ media.media_name }}</span>
                    <span class="text-xs text-slate-500 dark:text-slate-400"> ({{ media.country }})</span>
                  </span>
                </label>
              </div>
            </div>

            <!-- 已选媒体标签 -->
            <div v-if="selectedMedia.length > 0" class="flex flex-wrap gap-2">
              <span
                v-for="mediaId in selectedMedia"
                :key="mediaId"
                class="flex items-center gap-1 rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-800 dark:bg-blue-900/40 dark:text-blue-300"
              >
                {{ allMediaList.find(m => m.media_id === mediaId)?.media_name }}
                <button @click="selectedMedia = selectedMedia.filter(m => m !== mediaId)" class="ml-1 hover:opacity-70">✕</button>
              </span>
            </div>
          </div>

          <!-- 右侧：操作按钮 -->
          <div class="flex flex-col justify-center gap-4">
            <button
              @click="runNewsGeneration"
              :disabled="loading || !eventText.trim() || selectedMedia.length === 0 || !eventDate"
              class="w-full rounded-xl bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4 font-bold text-white transition hover:from-blue-600 hover:to-blue-700 disabled:from-slate-400 disabled:to-slate-500 disabled:cursor-not-allowed dark:from-blue-600 dark:to-blue-700"
            >
              <span v-if="!loading" class="flex items-center justify-center gap-2">
                <span class="text-lg">🚀</span> 生成报道
              </span>
              <span v-else class="flex items-center justify-center gap-2">
                <span class="animate-spin">⏳</span> 生成中...
              </span>
            </button>
            <button
              v-if="selectedMedia.length > 0"
              @click="selectedMedia = []"
              class="w-full rounded-xl border border-slate-300 px-6 py-2 font-semibold text-slate-700 transition hover:bg-slate-100 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-700/30"
            >
              清空选择
            </button>
          </div>
        </div>
      </div>

      <!-- 错误提示面板 -->
      <div
        v-if="error.code"
        class="rounded-xl border-l-4 border-red-400 bg-gradient-to-r from-red-50 to-white p-4 shadow-lg backdrop-blur dark:border-red-500/50 dark:from-red-950/40 dark:to-slate-900/40 sm:p-6"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="min-w-0 flex-1">
            <h3 class="flex items-center gap-2 font-bold text-red-800 dark:text-red-300 text-lg">
              <span>{{ error.icon }}</span> {{ error.title }}
            </h3>
            <p class="mt-2 text-sm text-red-700 dark:text-red-200">{{ error.message }}</p>
            <p v-if="error.detail" class="mt-1 text-xs text-red-600 dark:text-red-400">{{ error.detail }}</p>
            <div v-if="error.solutions.length > 0" class="mt-3 space-y-1">
              <p class="text-xs font-semibold text-red-700 dark:text-red-300">💡 建议：</p>
              <ul class="list-disc list-inside space-y-1 text-xs text-red-600 dark:text-red-400">
                <li v-for="(sol, i) in error.solutions" :key="i">{{ sol }}</li>
              </ul>
            </div>
          </div>
          <button
            @click="clearError"
            class="flex-shrink-0 p-2 text-xl transition hover:opacity-70"
            title="关闭错误提示"
          >
            ✕
          </button>
        </div>
      </div>

      <!-- 结果展示 -->
      <div v-if="results.length > 0 || loading" class="space-y-6">
        <!-- 进度条 -->
        <div v-if="loading" class="rounded-xl border border-slate-200 bg-white p-4 shadow-lg dark:border-slate-700/50 dark:bg-slate-800 sm:p-6">
          <div class="mb-4 flex items-center space-x-4">
            <span class="animate-spin text-3xl">⚙️</span>
            <div class="min-w-0 flex-1">
              <p class="font-semibold text-slate-800 dark:text-slate-200">报道生成中...</p>
              <p class="text-sm text-slate-600 dark:text-slate-400">已生成 <span class="font-bold text-blue-600 dark:text-blue-400">{{ receivedCount }}</span> / <span class="font-bold text-slate-700 dark:text-slate-300">{{ totalCount > 0 ? totalCount : '...' }}</span> 份报道</p>
            </div>
          </div>
          <div class="h-3 overflow-hidden rounded-full border border-slate-200 bg-slate-200 dark:border-slate-600/50 dark:bg-slate-700">
            <div class="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-300" :style="{ width: totalCount > 0 ? (100 * receivedCount / totalCount) + '%' : '15%' }"></div>
          </div>
        </div>

        <!-- 结果统计 -->
        <div v-if="results.length > 0 && !loading" class="grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-4">
          <div class="rounded-xl border border-slate-200 bg-white p-3 text-center dark:border-slate-700/50 dark:bg-slate-800 sm:p-4">
            <p class="mb-1 text-xs font-semibold text-slate-500 dark:text-slate-400">总报道数</p>
            <p class="text-2xl font-bold text-slate-900 dark:text-white sm:text-3xl">{{ results.length }}</p>
          </div>
          <div class="rounded-xl border border-green-200 bg-green-50 p-3 text-center dark:border-green-500/30 dark:bg-green-950/40 sm:p-4">
            <p class="mb-1 text-xs font-semibold text-green-700 dark:text-green-300">成功生成</p>
            <p class="text-2xl font-bold text-green-600 dark:text-green-400 sm:text-3xl">{{ successCount }}</p>
          </div>
          <div v-if="errorCount > 0" class="rounded-xl border border-red-200 bg-red-50 p-3 text-center dark:border-red-500/30 dark:bg-red-950/40 sm:p-4">
            <p class="mb-1 text-xs font-semibold text-red-700 dark:text-red-300">生成失败</p>
            <p class="text-2xl font-bold text-red-600 dark:text-red-400 sm:text-3xl">{{ errorCount }}</p>
          </div>
          <div class="rounded-xl border border-slate-200 bg-white p-3 text-center dark:border-slate-700/50 dark:bg-slate-800 sm:p-4">
            <p class="mb-1 text-xs font-semibold text-slate-500 dark:text-slate-400">成功率</p>
            <p class="text-2xl font-bold text-slate-800 dark:text-slate-300 sm:text-3xl">{{ results.length > 0 ? ((100 * successCount / results.length).toFixed(1)) : 0 }}%</p>
          </div>
        </div>

        <!-- 报道卡片网格 -->
        <div class="grid grid-cols-1 gap-4 sm:gap-6 lg:grid-cols-2">
          <div
            v-for="(report, index) in results"
            :key="index"
            :class="[
              'rounded-xl border-l-4 p-4 shadow-lg backdrop-blur transition-all duration-300 sm:p-6',
              report.has_error
                ? 'border-red-400 bg-gradient-to-br from-red-50 to-white opacity-95 dark:border-red-500/50 dark:from-red-950/40 dark:to-slate-900/40'
                : 'border-green-400 bg-gradient-to-br from-green-50 to-white dark:border-green-500/50 dark:from-green-950/40 dark:to-slate-900/40'
            ]"
          >
            <!-- 媒体头部 -->
            <div class="flex justify-between items-start mb-4">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <span
                    :class="[
                      'rounded-full border px-3 py-1 text-xs font-bold uppercase',
                      report.has_error
                        ? 'border-red-200 bg-red-100 text-red-800 dark:border-red-500/30 dark:bg-red-900/60 dark:text-red-200'
                        : 'border-green-200 bg-green-100 text-green-800 dark:border-green-500/30 dark:bg-green-900/60 dark:text-green-200'
                    ]"
                  >
                    {{ report.country }}
                  </span>
                  <span v-if="report.has_error" class="text-red-400 text-sm">✗ 失败</span>
                  <span v-else class="text-green-400 text-sm">✓ 成功</span>
                </div>
                <h3 :class="['text-base font-bold sm:text-lg', report.has_error ? 'text-slate-600 dark:text-slate-400' : 'text-slate-900 dark:text-white']">
                  {{ report.media_name }}
                </h3>
                <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">📅 {{ report.publish_date || eventDate }}</p>
              </div>
              <span class="text-2xl opacity-100">📰</span>
            </div>

            <!-- 报道内容 -->
            <div :class="[
              'mb-4 rounded-lg border-l-2 p-4 leading-relaxed sm:p-5',
              report.has_error
                ? 'border-red-400 bg-red-50 text-sm text-red-900 dark:border-red-500/50 dark:bg-red-950/40 dark:text-red-200'
                : 'border-green-300 bg-white text-sm text-slate-800 dark:border-green-400/50 dark:bg-slate-800/50 dark:text-slate-200'
            ]">
              <div v-if="report.has_error" class="flex items-start gap-2">
                <span class="text-lg flex-shrink-0">⚠️</span>
                <div>
                  <p class="font-semibold text-red-300 mb-1">报道生成失败</p>
                  <p class="text-xs opacity-90">{{ report.content }}</p>
                </div>
              </div>
              <div v-else>
                <!-- 显示预览或完整内容 -->
                <div v-if="!expandedReports[index] && (report.content?.length || 0) > 200" class="space-y-3">
                  <p class="line-clamp-3">{{ report.content }}</p>
                  <button
                    @click="expandedReports[index] = true"
                    class="text-xs font-semibold text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 transition"
                  >
                    📖 展开全文 ({{ report.content?.length || 0 }} 字)
                  </button>
                </div>
                <div v-else class="space-y-2">
                  <p>{{ report.content }}</p>
                  <button
                    v-if="(report.content?.length || 0) > 200"
                    @click="expandedReports[index] = false"
                    class="text-xs font-semibold text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 transition"
                  >
                    📖 折叠
                  </button>
                </div>
              </div>
            </div>

            <!-- 元数据标签 -->
            <div v-if="!report.has_error" class="flex flex-wrap gap-2 text-xs">
              <span v-if="report.report_style" class="rounded-md bg-blue-100 px-2 py-1 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300">
                #{{ report.report_style }}
              </span>
              <span v-if="report.word_count" class="rounded-md bg-slate-100 px-2 py-1 text-slate-700 dark:bg-slate-700/30 dark:text-slate-300">
                📝 ~{{ report.word_count }} 字
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// ===== API 地址配置 =====
const getApiBase = () => {
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8001'
  }
  const protocol = window.location.protocol
  return `${protocol}//${window.location.hostname}:8001`
}
const API_BASE = getApiBase()

// ===== 响应式数据 =====
const eventText = ref('')
const eventDate = ref('')
const loading = ref(false)
const results = ref([])
const receivedCount = ref(0)
const totalCount = ref(0)
const selectedMedia = ref([])
const mediaSearchText = ref('')
const expandedReports = ref({})
const MEDIA_LIMIT = 10

// 错误对象结构
const error = ref({
  code: null,
  title: '',
  message: '',
  detail: '',
  solutions: [],
  icon: ''
})

// ===== 媒体列表（完整列表，从 InquiryView 获取） =====
const allMediaList = ref([
  { media_id: 'media_081', media_name: '路透社', country: '英国' },
  { media_id: 'media_092', media_name: '新华社', country: '中国' },
  { media_id: 'media_042', media_name: '半岛电视台', country: '卡塔尔' },
  { media_id: 'media_048', media_name: '美国有线电视新闻网（CNN）', country: '美国' },
  { media_id: 'media_045', media_name: '《纽约时报》', country: '美国' },
  { media_id: 'media_082', media_name: '英国广播公司（BBC）', country: '英国' },
  { media_id: 'media_023', media_name: '法新社', country: '法国' },
  { media_id: 'media_093', media_name: '《中国日报》', country: '中国' },
  { media_id: 'media_001', media_name: '拉通社', country: '拉丁美洲' },
  { media_id: 'media_002', media_name: '阿拉比电视网', country: '阿联酋' },
  { media_id: 'media_046', media_name: '美联社', country: '美国' },
  { media_id: 'media_054', media_name: '日本广播协会（NHK）', country: '日本' },
  { media_id: 'media_047', media_name: '《华尔街日报》', country: '美国' },
  { media_id: 'media_022', media_name: '俄罗斯卫星通讯社', country: '俄罗斯' },
  { media_id: 'media_089', media_name: '中新社', country: '中国' },
  { media_id: 'media_055', media_name: '日本朝日新闻', country: '日本' },
  // 这里可以添加更多媒体，缩略显示
])

// ===== 计算属性 =====
const filteredMediaList = computed(() => {
  const query = mediaSearchText.value.toLowerCase()
  return allMediaList.value.filter(media =>
    media.media_name.toLowerCase().includes(query) ||
    media.country.toLowerCase().includes(query)
  )
})

const successCount = computed(() => {
  return results.value.filter(r => !r.has_error).length
})

const errorCount = computed(() => {
  return results.value.filter(r => r.has_error).length
})

// ===== 函数 =====
const toggleMediaSelection = (mediaId) => {
  if (selectedMedia.value.includes(mediaId)) {
    selectedMedia.value = selectedMedia.value.filter(m => m !== mediaId)
  } else if (selectedMedia.value.length < MEDIA_LIMIT) {
    selectedMedia.value.push(mediaId)
  }
}

const clearError = () => {
  error.value = {
    code: null,
    title: '',
    message: '',
    detail: '',
    solutions: [],
    icon: ''
  }
}

const setError = (code, title, message, detail = '', solutions = [], icon = '❌') => {
  error.value = {
    code,
    title,
    message,
    detail,
    solutions,
    icon
  }
}

const handleErrorResponse = (statusCode, responseData) => {
  const code = responseData?.code || responseData?.error?.code || 'UNKNOWN_ERROR'
  const message = responseData?.message || responseData?.error?.message || '发生未知错误'
  const detail = responseData?.detail || responseData?.error?.reason || ''

  const errorHandlers = {
    VALIDATION_ERROR: {
      title: '⚠️ 输入验证失败',
      solutions: ['检查事件描述是否为空', '确保已选择至少1个媒体', '检查日期选择']
    },
    DATA_FILE_MISSING: {
      title: '📁 数据文件缺失',
      solutions: ['检查数据文件是否已生成', '联系管理员重新初始化数据']
    },
    LLM_UNAVAILABLE: {
      title: '🤖 LLM API 不可用',
      solutions: ['检查 API 密钥配置', '检查网络连接', '等待服务恢复后重试']
    },
    SIMULATION_FAILED: {
      title: '⚙️ 报道生成失败',
      solutions: ['查看终端日志了解详细错误', '尝试减少选择的媒体数量', '检查 LLM API 配额']
    },
    TIMEOUT_ERROR: {
      title: '⏱️ 请求超时',
      solutions: ['后端响应缓慢，请稍候', '尝试选择较少的媒体', '检查网络连接']
    },
    NETWORK_ERROR: {
      title: '🌐 网络连接失败',
      solutions: ['检查后端服务是否运行', `访问 ${API_BASE}/health 测试连接`]
    }
  }

  const handler = errorHandlers[code] || { title: '❌ 未知错误', solutions: [] }
  setError(code, handler.title, message, detail, handler.solutions, handler.title[0])
}

const runNewsGeneration = async () => {
  clearError()
  results.value = []
  receivedCount.value = 0
  totalCount.value = 0
  loading.value = true

  try {
    const body = {
      event_text: eventText.value,
      event_date: eventDate.value,
      // 确保 media_ids 是普通数组而不是 Proxy
      media_ids: Array.from(selectedMedia.value)
    }
    console.log('请求数据:', { body, apiBase: API_BASE })
    
    // 期望的数据数量 = 发送的 media_ids 数量
    const expectedCount = selectedMedia.value.length
    totalCount.value = expectedCount
    console.log(`📌 期望接收 ${expectedCount} 份报道`)
    
    const response = await fetch(`${API_BASE}/simulate/news`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(120000)
    })
    console.log('响应状态:', response)
    if (!response.ok) {
      try {
        const errorData = await response.json()
        handleErrorResponse(response.status, errorData)
      } catch {
        const httpErrors = {
          400: ['VALIDATION_ERROR', '请求格式错误'],
          422: ['VALIDATION_ERROR', '参数验证失败'],
          503: ['LLM_UNAVAILABLE', '服务暂时不可用'],
          500: ['SIMULATION_FAILED', '服务器内部错误'],
          504: ['TIMEOUT_ERROR', '网关超时']
        }
        const [code, msg] = httpErrors[response.status] || ['SIMULATION_FAILED', '请求失败']
        setError(code, `❌ HTTP ${response.status}`, msg)
      }
      loading.value = false
      return
    }

    if (!response.body) {
      setError(
        'NETWORK_ERROR',
        '🌐 响应异常',
        '后端未返回流式数据体，可能连接中断。',
        '',
        ['检查后端服务是否仍在运行', '查看终端输出是否有错误']
      )
      loading.value = false
      return
    }

    const reader = response.body.getReader()
    let buffer = ''
    let done = false
    let chunkCount = 0

    while (!done) {
      const { value, done: doneReading } = await reader.read()
      done = doneReading

      if (value) {
        chunkCount++
        const decoded = new TextDecoder().decode(value)
        console.log(`📦 接收数据块 #${chunkCount}:`, decoded.substring(0, 100))
        buffer += decoded

        // 按行分割处理 NDJSON（后端返回的是 line-delimited JSON）
        const lines = buffer.split('\n')
        console.log(`📝 分割后的行数: ${lines.length}, 最后一行完整性: ${lines[lines.length - 1].length}`)
        
        // 保留最后一行（可能不完整）
        buffer = lines[lines.length - 1]
        
        // 处理完整的行
        for (let i = 0; i < lines.length - 1; i++) {
          const line = lines[i].trim()
          if (!line) continue
          
          try {
            const report = JSON.parse(line)
            console.log(`✅ 解析成功 - 媒体: ${report.media_id}, 内容长度: ${(report.content || '').length}`)
            
            // 检查是否是有效的报告对象
            if (report.media_id) {
              results.value.push(report)
              receivedCount.value++
              console.log(`📊 进度: ${receivedCount.value}/${expectedCount}`)
            }
          } catch (e) {
            console.warn(`❌ JSON解析失败 (行#${i}):`, line.substring(0, 50), '错误:', e.message)
            continue
          }
        }
      }
    }
    
    console.log(`⏁ 流接收完成。总接收数据块: ${chunkCount}, 最终缓冲区: "${buffer}"`)

    if (results.value.length === 0) {
      setError(
        'PARSE_ERROR',
        '🔨 无结果返回',
        '报道生成完成但未收到任何媒体结果，检查后端日志了解详细信息。',
        '',
        ['查看后端终端的日志输出', '检查所选媒体是否有效', '确保 LLM 服务可用', '尝试选择其他媒体重新提交']
      )
    }
  } catch (err) {
    if (err.name === 'AbortError') {
      setError('TIMEOUT_ERROR', '⏱️ 请求超时', '后端响应超过120秒，请检查后端是否正常。', err.message,
        ['确保后端服务正在运行', '检查网络连接', '尝试减少选择的媒体数量'])
    } else if (err instanceof TypeError && err.message.includes('fetch')) {
      setError('NETWORK_ERROR', '🌐 网络连接失败', '无法连接到后端服务器，请确保后端已启动。', err.message,
        [`启动后端：python -m src.modules.api`, `检查 ${API_BASE} 是否可访问`])
    } else {
      setError('PARSE_ERROR', '⚙️ 处理错误', '在处理响应时发生错误。', err instanceof Error ? err.message : String(err),
        ['尝试刷新页面', '检查浏览器控制台（F12）获取更多信息'])
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>








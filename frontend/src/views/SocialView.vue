<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-slate-100 to-slate-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 p-4 sm:p-6 md:p-8">
    
    <!-- 头部 -->
    <div class="mb-8">
      <h1 class="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white mb-2">
        🌐 受众传播仿真
      </h1>
      <p class="text-sm sm:text-base text-slate-600 dark:text-slate-400">
        模拟事件在社交网络中的传播动态，分析受众的媒介接触行为
      </p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- 左侧：配置面板 -->
      <div class="lg:col-span-1">
        <div class="sticky top-4 space-y-4">
          
          <!-- 事件输入 -->
          <div class="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800 shadow-sm">
            <h2 class="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white">
              <span>📝</span> 事件设置
            </h2>

            <!-- 事件文本 -->
            <div class="space-y-2 mb-4">
              <label class="text-sm font-medium text-slate-700 dark:text-slate-300">
                事件描述 <span class="text-red-500">*</span>
              </label>
              <textarea
                v-model="eventText"
                placeholder="输入要仿真的事件描述..."
                class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-700 dark:text-white dark:placeholder-slate-500"
                rows="4"
              />
            </div>

            <!-- 事件情感 -->
            <div class="space-y-2 mb-4">
              <label class="flex items-center justify-between text-sm font-medium text-slate-700 dark:text-slate-300">
                <span>情感强度</span>
                <span class="text-blue-600 dark:text-blue-400">{{ eventEmotion.toFixed(2) }}</span>
              </label>
              <input
                v-model.number="eventEmotion"
                type="range"
                min="0"
                max="1"
                step="0.1"
                class="w-full rounded-lg"
              />
              <p class="text-xs text-slate-500 dark:text-slate-400">
                0 = 平淡无奇 ↔ 1 = 极度愤怒/激情
              </p>
            </div>

            <!-- 事件立场 -->
            <div class="space-y-2">
              <label class="flex items-center justify-between text-sm font-medium text-slate-700 dark:text-slate-300">
                <span>立场倾向</span>
                <span class="text-blue-600 dark:text-blue-400">{{ eventStance.toFixed(2) }}</span>
              </label>
              <input
                v-model.number="eventStance"
                type="range"
                min="-1"
                max="1"
                step="0.1"
                class="w-full rounded-lg"
              />
              <p class="text-xs text-slate-500 dark:text-slate-400">
                -1 = 坚定反对 ↔ 0 = 中立 ↔ 1 = 坚定支持
              </p>
            </div>
          </div>

          <!-- 参数设置 -->
          <div class="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800 shadow-sm">
            <h2 class="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white">
              <span>⚙️</span> 仿真参数
            </h2>

            <!-- 种子策略 -->
            <div class="space-y-2 mb-4">
              <label class="text-sm font-medium text-slate-700 dark:text-slate-300">
                种子选择策略
              </label>
              <select
                v-model="seedStrategy"
                class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-700 dark:text-white"
              >
                <option value="influence">🎯 高影响力用户</option>
                <option value="emotion">😊 高情感用户</option>
                <option value="random">🎲 随机选择</option>
              </select>
              <p class="text-xs text-slate-500 dark:text-slate-400">
                选择仿真的起始用户类型
              </p>
            </div>

            <!-- 种子数量 -->
            <div class="space-y-2 mb-4">
              <label class="flex items-center justify-between text-sm font-medium text-slate-700 dark:text-slate-300">
                <span>种子数量</span>
                <span class="text-blue-600 dark:text-blue-400">{{ numSeeds }}</span>
              </label>
              <input
                v-model.number="numSeeds"
                type="range"
                min="1"
                max="20"
                step="1"
                class="w-full rounded-lg"
              />
            </div>

            <!-- 是否启用 LLM -->
            <div class="space-y-2 mb-4">
              <label class="flex items-center justify-between text-sm font-medium text-slate-700 dark:text-slate-300">
                <span>启用 LLM 语义增强</span>
                <span class="text-blue-600 dark:text-blue-400">{{ enableLLM ? '已启用' : '未启用' }}</span>
              </label>
              <button
                type="button"
                @click="enableLLM = !enableLLM"
                class="inline-flex items-center justify-center rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 transition hover:border-blue-500 hover:bg-blue-50 dark:border-slate-600 dark:bg-slate-700 dark:text-white dark:hover:border-blue-400 dark:hover:bg-blue-900"
              >
                {{ enableLLM ? '关闭 LLM' : '开启 LLM' }}
              </button>
            </div>

            <!-- 最大步数 -->
            <div class="space-y-2">
              <label class="flex items-center justify-between text-sm font-medium text-slate-700 dark:text-slate-300">
                <span>最大步数</span>
                <span class="text-blue-600 dark:text-blue-400">{{ maxSteps }}</span>
              </label>
              <input
                v-model.number="maxSteps"
                type="range"
                min="5"
                max="50"
                step="5"
                class="w-full rounded-lg"
              />
            </div>
          </div>

          <!-- 提示 -->
          <div class="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-700/30 shadow-sm">
            <div class="space-y-2 text-sm text-slate-700 dark:text-slate-300">
              <p class="flex items-center gap-2"><span>💡</span> <strong>提示：</strong></p>
              <ul class="ml-6 space-y-1 text-xs text-slate-600 dark:text-slate-400">
                <li>• 更高的情感强度会加快信息传播速度</li>
                <li>• 立场相近的用户更容易转发信息</li>
                <li>• 影响力大的用户是最有效的种子</li>
              </ul>
            </div>
          </div>

          <!-- 运行按钮 -->
          <button
            @click="runSimulation"
            :disabled="!eventText.trim() || loading"
            class="w-full rounded-lg bg-gradient-to-r from-blue-600 to-blue-700 px-4 py-3 font-medium text-white shadow-lg transition-all duration-200 hover:shadow-xl hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="!loading" class="flex items-center justify-center gap-2">
              <span>🚀</span> 开始仿真
            </span>
            <span v-else class="flex items-center justify-center gap-2">
              <span class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
              仿真中...
            </span>
          </button>
        </div>
      </div>

      <!-- 右侧：结果展示 -->
      <div class="lg:col-span-2">
        
        <!-- 加载状态 -->
        <div v-if="loading" class="rounded-xl border border-slate-200 bg-white p-8 dark:border-slate-700 dark:bg-slate-800 shadow-sm">
          <div class="flex flex-col items-center justify-center space-y-4">
            <div class="h-12 w-12 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
            <p class="text-sm text-slate-600 dark:text-slate-400">仿真进行中，请稍候...</p>
          </div>
        </div>

        <!-- 错误提示 -->
        <div v-if="error" class="rounded-xl border-l-4 border-red-500 bg-red-50 p-4 dark:border-red-400 dark:bg-red-900/20">
          <div class="flex gap-3">
            <span class="text-lg">❌</span>
            <div>
              <h3 class="font-semibold text-red-900 dark:text-red-100">{{ error }}</h3>
              <p v-if="errorDetail" class="text-sm text-red-800 dark:text-red-200 mt-1">{{ errorDetail }}</p>
            </div>
          </div>
        </div>

        <!-- 结果卡片 -->
        <div v-if="results && !loading" class="space-y-4">
          
          <!-- 过程展示卡片 -->
          <div class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800 shadow-sm">
            <h2 class="mb-4 text-lg font-semibold text-slate-900 dark:text-white">🧩 建模与传播过程</h2>
            <div class="grid gap-4 sm:grid-cols-2">
              <div class="rounded-xl bg-slate-50 p-4 dark:bg-slate-700/30">
                <p class="text-xs text-slate-500 dark:text-slate-400">事件建模</p>
                <p class="text-sm text-slate-800 dark:text-slate-100">{{ eventText }}</p>
                <p class="text-xs text-slate-500 dark:text-slate-400 mt-2">情感：{{ eventEmotion.toFixed(2) }}；立场：{{ eventStance.toFixed(2) }}</p>
              </div>
              <div class="rounded-xl bg-slate-50 p-4 dark:bg-slate-700/30">
                <p class="text-xs text-slate-500 dark:text-slate-400">传播方式</p>
                <p class="text-sm text-slate-800 dark:text-slate-100">规则驱动传播 + {{ enableLLM ? 'LLM 语义增强' : '规则推理' }}</p>
                <p class="text-xs text-slate-500 dark:text-slate-400 mt-2">最大步数：{{ maxSteps }}；种子策略：{{ seedStrategy }}</p>
              </div>
            </div>
          </div>

          <!-- 概览卡片 -->
          <div class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800 shadow-sm">
            <h2 class="mb-4 text-lg font-semibold text-slate-900 dark:text-white">📊 仿真概览</h2>
            
            <div class="grid grid-cols-2 gap-4">
              <div class="rounded-lg bg-blue-50 p-4 dark:bg-blue-900/20">
                <p class="text-xs text-slate-600 dark:text-slate-400">总参与用户</p>
                <p class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ results.metrics.active_nodes_count }}</p>
              </div>
              <div class="rounded-lg bg-green-50 p-4 dark:bg-green-900/20">
                <p class="text-xs text-slate-600 dark:text-slate-400">传播覆盖率</p>
                <p class="text-2xl font-bold text-green-600 dark:text-green-400">
                  {{ (results.metrics.coverage_rate * 100).toFixed(1) }}%
                </p>
              </div>
              <div class="rounded-lg bg-purple-50 p-4 dark:bg-purple-900/20">
                <p class="text-xs text-slate-600 dark:text-slate-400">传播深度</p>
                <p class="text-2xl font-bold text-purple-600 dark:text-purple-400">{{ results.history.length }}</p>
              </div>
              <div class="rounded-lg bg-orange-50 p-4 dark:bg-orange-900/20">
                <p class="text-xs text-slate-600 dark:text-slate-400">平均增长率</p>
                <p class="text-2xl font-bold text-orange-600 dark:text-orange-400">
                  {{ (results.metrics.avg_growth_rate * 100).toFixed(1) }}%
                </p>
              </div>
            </div>
          </div>

          <!-- 传播曲线 -->
          <div class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800 shadow-sm">
            <h2 class="mb-4 text-lg font-semibold text-slate-900 dark:text-white">📈 传播曲线</h2>
            <div class="h-64 rounded-lg bg-slate-50 dark:bg-slate-700/30 flex items-center justify-center">
              <p class="text-sm text-slate-500 dark:text-slate-400">
                步长: {{ results.history.join(' → ') }}
              </p>
            </div>
          </div>

          <!-- 情感和立场分析 -->
          <div class="grid grid-cols-2 gap-4">
            <div class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800 shadow-sm">
              <h3 class="mb-4 text-sm font-semibold text-slate-900 dark:text-white">😊 情感分析</h3>
              <div class="space-y-3">
                <div>
                  <p class="text-xs text-slate-600 dark:text-slate-400">活跃用户平均情感</p>
                  <p class="text-xl font-bold text-slate-900 dark:text-white">
                    {{ results.metrics.active_emotion_mean.toFixed(2) }}
                  </p>
                </div>
                <div>
                  <p class="text-xs text-slate-600 dark:text-slate-400">情感波动</p>
                  <p class="text-xl font-bold text-slate-900 dark:text-white">
                    {{ results.metrics.active_emotion_std.toFixed(2) }}
                  </p>
                </div>
              </div>
            </div>

            <div class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800 shadow-sm">
              <h3 class="mb-4 text-sm font-semibold text-slate-900 dark:text-white">🎯 立场分析</h3>
              <div class="space-y-3">
                <div>
                  <p class="text-xs text-slate-600 dark:text-slate-400">活跃用户平均立场</p>
                  <p class="text-xl font-bold text-slate-900 dark:text-white">
                    {{ results.metrics.active_stance_mean.toFixed(2) }}
                  </p>
                </div>
                <div>
                  <p class="text-xs text-slate-600 dark:text-slate-400">立场分化程度</p>
                  <p class="text-xl font-bold text-slate-900 dark:text-white">
                    {{ results.metrics.stance_divergence.toFixed(2) }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- 种子信息 -->
          <div class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800 shadow-sm">
            <h2 class="mb-4 text-lg font-semibold text-slate-900 dark:text-white">🌱 种子节点</h2>
            <div class="grid grid-cols-2 gap-2">
              <div v-for="seed in results.seeds" :key="seed" class="rounded-lg bg-slate-100 px-3 py-2 text-sm text-slate-700 dark:bg-slate-700 dark:text-slate-300">
                {{ seed }}
              </div>
            </div>
          </div>

          <!-- 每个智能体决策轨迹 -->
          <div class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800 shadow-sm">
            <h2 class="mb-4 text-lg font-semibold text-slate-900 dark:text-white">🧠 智能体决策日志</h2>
            <p class="text-xs text-slate-500 dark:text-slate-400 mb-4">
              展示每个智能体对当前消息的 exposure、action、LLM生成文本与传播概率。
            </p>
            <div v-if="results.decision_trace && results.decision_trace.length" class="space-y-3">
              <div v-for="(item, index) in results.decision_trace.slice(0, 18)" :key="index" class="rounded-lg border border-slate-200 p-3 dark:border-slate-700 dark:bg-slate-900/50">
                <div class="flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500 dark:text-slate-400">
                  <span>步骤：{{ item.step }}</span>
                  <span>智能体：{{ item.agent_id }}</span>
                  <span>来源：{{ item.source_agent_id }}</span>
                  <span>类型：{{ item.recommendation ? '推荐曝光' : '邻居曝光' }}</span>
                </div>
                <div class="mt-2 text-sm text-slate-700 dark:text-slate-200 space-y-1">
                  <p><strong>行为：</strong>{{ item.action }} / {{ item.outcome }}</p>
                  <p>
                    <strong>LLM：</strong>
                    {{ item.use_llm ? '已启用' : '未启用' }}
                    <span v-if="item.llm_error" class="text-red-600 dark:text-red-400">(回退：{{ item.llm_error }})</span>
                  </p>
                  <p><strong>语义分数：</strong>{{ item.semantic_score.toFixed(2) }}，传播概率：{{ item.propagation_prob.toFixed(2) }}</p>
                  <p><strong>生成文本：</strong><span class="whitespace-pre-wrap break-words">{{ item.generated_text || '无生成文本' }}</span></p>
                </div>
              </div>
              <p class="text-xs text-slate-500 dark:text-slate-400">仅展示前 18 条决策，更多数据请查看原始仿真 JSON。</p>
            </div>
            <div v-else class="text-sm text-slate-500 dark:text-slate-400">
              当前仿真尚无可展示的决策轨迹。
            </div>
          </div>

          <!-- AI 分析结果 - 这里的 HTML 绑定已优化 -->
          <div class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800 shadow-sm">
            <h2 class="mb-4 text-lg font-semibold text-slate-900 dark:text-white">🤖 AI 分析</h2>
            <div v-if="analysisLoading" class="text-sm text-slate-600 dark:text-slate-400">正在将仿真数据发送给 AI 进行深度分析...</div>
            <div v-else-if="analysisError" class="text-sm text-red-700 dark:text-red-300">{{ analysisError }}</div>
            <!-- 使用 markdown-body 类并绑定格式化后的 HTML -->
            <div v-else-if="analysis" class="ai-analysis-container prose prose-slate dark:prose-invert max-w-none text-sm">
              <div v-html="analysisFormatted"></div>
            </div>
            <div v-else class="text-sm text-slate-500 dark:text-slate-400">AI 分析结果将在仿真完成后自动生成。</div>
          </div>

          <!-- 原始仿真数据 -->
          <div class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800 shadow-sm">
            <h2 class="mb-4 text-lg font-semibold text-slate-900 dark:text-white">🗂️ 仿真原始数据</h2>
            <pre class="max-h-72 overflow-auto rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs text-slate-700 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100">
{{ rawSimulationJson }}
            </pre>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="!results && !loading && !error" class="rounded-xl border border-slate-200 bg-slate-50 p-8 dark:border-slate-700 dark:bg-slate-700/30 text-center">
          <p class="text-lg text-slate-600 dark:text-slate-400">
            等待仿真结果...
          </p>
          <p class="text-sm text-slate-500 dark:text-slate-500 mt-2">
            设置事件和参数，点击"开始仿真"按钮运行
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
// 需要安装: npm install markdown-it
import MarkdownIt from 'markdown-it'

// 初始化 markdown-it，启用 HTML 支持和表格转换
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

// API 基础URL
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8001'

// 事件参数
const eventText = ref('天舟九号货运飞船已受控再入大气层，少量残骸落入预定安全海域。')
const eventEmotion = ref(0.7)
const eventStance = ref(0.6)

// 仿真参数
const seedStrategy = ref('influence')
const numSeeds = ref(5)
const maxSteps = ref(10)
const enableLLM = ref(true)

// 状态
const loading = ref(false)
const error = ref<string | null>(null)
const errorDetail = ref<string | null>(null)
const results = ref<any>(null)
const rawSimulationJson = ref('')
const analysis = ref<string | null>(null)
const analysisLoading = ref(false)
const analysisError = ref<string | null>(null)

// 修改后的格式化逻辑：使用 markdown-it 渲染
const analysisFormatted = computed(() => {
  if (!analysis.value) return ''
  return md.render(analysis.value)
})

async function analyzeSimulation(simulationData: any) {
  analysisLoading.value = true
  analysisError.value = null
  analysis.value = null

  try {
    const response = await fetch(`${API_BASE}/simulate/social/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        simulation_data: simulationData,
      })
    })

    if (!response.ok) {
      const errorData = await response.json()
      analysisError.value = errorData.message || 'AI 分析接口请求失败'
      return
    }

    const data = await response.json()
    if (data.status === 'success') {
      analysis.value = data.analysis
    } else {
      analysisError.value = data.message || 'AI 分析失败'
    }
  } catch (e: any) {
    analysisError.value = 'AI 分析请求失败'
  } finally {
    analysisLoading.value = false
  }
}

async function runSimulation() {
  if (!eventText.value.trim()) {
    error.value = '请输入事件描述'
    return
  }

  loading.value = true
  error.value = null
  errorDetail.value = null
  results.value = null

  try {
    const response = await fetch(`${API_BASE}/simulate/social`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        event_text: eventText.value,
        event_emotion: eventEmotion.value,
        event_stance: eventStance.value,
        num_seeds: numSeeds.value,
        seed_strategy: seedStrategy.value,
        max_steps: maxSteps.value,
        enable_llm: enableLLM.value,
        experiment_name: `social_sim_${Date.now()}`
      })
    })

    if (!response.ok) {
      const errorData = await response.json()
      error.value = errorData.error?.message || '仿真失败'
      errorDetail.value = errorData.error?.reason || ''
      return
    }

    const data = await response.json()
    if (data.status === 'success') {
      results.value = data.data.results
      rawSimulationJson.value = JSON.stringify(data.data, null, 2)
      await analyzeSimulation(data.data)
    } else {
      error.value = data.error?.message || '仿真执行失败'
      errorDetail.value = data.error?.reason || ''
    }
  } catch (e: any) {
    error.value = '网络错误'
    errorDetail.value = e.message || '无法连接到服务器'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 自定义滑块样式 */
input[type="range"] {
  accent-color: rgb(59, 130, 246);
}

@media (prefers-color-scheme: dark) {
  input[type="range"] {
    accent-color: rgb(96, 165, 250);
  }
}

/* AI 分析内容样式美化 (Markdown 支持) */
:deep(.ai-analysis-container table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  border: 1px solid #e2e8f0;
}
:deep(.ai-analysis-container th), 
:deep(.ai-analysis-container td) {
  border: 1px solid #e2e8f0;
  padding: 0.5rem;
  text-align: left;
}
:deep(.ai-analysis-container th) {
  background-color: #f8fafc;
  font-weight: 600;
}
:deep(.ai-analysis-container ul), 
:deep(.ai-analysis-container ol) {
  padding-left: 1.5rem;
  margin: 1rem 0;
  list-style: disc;
}
:deep(.ai-analysis-container h1),
:deep(.ai-analysis-container h2),
:deep(.ai-analysis-container h3) {
  font-weight: bold;
  margin-top: 1.25rem;
  margin-bottom: 0.5rem;
}
:deep(.ai-analysis-container p) {
  margin-bottom: 0.75rem;
  line-height: 1.6;
}
</style>
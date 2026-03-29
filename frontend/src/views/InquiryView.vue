<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
    <div class="max-w-7xl mx-auto space-y-6">
      <!-- 标题头 -->
      <header class="border-b border-slate-700/50 pb-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-4xl font-bold text-white tracking-tight flex items-center gap-3">
              <span class="text-5xl">🎙️</span> 媒体提问场景仿真
            </h1>
            <p class="text-slate-400 mt-3">基于 GSS 范式，模拟多国媒体针对特定科技事件的反应逻辑</p>
          </div>
        </div>
      </header>

      <!-- 输入面板 -->
      <div class="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-8 shadow-2xl border border-slate-700/50 backdrop-blur">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- 左侧：事件输入与媒体选择 -->
          <div class="lg:col-span-2 space-y-6">
            <!-- 事件描述 -->
            <div>
              <label class="block text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
                <span class="text-lg">📝</span> 事件描述 (Event Input)
              </label>
              <textarea 
                v-model="eventText"
                class="w-full h-36 bg-slate-700/30 border border-slate-600/50 rounded-xl p-4 text-slate-100 focus:ring-2 focus:ring-blue-500/50 outline-none focus:border-blue-500/50 transition placeholder-slate-500"
                placeholder="请输入需要仿真的科技事件内容，如：'2月12日，中国一箭七星发射巴基斯坦卫星...'"
              ></textarea>
            </div>

            <!-- 媒体选择 -->
            <div>
              <div class="flex items-center justify-between mb-3">
                <label class="text-sm font-semibold text-slate-200 flex items-center gap-2">
                  <span class="text-lg">📺</span> 选择媒体 <span class="text-xs text-slate-400">(最多 {{ MEDIA_LIMIT }} 个)</span>
                </label>
                <button 
                  v-if="selectedMedia.length > 0"
                  @click="clearSelection"
                  class="text-xs px-3 py-1 bg-slate-700/50 hover:bg-slate-700 text-slate-300 rounded-lg transition"
                >
                  ✕ 清空
                </button>
              </div>

              <!-- 搜索框 -->
              <div class="mb-3 relative">
                <input 
                  v-model="mediaSearchText"
                  type="text"
                  placeholder="🔍 搜索媒体名称或国家..."
                  class="w-full bg-slate-700/30 border border-slate-600/50 rounded-lg px-4 py-2 text-slate-100 text-sm focus:ring-2 focus:ring-blue-500/50 outline-none focus:border-blue-500/50 transition placeholder-slate-500"
                />
                <div v-if="mediaSearchText" class="absolute right-3 top-2.5 text-slate-400 text-sm cursor-pointer hover:text-slate-200" @click="mediaSearchText = ''">✕</div>
              </div>

              <!-- 媒体列表 -->
              <div class="max-h-48 overflow-y-auto bg-slate-700/20 rounded-xl border border-slate-600/30 p-4 space-y-2">
                <div v-if="allMediaList.length === 0" class="text-slate-500 text-sm py-8 text-center">媒体列表加载中...</div>
                <div v-else-if="filteredMediaList.length === 0" class="text-slate-500 text-sm py-8 text-center">
                  <p>没有找到匹配的媒体</p>
                  <p class="text-xs mt-2">试试其他搜索关键词</p>
                </div>
                <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  <label v-for="media in filteredMediaList" :key="media.media_id" 
                         class="flex items-center space-x-3 text-slate-300 text-sm cursor-pointer group hover:bg-slate-700/30 p-2 rounded-lg transition">
                    <input type="checkbox"
                           :value="media.media_id"
                           v-model="selectedMedia"
                           @change="onMediaSelected"
                           :disabled="isMediaLimit && !selectedMedia.includes(media.media_id)"
                           class="w-4 h-4 rounded cursor-pointer accent-blue-500"
                    >
                    <span class="group-hover:text-slate-100 transition">
                      <span class="font-medium">{{ media.media_name }}</span>
                      <span class="text-slate-500 ml-1 text-xs">({{ media.country }})</span>
                    </span>
                  </label>
                </div>
              </div>

              <!-- 选中状态提示 -->
              <div v-if="selectedMedia.length > 0" class="text-xs text-blue-400 mt-2 flex items-center gap-1">
                <span>✓</span> 已选 {{ selectedMedia.length }} 个媒体
              </div>
              <div v-if="isMediaLimit" class="text-xs text-amber-400 mt-2 flex items-center gap-1">
                <span>⚠</span> 已达最大数量限制
              </div>
            </div>
          </div>

          <!-- 右侧：操作面板 -->
          <div class="flex flex-col justify-between">
            <div class="bg-slate-700/20 rounded-xl p-6 border border-slate-600/30 space-y-4">
              <div class="text-sm text-slate-300 space-y-2">
                <p class="flex items-center gap-2"><span>💡</span> <strong>提示：</strong></p>
                <ul class="text-xs text-slate-400 space-y-1 ml-6">
                  <li>• 不选媒体将使用全部媒体</li>
                  <li>• 选择媒体数量越少越快</li>
                  <li>• 结果包含参与和不参与的媒体</li>
                  <li>• 优化后每媒体仅需 1 次大模型调用</li>
                </ul>
              </div>
            </div>
            <button 
              @click="runInquiry"
              :disabled="loading || !eventText.trim()"
              class="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 disabled:from-slate-600 disabled:to-slate-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-4 rounded-xl transition-all shadow-lg flex items-center justify-center gap-2 text-lg"
            >
              <span v-if="loading" class="animate-spin text-xl">⚙️</span>
              <span v-else class="text-xl">▶️</span>
              {{ loading ? '仿真计算中...' : '开启仿真' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 错误信息面板 -->
      <div v-if="error.message" 
           :class="[
             'rounded-xl border-l-4 p-6 shadow-xl backdrop-blur transition-all duration-300',
             errorStyleClass
           ]">
        <div class="flex items-start justify-between gap-4">
          <div class="flex items-start gap-4 flex-1">
            <span class="text-3xl mt-1">{{ error.icon }}</span>
            <div class="flex-1">
              <p class="font-bold text-lg mb-2">{{ error.title }}</p>
              <p class="mb-3 leading-relaxed">{{ error.message }}</p>
              
              <!-- 针对不同错误代码的解决方案 -->
              <div v-if="error.solutions.length > 0" class="bg-black/20 rounded-lg p-4 mb-3 border border-white/10">
                <p class="text-xs font-semibold uppercase mb-2 opacity-75">💡 解决方案：</p>
                <ul class="space-y-2 text-xs">
                  <li v-for="(solution, idx) in error.solutions" :key="idx" class="flex gap-2">
                    <span class="flex-shrink-0">→</span>
                    <span>{{ solution }}</span>
                  </li>
                </ul>
              </div>

              <!-- 详细信息 -->
              <div v-if="error.detail" class="text-xs opacity-75 bg-black/20 rounded-lg p-3 mb-3 font-mono border border-white/5">
                <p class="text-orange-300">{{ error.detail }}</p>
              </div>

              <!-- 额外建议 -->
              <p v-if="error.suggestion" class="text-xs opacity-70 italic">
                📌 {{ error.suggestion }}
              </p>
            </div>
          </div>
          <button 
            @click="clearError"
            class="flex-shrink-0 text-xl hover:opacity-70 transition p-2"
            title="关闭错误提示"
          >
            ✕
          </button>
        </div>
      </div>

      <!-- 结果展示 -->
      <div v-if="results.length > 0 || loading" class="space-y-6">
        <!-- 异常警告 -->
        <div v-if="errorCount > 0" class="bg-red-950/40 rounded-xl p-6 border-l-4 border-red-500/50 shadow-lg">
          <div class="flex items-start gap-3">
            <span class="text-3xl flex-shrink-0">⚠️</span>
            <div class="flex-1">
              <h3 class="text-red-300 font-semibold mb-2">检测到 {{ errorCount }} 个后端处理异常</h3>
              <p class="text-red-200 text-sm mb-3">部分媒体的响应因后端模块异常而失败。这通常是由于 LLM API 不可用或网络连接问题。</p>
              <div class="text-xs text-red-300 space-y-1">
                <p>🔧 故障排查步骤：</p>
                <ul class="list-disc list-inside ml-2 space-y-1">
                  <li>检查所有 LLM API（智谱、DeepSeek、OpenAI）的配置和密钥</li>
                  <li>确保 .env 文件中的 API 密钥有效且未过期</li>
                  <li>查看后端终端输出获取详细错误信息</li>
                  <li>等待 API 服务恢复后重试</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 进度条 -->
        <div v-if="loading" class="bg-slate-800 rounded-xl p-6 border border-slate-700/50 shadow-lg">
          <div class="flex items-center space-x-4 mb-4">
            <span class="animate-spin text-3xl">⚙️</span>
            <div class="flex-1">
              <p class="text-slate-200 font-semibold">仿真进行中...</p>
              <p class="text-slate-400 text-sm">已收到 <span class="text-blue-400 font-bold">{{ receivedCount }}</span> / <span class="text-slate-300 font-bold">{{ totalCount > 0 ? totalCount : '...' }}</span> 条结果</p>
            </div>
          </div>
          <div class="h-3 bg-slate-700 rounded-full overflow-hidden border border-slate-600/50">
            <div class="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-300 rounded-full" 
                 :style="{ width: totalCount > 0 ? (100 * receivedCount / totalCount) + '%' : '15%' }"></div>
          </div>
        </div>

        <!-- 结果统计 -->
        <div v-if="results.length > 0 && !loading" class="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div class="rounded-xl bg-slate-800 border border-slate-700/50 p-4 text-center">
            <p class="text-slate-400 text-xs font-semibold mb-1">总计</p>
            <p class="text-4xl font-bold text-white">{{ validResults.length }}</p>
            <p v-if="errorCount > 0" class="text-xs text-red-400 mt-1">异常: {{ errorCount }}</p>
          </div>
          <div class="rounded-xl bg-blue-950/40 border border-blue-500/30 p-4 text-center">
            <p class="text-blue-300 text-xs font-semibold mb-1">参与提问</p>
            <p class="text-4xl font-bold text-blue-400">{{ participatingCount }}</p>
          </div>
          <div class="rounded-xl bg-slate-700/30 border border-slate-600/50 p-4 text-center">
            <p class="text-slate-300 text-xs font-semibold mb-1">不参与</p>
            <p class="text-4xl font-bold text-slate-400">{{ validResults.length - participatingCount }}</p>
          </div>
          <div v-if="errorCount > 0" class="rounded-xl bg-red-950/40 border border-red-500/30 p-4 text-center">
            <p class="text-red-300 text-xs font-semibold mb-1">异常处理</p>
            <p class="text-4xl font-bold text-red-400">{{ errorCount }}</p>
          </div>
          <div class="rounded-xl bg-slate-800 border border-slate-700/50 p-4 text-center">
            <p class="text-slate-400 text-xs font-semibold mb-1">参与率</p>
            <p class="text-4xl font-bold text-slate-300">{{ validResults.length > 0 ? ((100 * participatingCount / validResults.length).toFixed(1)) : 0 }}%</p>
          </div>
        </div>

        <!-- 结果卡片网格 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div v-for="(res, index) in results" :key="index" 
               :class="[
                 'rounded-xl p-6 shadow-lg border-l-4 backdrop-blur transition-all duration-300',
                 res.has_error
                   ? 'bg-gradient-to-br from-red-950/40 to-slate-900/40 border-red-500/50 hover:border-red-400 hover:shadow-red-500/20 opacity-90'
                   : res.is_participating 
                     ? 'bg-gradient-to-br from-blue-950/40 to-slate-900/40 border-blue-500/50 hover:border-blue-400 hover:shadow-blue-500/20' 
                     : 'bg-gradient-to-br from-slate-800/30 to-slate-900/30 border-slate-700/50 hover:border-slate-600 opacity-75'
               ]">
            <!-- 媒体头部 -->
            <div class="flex justify-between items-start mb-4">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <span :class="[
                    'px-3 py-1 text-xs font-bold rounded-full uppercase',
                    res.is_participating 
                      ? 'bg-blue-900/60 text-blue-200 border border-blue-500/30' 
                      : 'bg-slate-700/60 text-slate-400 border border-slate-600/30'
                  ]">
                    {{ res.country }}
                  </span>
                  <span v-if="res.is_participating" class="text-blue-400 text-sm">✓ 参与</span>
                  <span v-else class="text-slate-500 text-sm">✗ 不参与</span>
                </div>
                <h3 :class="['text-lg font-bold', res.is_participating ? 'text-white' : 'text-slate-400']">
                  {{ res.media_name }}
                </h3>
              </div>
              <span :class="[
                'text-2xl', 
                res.is_participating ? 'opacity-100' : 'opacity-50'
              ]">
                🎬
              </span>
            </div>

            <!-- 媒体内容 -->
            <div :class="[
              'rounded-lg p-5 mb-3 border-l-2 italic leading-relaxed',
              res.has_error
                ? 'bg-red-950/40 border-red-500/50 text-red-200 text-sm'
                : res.is_participating 
                  ? 'bg-slate-800/50 border-blue-400/50 text-slate-200 text-sm' 
                  : 'bg-slate-800/30 border-slate-600/30 text-slate-500 text-xs'
            ]">
              <div v-if="res.has_error" class="flex items-start gap-2">
                <span class="text-lg flex-shrink-0">⚠️</span>
                <div>
                  <p class="font-semibold text-red-300 mb-1">后端处理异常</p>
                  <p class="text-xs opacity-90">{{ res.content }}</p>
                </div>
              </div>
              <div v-else>
                {{ res.content }}
              </div>
            </div>

            <!-- 标签 -->
            <div class="flex gap-2 text-xs">
              <span :class="[
                'px-2 py-1 rounded-md',
                res.is_participating 
                  ? 'bg-blue-900/50 text-blue-300' 
                  : 'bg-slate-700/30 text-slate-500'
              ]">
                #{{ res.behavior_tag }}
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

// ===== 响应式数据 =====
const eventText = ref('')
const loading = ref(false)
const results = ref([])
const receivedCount = ref(0)
const totalCount = ref(0)
const selectedMedia = ref([])
const mediaSearchText = ref('')
const MEDIA_LIMIT = 15

// 错误对象结构
const error = ref({
  code: null,
  title: '',
  message: '',
  detail: '',
  solutions: [],
  suggestion: '',
  icon: ''
})

// ===== 媒体列表（完整列表） =====
const allMediaList = ref([
  { media_id: 'media_081', media_name: '路透社', country: '英国' },
  { media_id: 'media_092', media_name: '新华社', country: '中国' },
  { media_id: 'media_042', media_name: '半岛电视台', country: '卡塔尔' },
  { media_id: 'media_079', media_name: '《印度教徒报》', country: '印度' },
  { media_id: 'media_048', media_name: '美国有线电视新闻网（CNN）', country: '美国' },
  { media_id: 'media_071', media_name: '埃菲社', country: '西班牙' },
  { media_id: 'media_038', media_name: '荷兰广播电视协会', country: '荷兰' },
  { media_id: 'media_025', media_name: '法国《世界报》', country: '法国' },
  { media_id: 'media_067', media_name: '土耳其阿纳多卢通讯社', country: '土耳其' },
  { media_id: 'media_046', media_name: '美联社', country: '美国' },
  { media_id: 'media_022', media_name: '俄罗斯卫星通讯社', country: '俄罗斯' },
  { media_id: 'media_089', media_name: '中新社', country: '中国' },
  { media_id: 'media_055', media_name: '日本朝日新闻', country: '日本' },
  { media_id: 'media_116', media_name: '《南华早报》', country: '香港' },
  { media_id: 'media_021', media_name: '今日俄罗斯', country: '俄罗斯' },
  { media_id: 'media_024', media_name: '法兰西24电视台', country: '法国' },
  { media_id: 'media_072', media_name: '西班牙《阿贝赛报》', country: '西班牙' },
  { media_id: 'media_082', media_name: '英国广播公司（BBC）', country: '英国' },
  { media_id: 'media_093', media_name: '《中国日报》', country: '中国' },
  { media_id: 'media_004', media_name: '巴通社', country: '巴西' },
  { media_id: 'media_099', media_name: '《北京日报》', country: '中国' },
  { media_id: 'media_045', media_name: '《纽约时报》', country: '美国' },
  { media_id: 'media_044', media_name: '美国全国公共广播电台（NPR）', country: '美国' },
  { media_id: 'media_019', media_name: '俄通塔斯社', country: '俄罗斯' },
  { media_id: 'media_020', media_name: '俄新社', country: '俄罗斯' },
  { media_id: 'media_074', media_name: '西班牙《国家报》', country: '西班牙' },
  { media_id: 'media_009', media_name: '巴西UOL媒体集团', country: '巴西' },
  { media_id: 'media_032', media_name: '韩国广播公司（KBS）', country: '韩国' },
  { media_id: 'media_112', media_name: '凤凰卫视', country: '香港' },
  { media_id: 'media_063', media_name: '日本《东京新闻》', country: '日本' },
  { media_id: 'media_075', media_name: '伊拉克如道电视台', country: '伊拉克' },
  { media_id: 'media_058', media_name: '日本富士电视台', country: '日本' },
  { media_id: 'media_087', media_name: '越南之声广播电台', country: '越南' },
  { media_id: 'media_069', media_name: '委内瑞拉南方电视台', country: '委内瑞拉' },
  { media_id: 'media_098', media_name: '中国国际电视台（CGTN）', country: '中国' },
  { media_id: 'media_011', media_name: '波兰电台', country: '波兰' },
  { media_id: 'media_028', media_name: '古巴拉美社', country: '古巴' },
  { media_id: 'media_115', media_name: '香港无线电视（TVB）', country: '香港' },
  { media_id: 'media_018', media_name: '德国《明镜》周刊', country: '德国' },
  { media_id: 'media_006', media_name: '巴西《圣保罗页报》', country: '巴西' },
  { media_id: 'media_041', media_name: '《荷兰电讯报》', country: '荷兰' },
  { media_id: 'media_010', media_name: '波兰通讯社', country: '波兰' },
  { media_id: 'media_084', media_name: '英国天空新闻', country: '英国' },
  { media_id: 'media_105', media_name: '深圳卫视直新闻', country: '中国' },
  { media_id: 'media_096', media_name: '湖北广播电视台', country: '中国' },
  { media_id: 'media_043', media_name: '彭博社', country: '美国' },
  { media_id: 'media_030', media_name: '韩联社', country: '韩国' },
  { media_id: 'media_101', media_name: '《人民日报》', country: '中国' },
  { media_id: 'media_053', media_name: '日本共同社', country: '日本' },
  { media_id: 'media_007', media_name: '巴西劳动者电视台', country: '巴西' },
  { media_id: 'media_049', media_name: 'CNBC', country: '美国' },
  { media_id: 'media_070', media_name: '乌克兰国家通讯社', country: '乌克兰' },
  { media_id: 'media_031', media_name: '韩国新一社', country: '韩国' },
  { media_id: 'media_016', media_name: '德国电视一台', country: '德国' },
  { media_id: 'media_094', media_name: '《澎湃新闻》', country: '中国' },
  { media_id: 'media_086', media_name: '天空新闻', country: '英国' },
  { media_id: 'media_107', media_name: '湖北卫视', country: '中国' },
  { media_id: 'media_083', media_name: '《金融时报》', country: '英国' },
  { media_id: 'media_064', media_name: '日本《北海道新闻》', country: '日本' },
  { media_id: 'media_036', media_name: '韩国CHANNEL A电视台', country: '韩国' },
  { media_id: 'media_085', media_name: '英国独立电视新闻', country: '英国' },
  { media_id: 'media_017', media_name: '德国电视二台', country: '德国' },
  { media_id: 'media_052', media_name: '美国专题新闻社', country: '美国' },
  { media_id: 'media_035', media_name: '韩国联合有线电视台', country: '韩国' },
  { media_id: 'media_076', media_name: '安莎社', country: '意大利' },
  { media_id: 'media_034', media_name: '韩国文化广播公司（MBC）', country: '韩国' },
  { media_id: 'media_056', media_name: '日本经济新闻', country: '日本' },
  { media_id: 'media_012', media_name: '《澳人报》', country: '澳大利亚' },
  { media_id: 'media_026', media_name: '芬兰《赫尔辛基新闻》', country: '芬兰' },
  { media_id: 'media_068', media_name: '土耳其国家广播电视总台', country: '土耳其' },
  { media_id: 'media_002', media_name: '阿拉比电视网 阿拉比亚电视台', country: '阿联酋' },
  { media_id: 'media_027', media_name: '芬兰广播公司', country: '芬兰' },
  { media_id: 'media_008', media_name: '真实巴西', country: '巴西' },
  { media_id: 'media_103', media_name: '总台央视中文国际频道', country: '中国' },
  { media_id: 'media_110', media_name: '《澳门月刊》', country: '澳门' },
  { media_id: 'media_109', media_name: '澳亚卫视', country: '澳门' },
  { media_id: 'media_005', media_name: '巴西《环球报》', country: '巴西' },
  { media_id: 'media_057', media_name: '日本《读卖新闻》', country: '日本' },
  { media_id: 'media_111', media_name: '澳门月刊', country: '澳门' },
  { media_id: 'media_051', media_name: '美国消费者新闻与商业频道', country: '美国' },
  { media_id: 'media_077', media_name: '印度报业托拉斯社', country: '印度' },
  { media_id: 'media_088', media_name: '中央广播电视总台', country: '中国' },
  { media_id: 'media_037', media_name: '韩国首尔电视台', country: '韩国' },
  { media_id: 'media_104', media_name: '北京广播电视台', country: '中国' },
  { media_id: 'media_073', media_name: '西班牙埃菲社', country: '西班牙' },
  { media_id: 'media_065', media_name: '瑞典国家广播电台', country: '瑞典' },
  { media_id: 'media_054', media_name: '日本广播协会（NHK）', country: '日本' },
  { media_id: 'media_091', media_name: '深圳卫视', country: '中国' },
  { media_id: 'media_014', media_name: '丹麦广播公司', country: '丹麦' },
  { media_id: 'media_047', media_name: '《华尔街日报》', country: '美国' },
  { media_id: 'media_059', media_name: '日本东京电视台', country: '日本' },
  { media_id: 'media_003', media_name: '中阿卫视', country: '阿联酋' },
  { media_id: 'media_106', media_name: '总台央视华语环球节目中心', country: '中国' },
  { media_id: 'media_062', media_name: '朝日电视台', country: '日本' },
  { media_id: 'media_023', media_name: '法新社', country: '法国' },
  { media_id: 'media_108', media_name: '总台新闻中心', country: '中国' },
  { media_id: 'media_066', media_name: '沙特东方电视台', country: '沙特' },
  { media_id: 'media_095', media_name: '东方卫视', country: '中国' },
  { media_id: 'media_102', media_name: '总台中国之声', country: '中国' },
  { media_id: 'media_040', media_name: '《新鹿特丹商业报》', country: '荷兰' },
  { media_id: 'media_097', media_name: '《北京青年报》', country: '中国' },
  { media_id: 'media_100', media_name: '总台华语环球节目中心', country: '中国' },
  { media_id: 'media_029', media_name: '哈萨克斯坦24KZ', country: '哈萨克斯坦' },
  { media_id: 'media_061', media_name: '日本时事通讯社', country: '日本' },
  { media_id: 'media_039', media_name: '荷兰《忠诚报》', country: '荷兰' },
  { media_id: 'media_078', media_name: '印度广播公司', country: '印度' },
  { media_id: 'media_090', media_name: '《环球时报》', country: '中国' },
  { media_id: 'media_050', media_name: '美国国际市场新闻社', country: '美国' },
  { media_id: 'media_113', media_name: '香港中评社', country: '香港' },
  { media_id: 'media_114', media_name: '香港电台', country: '香港' },
  { media_id: 'media_015', media_name: '德新社', country: '德国' },
  { media_id: 'media_060', media_name: '日本电视网', country: '日本' },
  { media_id: 'media_033', media_name: '韩国《中央日报》', country: '韩国' },
  { media_id: 'media_001', media_name: '拉通社', country: '拉丁美洲' },
  { media_id: 'media_013', media_name: '伊朗声像组织', country: '伊朗' },
  { media_id: 'media_080', media_name: '印尼安塔拉通讯社', country: '印度尼西亚' },
])

// ===== 计算属性 =====
const errorStyleClass = computed(() => {
  const baseClass = 'border-l-4'
  const codeToClass = {
    'VALIDATION_ERROR': 'border-amber-500/50 bg-amber-950/40 text-amber-200',
    'DATA_FILE_MISSING': 'border-purple-500/50 bg-purple-950/40 text-purple-200',
    'DATA_READ_FAILED': 'border-purple-500/50 bg-purple-950/40 text-purple-200',
    'LLM_UNAVAILABLE': 'border-orange-500/50 bg-orange-950/40 text-orange-200',
    'SIMULATION_FAILED': 'border-red-500/50 bg-red-950/40 text-red-200',
    'NETWORK_ERROR': 'border-red-500/50 bg-red-950/40 text-red-200',
    'PARSE_ERROR': 'border-red-500/50 bg-red-950/40 text-red-200',
    'TIMEOUT_ERROR': 'border-orange-500/50 bg-orange-950/40 text-orange-200'
  }
  return `${baseClass} ${codeToClass[error.value.code] || 'border-red-500/50 bg-red-950/40 text-red-200'}`
})

// 过滤后的媒体列表（根据搜索文本）
const filteredMediaList = computed(() => {
  if (!mediaSearchText.value.trim()) {
    return allMediaList.value
  }
  const query = mediaSearchText.value.toLowerCase()
  return allMediaList.value.filter(media => 
    media.media_name.toLowerCase().includes(query) || 
    media.country.toLowerCase().includes(query)
  )
})

const isMediaLimit = computed(() => selectedMedia.value.length >= MEDIA_LIMIT)
const participatingCount = computed(() => results.value.filter(r => r.is_participating && !r.has_error).length)
const errorCount = computed(() => results.value.filter(r => r.has_error).length)
const validResults = computed(() => results.value.filter(r => !r.has_error))

// ===== 方法 =====

// 检测响应内容是否包含后端异常标记
const isErrorResponse = (content) => {
  if (!content) return false
  const errorKeywords = [
    '模块异常',
    '降级处理',
    '不可用',
    '无法连接',
    '失败',
    '错误',
    '异常',
    'error',
    'Error',
    'Exception'
  ]
  return errorKeywords.some(keyword => content.includes(keyword))
}

// 清空选中媒体
const clearSelection = () => {
  selectedMedia.value = []
}

// 清空错误提示
const clearError = () => {
  error.value = {
    code: null,
    title: '',
    message: '',
    detail: '',
    solutions: [],
    suggestion: '',
    icon: ''
  }
}

// 设置错误信息
const setError = (code, title, message, detail = '', solutions = [], suggestion = '', icon = '❌') => {
  error.value = {
    code,
    title,
    message,
    detail,
    solutions,
    suggestion,
    icon
  }
}

// 媒体选择后的回调（清空搜索框）
const onMediaSelected = () => {
  mediaSearchText.value = ''
}

// 处理错误响应
const handleErrorResponse = (statusCode, responseData) => {
  const code = responseData?.code || responseData?.error?.code || 'UNKNOWN_ERROR'
  const message = responseData?.message || responseData?.error?.message || '发生未知错误'
  const detail = responseData?.detail || responseData?.error?.reason || responseData?.error?.detail || ''

  const errorHandlers = {
    'VALIDATION_ERROR': {
      title: '⚠️ 输入参数错误',
      message: '您的输入不符合要求，请检查后重试。',
      icon: '⚠️',
      solutions: [
        '请确保事件描述不为空',
        '事件描述长度应在1-10000字符之间',
        '避免只输入空格或特殊符号'
      ],
      suggestion: '如果问题持续存在，请尝试刷新页面重新开始。'
    },
    'DATA_FILE_MISSING': {
      title: '🔓 后端配置错误',
      message: '媒体数据文件找不到。这是后端配置问题，不是您的错。',
      icon: '🔓',
      solutions: [
        '确保后端服务在项目根目录启动：python -m src.modules.api',
        '检查文件是否存在：data/processed/media_science_inquiring_generalized.csv',
        '确认项目完整性，可能需要重新下载或拉取最新代码'
      ],
      suggestion: '若问题持续，请通知系统管理员。'
    },
    'DATA_READ_FAILED': {
      title: '📂 文件读取失败',
      message: '无法读取媒体数据文件。后端可能有权限问题或文件损坏。',
      icon: '📂',
      solutions: [
        '检查文件权限（确保后端进程有读权限）',
        '尝试重启后端服务',
        '检查数据文件是否被其他程序占用或损坏'
      ],
      suggestion: '如果多次重试仍失败，请重新部署应用。'
    },
    'LLM_UNAVAILABLE': {
      title: '🤖 大模型服务不可用',
      message: '无法连接到配置的大模型服务（智谱/DeepSeek/OpenAI）。',
      icon: '🤖',
      solutions: [
        '检查网络连接是否正常',
        '验证 .env 配置文件中的 API 密钥是否正确',
        '检查 .env 中的 PRIMARY_PROVIDER 配置（置顶供应商）',
        '尝试切换不同的大模型供应商（如从zhipu改为deepseek）',
        '确认 API 密钥未过期或达到配额限制'
      ],
      suggestion: '若所有供应商都不可用，请检查网络和配置，可能需要更换 API 账号。'
    },
    'SIMULATION_FAILED': {
      title: '⚡ 仿真执行失败',
      message: '在处理您的请求时发生了内部错误。',
      icon: '⚡',
      solutions: [
        '检查事件描述是否包含特殊字符或不支持的内容',
        '尝试用更简洁的事件描述重新提交',
        '减少选中的媒体数量，使用全部媒体而不是部分',
        '查看终端输出是否有具体错误信息'
      ],
      suggestion: '如果可以接受，请提供错误信息给系统管理员以改进系统。'
    },
    'NETWORK_ERROR': {
      title: '🌐 网络连接失败',
      message: '无法连接到后端服务器。请检查后端是否正常运行。',
      icon: '🌐',
      solutions: [
        '确保后端服务已启动：python -m src.modules.api',
        '检查后端服务地址：http://localhost:8000',
        '验证防火墙或代理设置没有阻止连接',
        '确保前端能访问后端（可能需要CORS配置）'
      ],
      suggestion: '在终端运行后端服务后，等待2-3秒再尝试。'
    },
    'TIMEOUT_ERROR': {
      title: '⏱️ 请求超时',
      message: '后端响应耗时过长。可能是大模型响应缓慢。',
      icon: '⏱️',
      solutions: [
        '检查网络连接是否稳定',
        '尝试减少输入的事件描述长度',
        '减少选中的媒体数量',
        '尝试用低延迟的大模型供应商（如DeepSeek）'
      ],
      suggestion: '如果依然超时，可能是大模型供应商负载过高，请稍后再试。'
    },
    'PARSE_ERROR': {
      title: '🔨 响应解析错误',
      message: '无法解析后端返回的数据。可能是后端版本不匹配。',
      icon: '🔨',
      solutions: [
        '尝试刷新页面',
        '清除浏览器缓存（Ctrl+Shift+Del）',
        '确保前端版本与后端版本匹配',
        '尝试用新的浏览器隐私标签页重新操作'
      ],
      suggestion: '若问题持续，可能需要更新前后端代码。'
    }
  }

  const handler = errorHandlers[code] || {
    title: '❌ 未知错误',
    message: message,
    icon: '❌',
    solutions: [
      '尝试刷新页面重新开始',
      '检查终端输出的具体错误信息',
      '确保所有服务正常运行'
    ],
    suggestion: '如果问题持续，请收集错误信息并联系技术支持。'
  }

  setError(
    code,
    handler.title,
    handler.message,
    detail,
    handler.solutions,
    handler.suggestion,
    handler.icon
  )
}

// 主请求函数
const runInquiry = async () => {
  if (!eventText.value.trim()) {
    setError(
      'VALIDATION_ERROR',
      '⚠️ 输入不完整',
      '请输入事件描述内容后再提交。',
      '',
      ['在上方文本框中输入科技或外交事件的描述'],
      '输入至少1个字符。'
    )
    return
  }

  loading.value = true
  clearError()
  results.value = []
  receivedCount.value = 0
  totalCount.value = 0

  try {
    const body = { event_text: eventText.value }
    if (selectedMedia.value.length > 0) {
      body.media_ids = selectedMedia.value.slice(0, MEDIA_LIMIT)
    }

    const response = await fetch('http://localhost:8000/simulate/inquiry', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(60000)
    })

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
        setError(code, `HTTP ${response.status}`, msg)
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
    let isError = false

    while (!done) {
      const { value, done: doneReading } = await reader.read()
      done = doneReading

      if (value) {
        buffer += new TextDecoder().decode(value)

        let start = buffer.indexOf('{"media_id"')
        while (start !== -1) {
          let end = buffer.indexOf('}', start)
          if (end === -1) break

          let jsonStr = buffer.slice(start, end + 1)
          try {
            const obj = JSON.parse(jsonStr)
            // 检测是否包含后端异常信息
            if (isErrorResponse(obj.content)) {
              obj.is_participating = false
              obj.has_error = true
            }
            results.value.push(obj)
            receivedCount.value++
          } catch {}

          buffer = buffer.slice(end + 1)
          start = buffer.indexOf('{"media_id"')
        }

        if (buffer.includes('"meta"')) {
          const match = buffer.match(/"meta":\s*\{[^}]*}/)
          if (match) {
            totalCount.value = selectedMedia.value.length > 0 ? selectedMedia.value.length : allMediaList.value.length
          }
        }

        if (buffer.includes('"code":') && (buffer.includes('"message":') || buffer.includes('"error"'))) {
          try {
            const errObj = JSON.parse(buffer)
            handleErrorResponse(500, errObj)
            isError = true
            break
          } catch {}
        }
      }
    }

    if (!isError && results.value.length === 0) {
      setError(
        'PARSE_ERROR',
        '🔨 无结果返回',
        '仿真完成但未收到任何媒体结果，可能是解析错误。',
        '',
        ['尝试刷新页面重新开始', '检查是否选择了足够的媒体']
      )
    }
  } catch (e) {
    if (e.name === 'AbortError') {
      setError(
        'TIMEOUT_ERROR',
        '⏱️ 请求超时',
        '后端响应超过60秒，请检查后端是否正常。',
        e.message,
        ['确保后端服务正在运行', '检查网络连接', '尝试减少选择的媒体数量']
      )
    } else if (e instanceof TypeError && e.message.includes('fetch')) {
      setError(
        'NETWORK_ERROR',
        '🌐 网络连接失败',
        '无法连接到后端服务器，请确保后端已启动。',
        e.message,
        ['启动后端：python -m src.modules.api', '检查 http://localhost:8000 是否可访问']
      )
    } else {
      setError(
        'PARSE_ERROR',
        '⚙️ 处理错误',
        '在处理响应时发生错误。',
        e instanceof Error ? e.message : String(e),
        ['尝试刷新页面', '检查浏览器控制台（F12）获取更多信息']
      )
    }
  } finally {
    loading.value = false
  }
}
</script>
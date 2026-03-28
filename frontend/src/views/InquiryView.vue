<template>
  <div class="p-8 space-y-6">
    <header class="border-b border-slate-700 pb-4">
      <h1 class="text-3xl font-bold text-white tracking-tight">🎙️ 媒体提问场景仿真</h1>
      <p class="text-slate-400 mt-2">基于 GSS 范式，模拟多国媒体针对特定科技事件的反应逻辑。</p>
    </header>

    <div class="bg-slate-800 rounded-xl p-6 shadow-2xl border border-slate-700">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-slate-300 mb-2">事件描述 (Event Input)</label>
          <textarea 
            v-model="eventText"
            class="w-full h-32 bg-slate-900 border border-slate-600 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
            placeholder="请输入需要仿真的科技事件内容..."
          ></textarea>
        </div>
        <div class="flex flex-col justify-end">
          <label class="block text-sm font-medium text-slate-300 mb-2">参与媒体数量</label>
          <input type="number" v-model="mediaCount" class="bg-slate-900 border border-slate-600 rounded-lg p-3 text-white mb-4">
          <button 
            @click="runInquiry"
            :disabled="loading"
            class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-lg transition-all flex items-center justify-center"
          >
            <span v-if="loading" class="animate-spin mr-2">🌀</span>
            {{ loading ? '仿真计算中...' : '开启仿真 (Run Simulation)' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="results.length > 0" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div v-for="(res, index) in results" :key="index" class="bg-slate-800 border-l-4 border-blue-500 rounded-lg p-5 shadow-lg">
        <div class="flex justify-between items-start mb-3">
          <div>
            <span class="px-2 py-1 bg-blue-900 text-blue-200 text-xs rounded uppercase">{{ res.country }}</span>
            <h3 class="text-xl font-bold text-white mt-1">{{ res.media_name }}</h3>
          </div>
          <span class="text-slate-500 text-xs italic">#{{ res.behavior_tag }}</span>
        </div>
        <p class="text-slate-300 leading-relaxed bg-slate-900 p-4 rounded-md italic">
          "{{ res.content }}"
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const eventText = ref('')
const mediaCount = ref(3)
const loading = ref(false)
const results = ref([])

const runInquiry = async () => {
  loading.value = true
  try {
    const response = await fetch('http://localhost:8000/simulate/inquiry', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event_text: eventText.value, media_count: mediaCount.value })
    })
    const json = await response.json()
    results.value = json.data
  } finally {
    loading.value = false
  }
}
</script>
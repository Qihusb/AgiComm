<template>
  <div class="bg-slate-800 border border-slate-700 rounded-2xl p-6 hover:border-blue-500/50 transition-all group shadow-xl">
    <div class="flex justify-between items-start mb-6">
      <div class="flex items-center space-x-4">
        <div class="w-12 h-12 bg-slate-700 rounded-full flex items-center justify-center text-2xl group-hover:bg-blue-600 transition-colors">
          {{ getFlag(agent.country) }}
        </div>
        <div>
          <h3 class="text-lg font-bold text-white leading-tight">{{ agent.media_name }}</h3>
          <p class="text-xs text-slate-500">{{ agent.country }} · {{ agent.ownership }}</p>
        </div>
      </div>
      <div class="px-2 py-1 rounded bg-slate-900 text-[10px] font-mono text-blue-400 border border-blue-400/20">
        {{ agent.behavior_tag }}
      </div>
    </div>

    <div class="relative bg-slate-900/50 rounded-xl p-4 mb-6 border border-slate-700/50">
      <span class="absolute -top-3 left-4 px-2 bg-slate-800 text-[10px] text-slate-500 uppercase">Inquiry Content</span>
      <p class="text-slate-300 text-sm italic leading-relaxed">
        "{{ agent.content }}"
      </p>
    </div>

    <div class="space-y-3">
      <div class="flex justify-between items-center text-[10px] text-slate-500 uppercase font-bold">
        <span>认知偏向 (Cognitive Bias)</span>
        <span class="text-blue-500">{{ agent.dominant_tag || 'General' }}</span>
      </div>
      
      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <div class="flex justify-between text-[10px]">
            <span class="text-slate-400">风险意识</span>
            <span class="text-slate-500">85%</span>
          </div>
          <div class="h-1 bg-slate-700 rounded-full overflow-hidden">
            <div class="h-full bg-red-500/60" style="width: 85%"></div>
          </div>
        </div>
        <div class="space-y-1">
          <div class="flex justify-between text-[10px]">
            <span class="text-slate-400">事实核查</span>
            <span class="text-slate-500">60%</span>
          </div>
          <div class="h-1 bg-slate-700 rounded-full overflow-hidden">
            <div class="h-full bg-blue-500/60" style="width: 60%"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  agent: {
    type: Object,
    required: true
  }
})

// 一个简单的国旗映射函数（示意）
const getFlag = (country) => {
  const flags = { '中国': '🇨🇳', '美国': '🇺🇸', '英国': '🇬🇧', '日本': '🇯🇵', '法国': '🇫🇷' }
  return flags[country] || '🌐'
}
</script>
<template>
  <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-xl transition-all group hover:border-blue-400/50 dark:border-slate-700 dark:bg-slate-800 sm:p-6">
    <div class="mb-6 flex items-start justify-between">
      <div class="flex items-center space-x-4">
        <div class="flex h-12 w-12 items-center justify-center rounded-full bg-slate-200 text-2xl transition-colors group-hover:bg-blue-600 dark:bg-slate-700">
          {{ getFlag(agent.country) }}
        </div>
        <div>
          <h3 class="text-lg font-bold leading-tight text-slate-900 dark:text-white">{{ agent.media_name }}</h3>
          <p class="text-xs text-slate-500">{{ agent.country }} · {{ agent.ownership }}</p>
        </div>
      </div>
      <div class="rounded border border-blue-200 bg-blue-50 px-2 py-1 font-mono text-[10px] text-blue-700 dark:border-blue-400/20 dark:bg-slate-900 dark:text-blue-400">
        {{ agent.behavior_tag }}
      </div>
    </div>

    <div class="relative mb-6 rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700/50 dark:bg-slate-900/50">
      <span class="absolute -top-3 left-4 bg-white px-2 text-[10px] uppercase text-slate-500 dark:bg-slate-800">Inquiry Content</span>
      <p class="text-sm italic leading-relaxed text-slate-700 dark:text-slate-300">
        "{{ agent.content }}"
      </p>
    </div>

    <div class="space-y-3">
      <div class="flex items-center justify-between text-[10px] font-bold uppercase text-slate-500">
        <span>认知偏向 (Cognitive Bias)</span>
        <span class="text-blue-600 dark:text-blue-500">{{ agent.dominant_tag || 'General' }}</span>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <div class="flex justify-between text-[10px]">
            <span class="text-slate-500 dark:text-slate-400">风险意识</span>
            <span class="text-slate-500">85%</span>
          </div>
          <div class="h-1 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
            <div class="h-full bg-red-500/60" style="width: 85%"></div>
          </div>
        </div>
        <div class="space-y-1">
          <div class="flex justify-between text-[10px]">
            <span class="text-slate-500 dark:text-slate-400">事实核查</span>
            <span class="text-slate-500">60%</span>
          </div>
          <div class="h-1 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
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
    required: true,
  },
})

const getFlag = (country) => {
  const flags = { 中国: '🇨🇳', 美国: '🇺🇸', 英国: '🇬🇧', 日本: '🇯🇵', 法国: '🇫🇷' }
  return flags[country] || '🌐'
}
</script>

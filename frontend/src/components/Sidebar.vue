<template>
  <aside class="w-72 bg-slate-900 border-r border-slate-800 flex flex-col h-screen sticky top-0">
    <div class="p-8">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20">
          <span class="text-white font-black text-xl">A</span>
        </div>
        <div>
          <h1 class="text-xl font-bold text-white tracking-tighter">AgiComm</h1>
          <p class="text-[10px] text-slate-500 font-mono">GSS Simulation Platform</p>
        </div>
      </div>
    </div>

    <nav class="flex-1 px-4 py-4 space-y-1">
      <div class="text-[10px] text-slate-600 font-bold uppercase tracking-widest px-4 mb-4">核心仿真模块</div>
      
      <router-link to="/" v-activate 
        class="flex items-center space-x-3 px-4 py-3 rounded-xl transition-all group hover:bg-slate-800">
        <span class="text-xl group-hover:scale-110 transition-transform">🎙️</span>
        <span class="font-medium">媒体提问仿真</span>
      </router-link>

      <router-link to="/news" 
        class="flex items-center space-x-3 px-4 py-3 rounded-xl transition-all group hover:bg-slate-800 opacity-60">
        <span class="text-xl group-hover:scale-110 transition-transform">📰</span>
        <span class="font-medium">多维报道生成</span>
      </router-link>

      <router-link to="/social" 
        class="flex items-center space-x-3 px-4 py-3 rounded-xl transition-all group hover:bg-slate-800 opacity-60">
        <span class="text-xl group-hover:scale-110 transition-transform">🌐</span>
        <span class="font-medium">受众传播仿真</span>
      </router-link>
    </nav>

    <div class="p-6 border-t border-slate-800">
      <div class="bg-slate-800/50 rounded-lg p-4">
        <p class="text-xs text-slate-500">当前仿真事件</p>
        <p class="text-sm text-slate-300 truncate mt-1">未设定...</p>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.router-link-active {
  @apply bg-blue-600/10 text-blue-500 border border-blue-500/20;
}
</style>
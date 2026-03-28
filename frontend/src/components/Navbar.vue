<template>
  <nav class="h-16 border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50 px-8 flex items-center justify-between">
    <div class="flex items-center space-x-4">
      <div class="flex items-center space-x-2 px-3 py-1 bg-green-500/10 border border-green-500/20 rounded-full">
        <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
        <span class="text-xs text-green-500 font-mono">Backend: Connected</span>
      </div>
    </div>

    <div class="flex items-center space-x-6">
      <div class="text-slate-400 text-sm hover:text-white cursor-pointer transition-colors">实验指南</div>
      <div class="text-slate-400 text-sm hover:text-white cursor-pointer transition-colors">GitHub</div>
      <div class="h-8 w-8 rounded-full bg-gradient-to-tr from-blue-600 to-purple-600 border border-slate-700"></div>
    </div>
  </nav>
</template>
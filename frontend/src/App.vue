<template>
  <div class="flex h-screen bg-slate-950 font-sans antialiased text-slate-200">
    <Sidebar />

    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <Navbar />

      <main class="flex-1 overflow-y-auto bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-slate-950">
        <router-view v-slot="{ Component }">
          <transition 
            enter-active-class="transition ease-out duration-200"
            enter-from-class="opacity-0 translate-y-4"
            enter-to-class="opacity-100 translate-y-0"
          >
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import Sidebar from './components/Sidebar.vue'
import Navbar from './components/Navbar.vue'
</script>
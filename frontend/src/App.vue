<template>
  <div
    class="flex h-[100dvh] min-h-0 overflow-hidden bg-slate-100 text-slate-900 dark:bg-slate-950 dark:text-slate-200 font-sans antialiased"
  >
    <div
      v-show="sidebarOpen"
      class="fixed inset-0 z-30 bg-black/50 backdrop-blur-sm md:hidden"
      aria-hidden="true"
      @click="closeSidebar"
    />

    <Sidebar />

    <div class="flex min-w-0 flex-1 flex-col overflow-hidden">
      <Navbar />

      <main
        class="flex-1 min-h-0 overflow-y-auto bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-slate-200 via-slate-100 to-white dark:from-slate-900 dark:via-slate-950 dark:to-slate-950"
      >
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
import { ref, provide, onMounted, onUnmounted } from 'vue'
import Sidebar from './components/Sidebar.vue'
import Navbar from './components/Navbar.vue'

const sidebarOpen = ref(
  typeof window !== 'undefined' && window.matchMedia('(min-width: 768px)').matches,
)

function syncSidebarWithViewport() {
  if (window.matchMedia('(min-width: 768px)').matches) {
    sidebarOpen.value = true
  } else {
    sidebarOpen.value = false
  }
}

function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value
}

function closeSidebar() {
  sidebarOpen.value = false
}

provide('sidebar', {
  open: sidebarOpen,
  toggle: toggleSidebar,
  close: closeSidebar,
})

let mq
onMounted(() => {
  syncSidebarWithViewport()
  mq = window.matchMedia('(min-width: 768px)')
  mq.addEventListener('change', syncSidebarWithViewport)
})

onUnmounted(() => {
  if (mq) mq.removeEventListener('change', syncSidebarWithViewport)
})
</script>

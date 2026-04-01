import { createRouter, createWebHistory } from 'vue-router'
import InquiryView from '../views/InquiryView.vue'
import NewsView from '../views/NewsView.vue'
import SocialView from '../views/SocialView.vue'
import ModelStatusView from '../views/ModelStatusView.vue'

const routes = [
  {
    path: '/',
    name: 'inquiry',
    component: InquiryView
  },
  {
    path: '/news',
    name: 'news',
    component: NewsView
  },
  {
    path: '/social',
    name: 'social',
    component: SocialView
  },
  {
    path: '/model-status',
    name: 'modelStatus',
    component: ModelStatusView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
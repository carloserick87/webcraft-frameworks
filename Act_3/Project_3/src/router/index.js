import { createRouter, createWebHistory } from 'vue-router'

// Imported views

import HeroApp from '@/components/HeroApp.vue'
import AboutUs from '@/views/AboutUs.vue'
import BooksList from '@/views/BooksList.vue'
import Coworking from '@/views/Coworking.vue'
import Planes from '@/views/coworking/planes.vue'
import Reservas from '@/views/coworking/reservas.vue'
import Events from '@/views/coworking/events.vue'
import Contact from '@/views/contactApp.vue'

const routes = [
  { path: '/', name: 'home', component: HeroApp },
  { path: '/aboutUs', name: 'aboutUs', component: AboutUs },
  { path: '/books', name: 'booksList', component: BooksList },
  { path: '/coworking', name: 'coworking', component: Coworking },
  { path: '/coworking/planes', name: 'planes', component: Planes },
  { path: '/coworking/reservas', name: 'reservas', component: Reservas },
  { path: '/coworking/events', name: 'events', component: Events },
  { path: '/contact', name: 'contact', component: Contact },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router

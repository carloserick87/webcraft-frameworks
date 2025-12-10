<!-- NavBar -->

<template>
  <nav class="bg-[#2c414f] text-white shadow-md">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16 items-center">
        <!-- Logo -->
        <div class="flex items-center space-x-3">
          <img src="../assets/nexus_logo.png" alt="Nexus Logo" class="h-10 w-auto" />
          <span class="text-xl font-semibold">{{ NavBar.name }}</span>
        </div>

        <!-- Desktop Menu -->
        <div class="hidden md:flex space-x-6 text-lg ml-auto mr-6 items-center">
          <RouterLink to="/" class="hover:text-orange-300">{{ NavBar.home }}</RouterLink>
          <RouterLink to="/books" class="hover:text-orange-300">{{ NavBar.books }}</RouterLink>
          <RouterLink to="/aboutUs" class="hover:text-orange-300">{{ NavBar.aboutUs }}</RouterLink>
          <RouterLink to="/coworking" class="hover:text-orange-300">{{ NavBar.coworking }}</RouterLink>
          <RouterLink to="/cafeteria" class="hover:text-orange-300">{{ NavBar.cafeteria }}</RouterLink>
          <RouterLink to="/contact" class="hover:text-orange-300">{{ NavBar.contact }}</RouterLink>
          
          <!-- Tienda Online Dropdown -->
          <div class="relative" @mouseenter="showShopDropdown = true" @mouseleave="showShopDropdown = false">
            <button class="flex items-center gap-1 hover:text-orange-300">
              <ShoppingCartIcon class="h-6 w-6"/>
              <span>Tienda</span>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            
            <div
              v-if="showShopDropdown"
              class="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-xl border border-gray-200 z-20"
            >
              <div class="py-2">
                <router-link
                  v-for="item in shopStore.menuItems"
                  :key="item.id"
                  :to="item.route"
                  class="flex items-center gap-3 px-4 py-3 hover:bg-orange-50 transition-colors text-gray-700"
                >
                  <span class="text-xl">{{ item.icon }}</span>
                  <span class="font-medium">{{ item.name }}</span>
                </router-link>
              </div>
              <div class="border-t border-gray-200 px-4 py-2 bg-gray-50">
                <div class="flex items-center justify-between text-sm">
                  <span class="text-gray-600">Carrito:</span>
                  <span class="font-semibold text-orange-500">{{ shopStore.cartItemsCount }} items</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Login button (desktop) -->
        <div class="hidden md:flex items-center gap-4">
          <div v-if="authStore.isAuthenticated" class="flex items-center gap-2">
            <img 
              v-if="authStore.userPhoto" 
              :src="authStore.userPhoto" 
              :alt="authStore.userName"
              class="w-8 h-8 rounded-full"
            >
            <span class="text-sm">{{ authStore.userName }}</span>
          </div>
          <RouterLink 
            v-if="!authStore.isAuthenticated"
            to="/login" 
            class="bg-orange-400 text-black px-4 py-2 rounded-lg font-medium hover:bg-orange-300 transition"
          >
            {{ NavBar.login }}
          </RouterLink>
          <button
            v-else
            @click="handleLogout"
            class="bg-red-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-red-600 transition"
          >
            Cerrar Sesión
          </button>
        </div>

        <!-- Hamburger button (mobile) -->
        <button @click="isOpen = !isOpen" class="md:hidden text-white focus:outline-none text-3xl">
          {{ NavBar.icon }}
        </button>
      </div>
    </div>

    <!-- Mobile menu -->
    <div v-if="isOpen" class="md:hidden bg-[#2c414f] px-4 pb-4 space-y-3 text-lg">
      <RouterLink to="/" class="block hover:text-orange-300">{{ NavBar.home }}</RouterLink>
      <RouterLink to="/books" class="block hover:text-orange-300">{{ NavBar.books }}</RouterLink>
      <RouterLink to="/aboutUs" class="block hover:text-orange-300">{{ NavBar.aboutUs }}</RouterLink>
      <RouterLink to="/coworking" class="block hover:text-orange-300">{{ NavBar.coworking }}</RouterLink>
      <RouterLink to="/cafeteria" class="block hover:text-orange-300">{{ NavBar.cafeteria }}</RouterLink>
      <RouterLink to="/contact" class="block hover:text-orange-300">{{ NavBar.contact }}</RouterLink>
      
      <!-- Mobile Tienda Online -->
      <div>
        <button
          @click="showMobileShop = !showMobileShop"
          class="flex items-center gap-2 hover:text-orange-300 w-full"
        >
          <ShoppingCartIcon class="h-6 w-6"/>
          <span>Tienda Online</span>
          <svg
            class="w-4 h-4 ml-auto transition-transform"
            :class="{ 'rotate-180': showMobileShop }"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        <div v-if="showMobileShop" class="ml-6 mt-2 space-y-2">
          <router-link
            v-for="item in shopStore.menuItems"
            :key="item.id"
            :to="item.route"
            class="flex items-center gap-2 block hover:text-orange-300"
            @click="isOpen = false"
          >
            <span>{{ item.icon }}</span>
            <span>{{ item.name }}</span>
          </router-link>
        </div>
      </div>

      <div v-if="authStore.isAuthenticated" class="flex items-center gap-2 mb-2">
        <img 
          v-if="authStore.userPhoto" 
          :src="authStore.userPhoto" 
          :alt="authStore.userName"
          class="w-8 h-8 rounded-full"
        >
        <span class="text-sm">{{ authStore.userName }}</span>
      </div>
      <RouterLink 
        v-if="!authStore.isAuthenticated"
        to="/login" 
        class="block bg-orange-400 text-black px-4 py-2 text-center rounded-lg font-medium hover:bg-orange-300 transition"
      >
        {{ NavBar.login }}
      </RouterLink>
      <button
        v-else
        @click="handleLogout"
        class="w-full bg-red-500 text-white px-4 py-2 text-center rounded-lg font-medium hover:bg-red-600 transition"
      >
        Cerrar Sesión
      </button>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ShoppingCartIcon } from '@heroicons/vue/24/outline'
import { useShopStore } from '@/stores/shop'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const shopStore = useShopStore()

const NavBar = {
  name:'Nexus',
  home:'Inicio',
  books:'Libros',
  aboutUs:'Sobre nosotros',
  coworking:'Coworking',
  cafeteria:'Cafeteria',
  contact:'Contacto',
  icon:'☰',
  login:'Iniciar Sesión'
};

const isOpen = ref(false)
const showShopDropdown = ref(false)
const showMobileShop = ref(false)

onMounted(() => {
  authStore.checkAuth()
})

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}
</script>

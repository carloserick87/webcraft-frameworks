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
        <div class="hidden md:flex space-x-6 text-lg ml-auto mr-6">
          <RouterLink to="/" class="hover:text-orange-300">{{ NavBar.home }}</RouterLink>
          <RouterLink to="/books" class="hover:text-orange-300">{{ NavBar.books }}</RouterLink>
          <RouterLink to="/aboutUs" class="hover:text-orange-300">{{ NavBar.aboutUs }}</RouterLink>

          <!-- SUBMENU DESKTOP -->
          <div class="relative group">
            <RouterLink to="/coworking" class="hover:text-orange-300">
              {{ NavBar.coworking }}
            </RouterLink>

            <!-- Submenu -->
            <div
              class="absolute hidden group-hover:block bg-[#2c414f] text-white mt-2 py-2 w-40 rounded-lg shadow-lg"
            >
              <RouterLink
                to="/coworking/planes"
                class="block px-4 py-2 hover:bg-orange-300 hover:text-black"
              >
                Planes
              </RouterLink>

              <RouterLink
                to="/coworking/reservas"
                class="block px-4 py-2 hover:bg-orange-300 hover:text-black"
              >
                Reservas
              </RouterLink>

              <RouterLink
                to="/coworking/events"
                class="block px-4 py-2 hover:bg-orange-300 hover:text-black"
              >
                Eventos
              </RouterLink>
            </div>
          </div>

          <RouterLink to="/cafeteria" class="hover:text-orange-300">{{
            NavBar.cafeteria
          }}</RouterLink>
          <RouterLink to="/contact" class="hover:text-orange-300">{{ NavBar.contact }}</RouterLink>
          <RouterLink to="/shop" class="hover:text-orange-300">
            <ShoppingCartIcon class="h-6 w-6" />
          </RouterLink>
        </div>

        <!-- Login button (desktop) -->
        <div class="hidden md:flex">
          <RouterLink
            to="/login"
            class="bg-orange-400 text-white px-4 py-2 rounded-lg font-medium hover:bg-orange-300 transition"
          >
            {{ NavBar.login }}
          </RouterLink>
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
      <RouterLink to="/aboutUs" class="block hover:text-orange-300">{{
        NavBar.aboutUs
      }}</RouterLink>

      <!-- SUBMENU MOBILE -->
      <div class="border-t border-gray-500 pt-2">
        <button
          @click="coworkingOpen = !coworkingOpen"
          class="w-full text-left hover:text-orange-300 flex justify-between items-center"
        >
          {{ NavBar.coworking }}
          <span>{{ coworkingOpen ? '▲' : '▼' }}</span>
        </button>

        <div v-if="coworkingOpen" class="ml-4 mt-2 space-y-2">
          <RouterLink to="/coworking/planes" class="block hover:text-orange-300">
            Planes
          </RouterLink>

          <RouterLink to="/coworking/reservas" class="block hover:text-orange-300">
            Reservas
          </RouterLink>

          <RouterLink to="/coworking/eventos" class="block hover:text-orange-300">
            Eventos
          </RouterLink>
        </div>
      </div>

      <RouterLink to="/cafeteria" class="block hover:text-orange-300">{{
        NavBar.cafeteria
      }}</RouterLink>
      <RouterLink to="/contact" class="block hover:text-orange-300">{{
        NavBar.contact
      }}</RouterLink>
      <RouterLink to="/shop" class="block hover:text-orange-300">
        <ShoppingCartIcon class="h-6 w-6" />
      </RouterLink>

      <!-- Login -->
      <RouterLink
        to="/login"
        class="block bg-orange-400 text-black px-4 py-2 text-center rounded-lg font-medium hover:bg-orange-300 transition"
      >
        {{ NavBar.login }}
      </RouterLink>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { ShoppingCartIcon } from '@heroicons/vue/24/outline'

const NavBar = {
  name: 'Nexus',
  home: 'Inicio',
  books: 'Libros',
  aboutUs: 'Sobre nosotros',
  coworking: 'Coworking',
  cafeteria: 'Cafeteria',
  contact: 'Contacto',
  icon: '☰',
  login: 'Iniciar Sesión',
}

const isOpen = ref(false) // Menú móvil
const coworkingOpen = ref(false) // Submenú móvil
</script>

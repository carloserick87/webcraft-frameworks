<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <h1 class="text-3xl font-bold mb-6">Espacios de Coworking</h1>

      <!-- Tienda Online Submenu -->
      <div class="bg-white border rounded p-4 mb-6">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold">Tienda Online</h2>
          <button
            @click="showShopMenu = !showShopMenu"
            class="bg-orange-400 text-black px-4 py-2 rounded hover:bg-orange-300"
          >
            {{ showShopMenu ? 'Ocultar' : 'Ver opciones' }}
          </button>
        </div>

        <!-- Menu simple -->
        <div v-if="showShopMenu" class="mt-4 space-y-2">
          <router-link
            v-for="item in shopStore.menuItems"
            :key="item.id"
            :to="item.route"
            @click="showShopMenu = false"
            class="block p-2 hover:bg-gray-100 rounded"
          >
            {{ item.icon }} {{ item.name }}
          </router-link>
        </div>
      </div>

      <!-- Mensaje de confirmación -->
      <div 
        v-if="showMessage"
        class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4"
      >
        {{ messageText }}
      </div>

      <!-- Espacios -->
      <div class="space-y-4">
        <div
          v-for="space in coworkingSpaces"
          :key="space.id"
          class="bg-white border rounded p-4"
        >
          <div class="flex justify-between items-start">
            <div>
              <h3 class="font-semibold text-lg">{{ space.icon }} {{ space.name }}</h3>
              <p class="text-gray-600 text-sm mt-1">{{ space.description }}</p>
              <p class="text-gray-500 text-xs mt-2">Capacidad: {{ space.capacity }} personas</p>
            </div>
            <div class="text-right">
              <p class="font-bold text-orange-500">€{{ space.price }}/hora</p>
              <button 
                @click="reserveSpace(space)"
                class="mt-2 bg-orange-400 text-black px-3 py-1 rounded text-sm hover:bg-orange-300"
              >
                Reservar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useShopStore } from '@/stores/shop'
import { useAuthStore } from '@/stores/auth'

defineOptions({
  name: 'CoworkingView'
})

const shopStore = useShopStore()
const authStore = useAuthStore()
const showShopMenu = ref(false)
const showMessage = ref(false)
const messageText = ref('')

const coworkingSpaces = [
  { id: 1, name: 'Espacio Individual', description: 'Ideal para trabajo concentrado', capacity: 1, price: 15, icon: '💼' },
  { id: 2, name: 'Sala de Reuniones', description: 'Perfecta para equipos pequeños', capacity: 6, price: 40, icon: '🤝' },
  { id: 3, name: 'Espacio Colaborativo', description: 'Ambiente dinámico', capacity: 12, price: 25, icon: '👥' },
  { id: 4, name: 'Oficina Privada', description: 'Máxima privacidad', capacity: 4, price: 60, icon: '🏢' }
]

onMounted(() => {
  authStore.checkAuth()
})

const reserveSpace = (space) => {
  shopStore.addReservation(space)
  
  // Mostrar nombre del usuario si está autenticado
  if (authStore.isAuthenticated && authStore.userName) {
    messageText.value = `✅ Reserva realizada para ${authStore.userName}: ${space.icon} ${space.name} - €${space.price}/hora`
  } else {
    messageText.value = `✅ Reserva realizada: ${space.icon} ${space.name} - €${space.price}/hora`
  }
  
  showMessage.value = true
  
  setTimeout(() => {
    showMessage.value = false
  }, 3000)
}
</script>



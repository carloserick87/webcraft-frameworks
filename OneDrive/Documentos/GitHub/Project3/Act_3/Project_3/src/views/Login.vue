<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
    <div class="max-w-md w-full bg-white rounded-lg shadow-md p-8">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Iniciar Sesión</h1>
        <p class="text-gray-600">Accede a tu cuenta de Nexus</p>
      </div>

      <!-- Mensaje de éxito/error -->
      <div 
        v-if="message"
        :class="messageType === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
        class="px-4 py-3 rounded mb-4"
      >
        {{ message }}
      </div>

      <!-- Botón de Google -->
      <button
        @click="signInWithGoogle"
        :disabled="loading"
        class="w-full flex items-center justify-center gap-3 bg-white border-2 border-gray-300 rounded-lg px-6 py-3 font-medium text-gray-700 hover:bg-gray-50 hover:border-gray-400 transition disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <svg v-if="!loading" class="w-5 h-5" viewBox="0 0 24 24">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
        </svg>
        <span v-if="loading" class="animate-spin">⏳</span>
        <span v-else>Continuar con Google</span>
      </button>

      <div class="mt-6 text-center">
        <p class="text-sm text-gray-500">
          Al iniciar sesión, aceptas nuestros términos y condiciones
        </p>
      </div>

      <!-- Usuario logueado -->
      <div v-if="authStore.isAuthenticated" class="mt-8 pt-8 border-t">
        <div class="flex items-center gap-4 mb-4">
          <img 
            v-if="authStore.userPhoto" 
            :src="authStore.userPhoto" 
            :alt="authStore.userName"
            class="w-12 h-12 rounded-full"
          >
          <div>
            <p class="font-semibold">{{ authStore.userName }}</p>
            <p class="text-sm text-gray-600">{{ authStore.userEmail }}</p>
          </div>
        </div>
        <button
          @click="handleLogout"
          class="w-full bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition"
        >
          Cerrar Sesión
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const message = ref('')
const messageType = ref('')

// Verificar si ya está autenticado
onMounted(() => {
  authStore.checkAuth()
})

const signInWithGoogle = () => {
  loading.value = true
  message.value = ''

  // Simulación de autenticación con Google (para principiantes)
  // En producción, usarías Firebase Auth o Google OAuth real
  setTimeout(() => {
    // Datos simulados de usuario de Google
    const mockUser = {
      name: 'Usuario de Prueba',
      email: 'usuario@gmail.com',
      photo: 'https://ui-avatars.com/api/?name=Usuario&background=orange&color=fff&size=128'
    }

    // Aquí iría la autenticación real con Google
    // Por ahora simulamos el proceso
    handleGoogleAuth(mockUser)
  }, 1500)
}

const handleGoogleAuth = (userData) => {
  // En una app real, aquí recibirías los datos de Google OAuth
  authStore.login(userData)
  loading.value = false
  message.value = '✅ ¡Inicio de sesión exitoso!'
  messageType.value = 'success'
  
  // Redirigir después de 1 segundo
  setTimeout(() => {
    router.push('/')
  }, 1000)
}

const handleLogout = () => {
  authStore.logout()
  message.value = 'Sesión cerrada correctamente'
  messageType.value = 'success'
  setTimeout(() => {
    message.value = ''
  }, 2000)
}

// Función para usar Google OAuth real (comentada para principiantes)
/*
const signInWithGoogleReal = async () => {
  try {
    loading.value = true
    
    // Aquí usarías Firebase Auth o Google OAuth
    // Ejemplo con Firebase:
    // const provider = new GoogleAuthProvider()
    // const result = await signInWithPopup(auth, provider)
    // const user = result.user
    
    // authStore.login({
    //   name: user.displayName,
    //   email: user.email,
    //   photo: user.photoURL
    // })
    
  } catch (error) {
    message.value = 'Error al iniciar sesión: ' + error.message
    messageType.value = 'error'
  } finally {
    loading.value = false
  }
}
*/
</script>





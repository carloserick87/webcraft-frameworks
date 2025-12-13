<template>
  <section class="max-w-5xl mx-auto p-6">
    <div class="bg-white rounded-2xl shadow-lg p-8">
      <!-- Header -->
      <div class="mb-8 text-center">
        <h1 class="text-3xl font-bold text-gray-800">Reservas Coworking Nexus</h1>
        <p class="text-gray-500 mt-2">
          Reserva tu espacio de trabajo en nuestra librería–coworking
        </p>
      </div>

      <!-- Form -->
      <form class="grid grid-cols-1 md:grid-cols-2 gap-6" @submit.prevent="submitReservation">
        <!-- Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Nombre completo</label>
          <div class="relative">
            <UserIcon class="h-5 w-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              v-model="form.name"
              type="text"
              required
              class="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-[#2c414f] focus:outline-none"
              placeholder="Tu nombre"
            />
          </div>
        </div>

        <!-- Email -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <div class="relative">
            <EnvelopeIcon class="h-5 w-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              v-model="form.email"
              type="email"
              required
              class="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-[#2c414f] focus:outline-none"
              placeholder="correo@nexus.com"
            />
          </div>
        </div>

        <!-- Date -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Fecha</label>
          <div class="relative">
            <CalendarDaysIcon
              class="h-5 w-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2"
            />
            <input
              v-model="form.date"
              type="date"
              required
              class="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-[#2c414f] focus:outline-none"
            />
          </div>
        </div>

        <!-- Time -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Horario</label>
          <select
            v-model="form.time"
            required
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-[#2c414f] focus:outline-none"
          >
            <option disabled value="">Selecciona un horario</option>
            <option>Mañana (9:00 - 13:00)</option>
            <option>Tarde (14:00 - 18:00)</option>
            <option>Jornada completa</option>
          </select>
        </div>

        <!-- Plan -->
        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Plan</label>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <button
              v-for="plan in plans"
              :key="plan"
              type="button"
              @click="form.plan = plan"
              :class="[
                'border rounded-xl p-4 text-center transition',
                form.plan === plan
                  ? 'border-[#2c414f] bg-[#2c414f] text-white'
                  : 'border-gray-300 hover:border-[#2c414f]',
              ]"
            >
              <BuildingOffice2Icon class="h-6 w-6 mx-auto mb-2" />
              <span class="font-medium">{{ plan }}</span>
            </button>
          </div>
        </div>

        <!-- Submit -->
        <div class="md:col-span-2 text-center mt-6">
          <button
            type="submit"
            class="bg-orange-300 text-white px-8 py-3 rounded-xl font-semibold hover:bg-opacity-90 transition"
          >
            Reservar ahora
          </button>
        </div>
      </form>

      <!-- Success message -->
      <div v-if="success" class="mt-6 text-center text-green-600 font-medium">
        Reserva enviada correctamente. ¡Te esperamos en Nexus!
      </div>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref } from 'vue'
import {
  UserIcon,
  EnvelopeIcon,
  CalendarDaysIcon,
  BuildingOffice2Icon,
} from '@heroicons/vue/24/outline'

const success = ref(false)

const form = reactive({
  name: '',
  email: '',
  date: '',
  time: '',
  plan: '',
})

const plans = ['Día', 'Semana', 'Mes']

const submitReservation = () => {
  console.log('Reserva:', form)
  success.value = true

  // reset simple
  Object.keys(form).forEach((key) => (form[key] = ''))
}
</script>

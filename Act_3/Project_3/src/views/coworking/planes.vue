<!-- Plans-->

<template>
  <section class="bg-gray-100 min-h-screen py-14 px-4 sm:px-6 lg:px-10">
    <div class="max-w-6xl mx-auto">

      <!-- Título -->
      <h1 class="text-3xl sm:text-4xl font-bold text-[#2c414f] mb-8">
        Planes de Coworking
      </h1>

      <!-- Grid de planes -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">

        <!-- Card de plan -->
        <div
          v-for="plan in plans"
          :key="plan.id"
          @click="selectPlan(plan)"
          class="cursor-pointer bg-white border rounded-2xl p-6 shadow-md hover:shadow-xl transition border-gray-200 relative"
          :class="selectedPlan?.id === plan.id ? 'border-orange-400 shadow-lg' : 'border-gray-200'"
        >
          <!-- Etiqueta seleccionado -->
          <span
            v-if="selectedPlan?.id === plan.id"
            class="absolute top-4 right-4 bg-orange-400 text-black text-sm font-semibold px-2 py-1 rounded-md"
          >
            Seleccionado
          </span>

          <h2 class="text-2xl font-semibold text-gray-800 mb-3">{{ plan.name }}</h2>

          <p class="text-gray-600 mb-6">{{ plan.description }}</p>

          <p class="text-3xl font-bold text-[#2c414f] mb-4">
            €{{ plan.price }}
          </p>

          <button
            class="w-full bg-orange-400 hover:bg-orange-300 text-black font-semibold py-2 rounded-lg transition"
          >
            Seleccionar
          </button>
        </div>
      </div>

      <!-- Resultado -->
      <div v-if="selectedPlan" class="mt-12 bg-white p-6 rounded-2xl shadow-md border border-gray-200 max-w-xl mx-auto text-center">
        <h3 class="text-2xl font-bold text-[#2c414f] mb-4">Has seleccionado:</h3>

        <p class="text-xl font-semibold text-gray-800 mb-1">
          {{ selectedPlan.name }}
        </p>

        <p class="text-lg text-gray-600 mb-4">
          Precio: <span class="font-bold text-orange-500">€{{ selectedPlan.price }}</span>
        </p>

        <RouterLink
          to="/coworking/reservas"
          class="inline-block bg-orange-400 hover:bg-orange-300 text-black px-6 py-2 rounded-lg font-semibold transition"
        >
          Continuar con la reserva
        </RouterLink>
      </div>

    </div>
  </section>
</template>

<script setup>
import { ref } from "vue";

const plans = [
  {
    id: 1,
    name: "Plan Diario",
    price: 12,
    description: "Acceso por un día completo al espacio de coworking."
  },
  {
    id: 2,
    name: "Plan Semanal",
    price: 49,
    description: "Acceso ilimitado durante una semana."
  },
  {
    id: 3,
    name: "Plan Mensual",
    price: 150,
    description: "Acceso mensual completo con beneficios adicionales."
  }
];

const selectedPlan = ref(null);

function selectPlan(plan) {
  selectedPlan.value = plan;
}
</script>

<template>
  <section class="bg-gray-100">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10 py-12 sm:py-16">

      <!-- Hero principal -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-10 lg:gap-16 items-center">

        <!-- Text -->
        <div>
          <h1 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-[#2c414f] leading-tight mb-4 sm:mb-6">
            Bienvenido a nuestro espacio de
            <span class="text-orange-300">Coworking</span>
          </h1>

          <p class="text-base sm:text-lg text-gray-700 mb-4 sm:mb-6">
            Un lugar diseñado para ti: estudiantes, emprendedores, programadores,
            creativos y profesionales que buscan un entorno tranquilo, flexible y
            con todas las comodidades para trabajar o estudiar.
          </p>

          <p class="text-base sm:text-lg text-gray-700 mb-8 sm:mb-10">
            Conoce nuestros planes, reserva tu espacio ideal y participa en eventos
            pensados para impulsar tu crecimiento profesional.
          </p>

          <!-- Botones -->
          <div class="flex flex-col sm:flex-row flex-wrap gap-4">
            <RouterLink to="/coworking/planes" class="bg-orange-400 hover:bg-orange-300 text-white font-semibold px-6 py-3 rounded-lg shadow-md text-center transition">
              Ver planes
            </RouterLink>

            <RouterLink to="/coworking/reservas" class="bg-white border border-gray-300 hover:bg-gray-100 text-gray-800 font-semibold px-6 py-3 rounded-lg shadow-md text-center transition">
              Hacer una reserva
            </RouterLink>
          </div>
        </div>

        <!-- Imagen -->
        <div class="flex justify-center">
          <img
            src="../assets/ChatGPT Image Dec 12, 2025, 07_29_48 PM.png"
            alt="Coworking space"
            class="rounded-2xl shadow-xl object-cover w-full h-[240px] sm:h-[320px] lg:h-[380px]"
          />
        </div>

      </div>

      <!-- Beneficios -->
      <div class="mt-16 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 sm:gap-10">

        <!-- Beneficio 1 -->
        <div class="bg-white rounded-xl shadow-md p-6 border border-gray-200">
          <div class="w-14 h-14 bg-orange-100 text-orange-500 flex items-center justify-center rounded-xl mb-4">
            <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
              <path d="M17 8h2a2 2 0 012 2v9a2 2 0 01-2 2h-2M7 8H5a2 2 0 00-2 2v9a2 2 0 002 2h2m4-21v16m0 0l-4-4m4 4l4-4" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3 class="text-lg sm:text-xl font-semibold mb-2">Espacios flexibles</h3>
          <p class="text-gray-600 text-sm sm:text-base">
            Áreas diseñadas para trabajar, estudiar o reunirte con comodidad.
          </p>
        </div>

        <!-- Beneficio 2 -->
        <div class="bg-white rounded-xl shadow-md p-6 border border-gray-200">
          <div class="w-14 h-14 bg-orange-100 text-orange-500 flex items-center justify-center rounded-xl mb-4">
            <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
              <path d="M12 6v6l4 2M8 3h8l6 6v8a2 2 0 01-2 2H4a2 2 0 01-2-2V9l6-6z" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3 class="text-lg sm:text-xl font-semibold mb-2">Entorno seguro</h3>
          <p class="text-gray-600 text-sm sm:text-base">
            Un lugar limpio, tranquilo y perfecto para enfocarte.
          </p>
        </div>

        <!-- Beneficio 3 -->
        <div class="bg-white rounded-xl shadow-md p-6 border border-gray-200">
          <div class="w-14 h-14 bg-orange-100 text-orange-500 flex items-center justify-center rounded-xl mb-4">
            <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
              <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zm-6 7h4a6 6 0 016 6H4a6 6 0 016-6z" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3 class="text-lg sm:text-xl font-semibold mb-2">Comunidad</h3>
          <p class="text-gray-600 text-sm sm:text-base">
            Conecta con otros profesionales y crea nuevas oportunidades.
          </p>
        </div>

      </div>

    </div>
  </section>
</template>

<script setup>
// Componente solo visual
</script>

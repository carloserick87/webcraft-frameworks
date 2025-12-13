<template>
  <section class="max-w-6xl mx-auto p-4 sm:p-6">
    <!-- Header -->
    <div class="text-center mb-10">
      <h1 class="text-3xl sm:text-4xl font-bold text-gray-800">Eventos en Nexus</h1>
      <p class="text-gray-500 mt-2">Charlas, presentaciones de libros y eventos culturales</p>
    </div>

    <!-- Events grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="event in events"
        :key="event.id"
        class="bg-white rounded-2xl shadow-lg overflow-hidden flex flex-col"
      >
        <!-- Image -->
        <img :src="event.image" :alt="event.title" class="h-48 w-full object-cover" />

        <!-- Content -->
        <div class="p-6 flex flex-col flex-1">
          <h2 class="text-xl font-semibold text-gray-800 mb-2">
            {{ event.title }}
          </h2>

          <p class="text-gray-600 text-sm flex-1">
            {{ event.description }}
          </p>

          <!-- Info -->
          <div class="mt-4 space-y-2 text-sm text-gray-500">
            <div class="flex items-center gap-2">
              <CalendarDaysIcon class="h-5 w-5" />
              <span>{{ event.date }}</span>
            </div>
            <div class="flex items-center gap-2">
              <ClockIcon class="h-5 w-5" />
              <span>{{ event.time }}</span>
            </div>
            <div class="flex items-center gap-2">
              <MapPinIcon class="h-5 w-5" />
              <span>{{ event.location }}</span>
            </div>
          </div>

          <!-- Action -->
          <button
            class="mt-6 w-full bg-[#2c414f] text-white py-2.5 rounded-xl font-medium hover:bg-opacity-90 transition"
          >
            Reservar lugar
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { CalendarDaysIcon, ClockIcon, MapPinIcon } from '@heroicons/vue/24/outline'

const events = [
  {
    id: 1,
    title: 'Presentación de libro: Literatura Moderna',
    description: 'Una charla con el autor y firma de libros en un ambiente acogedor.',
    date: '20 Enero 2026',
    time: '18:00 - 20:00',
    location: 'Sala principal Nexus',
    image: 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f',
  },
  {
    id: 2,
    title: 'Workshop: Escritura Creativa',
    description: 'Aprende técnicas de escritura con profesionales del sector.',
    date: '25 Enero 2026',
    time: '10:00 - 13:00',
    location: 'Coworking Nexus',
    image: 'https://images.unsplash.com/photo-1455390582262-044cdead277a',
  },
  {
    id: 3,
    title: 'Club de Lectura Mensual',
    description: 'Comparte ideas y opiniones sobre el libro del mes.',
    date: '30 Enero 2026',
    time: '19:00 - 21:00',
    location: 'Zona Café Nexus',
    image: 'https://images.unsplash.com/photo-1519682337058-a94d519337bc',
  },
]
</script>

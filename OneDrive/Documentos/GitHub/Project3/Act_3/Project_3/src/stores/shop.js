import { defineStore } from 'pinia'

export const useShopStore = defineStore('shop', {
  state: () => ({
    cart: [],
    reservations: [],
    menuItems: [
      { id: 1, name: 'Libros', icon: '📚', route: '/books' },
      { id: 2, name: 'Cafetería', icon: '☕', route: '/cafeteria' },
      { id: 3, name: 'Merchandising', icon: '🛍️', route: '/shop/merchandising' },
      { id: 4, name: 'E-books', icon: '📱', route: '/shop/ebooks' },
      { id: 5, name: 'Suscripciones', icon: '⭐', route: '/shop/subscriptions' }
    ]
  }),
  
  getters: {
    cartItemsCount: (state) => state.cart.length,
    totalPrice: (state) => state.cart.reduce((total, item) => total + item.price, 0),
    reservationsCount: (state) => state.reservations.length
  },
  
  actions: {
    addToCart(item) {
      this.cart.push(item)
    },
    removeFromCart(itemId) {
      this.cart = this.cart.filter(item => item.id !== itemId)
    },
    clearCart() {
      this.cart = []
    },
    addReservation(space) {
      const reservation = {
        id: Date.now(),
        space: space.name,
        price: space.price,
        date: new Date().toLocaleDateString('es-ES'),
        status: 'Pendiente'
      }
      this.reservations.push(reservation)
      return reservation
    }
  }
})



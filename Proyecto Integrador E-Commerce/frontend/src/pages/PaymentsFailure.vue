<template>
  <div class="payments-failure page">
    <h1>Pago no completado</h1>
    <p v-if="carritoId">Carrito: <strong>{{ carritoId }}</strong></p>
    <p v-if="collectionId">ID de pago: <strong>{{ collectionId }}</strong></p>
    <p v-if="collectionStatus">Estado: <strong>{{ collectionStatus }}</strong></p>

    <p>El pago no fue completado. Tu carrito debería mantenerse intacto. Puedes intentar pagar de nuevo o revisar tu carrito.</p>

    <div class="actions">
      <router-link to="/cart" class="btn">Volver al carrito</router-link>
      <router-link to="/" class="btn">Volver al inicio</router-link>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
const carritoId = route.params.carritoId || route.params.id
const collectionId = route.query.payment_id || route.query.collection_id
const collectionStatus = route.query.collection_status || route.query.status
</script>

<style scoped>
.payments-failure { padding: 2rem; max-width: 760px; margin: 0 auto; }
.payments-failure h1 { color: #c62828; }
.actions { margin-top: 1.2rem; display:flex; gap: .5rem }
.btn { padding: .5rem 1rem; background:#1976d2; color:white; border-radius:4px; text-decoration:none }
</style>

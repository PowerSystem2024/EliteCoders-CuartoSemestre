<template>
  <div class="payments-success page">
    <h1>Pago confirmado</h1>
    <p v-if="carritoId">Carrito: <strong>{{ carritoId }}</strong></p>
    <p v-if="collectionId">ID de pago: <strong>{{ collectionId }}</strong></p>
    <p v-if="collectionStatus">Estado: <strong>{{ collectionStatus }}</strong></p>

    <p>Tu compra fue procesada correctamente. Si ya estás registrado en el curso, deberías poder acceder a las lecciones desde "Mis cursos".</p>

    <div class="actions">
      <router-link to="/" class="btn">Volver al inicio</router-link>
      <router-link to="/mis-cursos" class="btn">Ir a Mis cursos</router-link>
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
.payments-success { padding: 2rem; max-width: 760px; margin: 0 auto; }
.payments-success h1 { color: #2b8a3e; }
.actions { margin-top: 1.2rem; display:flex; gap: .5rem }
.btn { padding: .5rem 1rem; background:#1976d2; color:white; border-radius:4px; text-decoration:none }
</style>

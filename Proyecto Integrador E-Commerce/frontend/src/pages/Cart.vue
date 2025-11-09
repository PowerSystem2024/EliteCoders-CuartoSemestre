<template>
  <section class="container">
    <h1 class="h1">Carrito de compras</h1>

    <!-- Loading state -->
    <div v-if="loading" class="center">Cargando...</div>

    <!-- Empty cart -->
    <div v-else-if="!carrito || carrito.items.length === 0" class="center">
      <div class="card" style="max-width:400px">
        <div class="card-content">
          <h2 class="h2">Tu carrito está vacío</h2>
          <p style="color:var(--muted)">Agrega algunos cursos para comenzar.</p>
        </div>
        <div class="card-footer">
          <RouterLink to="/courses" class="btn block">Ver cursos</RouterLink>
        </div>
      </div>
    </div>

    <!-- Cart with items -->
    <div v-else class="sidebar-grid">
      <!-- Cart items -->
      <div>
        <div class="grid" style="gap:0.8rem">
          <article class="card" v-for="item in carrito.items" :key="item.id">
            <div class="card-content">
              <h3 class="h2">{{ item.curso_titulo }}</h3>
              <div style="display:flex;gap:.5rem;align-items:center;margin:.3rem 0">
                <span class="tag">Cantidad: {{ item.cantidad }}</span>
                <span class="tag">${{ item.curso_precio }}</span>
              </div>
            </div>
            <div class="card-footer">
              <div class="hr"></div>
              <div style="display:flex;justify-content:space-between;align-items:center">
                <strong>Subtotal: ${{ item.subtotal }}</strong>
                <button 
                  class="btn secondary" 
                  @click="quitarItem(item.curso)"
                  :disabled="removingItem === item.curso"
                >
                  {{ removingItem === item.curso ? 'Quitando...' : 'Quitar' }}
                </button>
              </div>
            </div>
          </article>
        </div>
      </div>

      <!-- Cart summary -->
      <aside class="card">
        <div class="card-content">
          <h2 class="h2">Resumen del pedido</h2>
          <div style="margin:1rem 0">
            <div style="display:flex;justify-content:space-between;margin:0.5rem 0">
              <span>{{ carrito.items.length }} curso{{ carrito.items.length !== 1 ? 's' : '' }}</span>
              <span>${{ carrito.total }}</span>
            </div>
          </div>
          <div class="hr"></div>
          <div style="display:flex;justify-content:space-between;margin:1rem 0;font-weight:bold">
            <span>Total:</span>
            <span>${{ carrito.total }}</span>
          </div>
        </div>
        <div class="card-footer">
          <button 
            class="btn block" 
            @click="checkout"
            :disabled="processingCheckout"
            style="margin-bottom:0.5rem"
          >
            {{ processingCheckout ? 'Procesando...' : 'Comprar ahora' }}
          </button>
          <button 
            class="btn secondary block" 
            @click="vaciar"
            :disabled="clearingCart"
          >
            {{ clearingCart ? 'Vaciando...' : 'Vaciar carrito' }}
          </button>
        </div>
      </aside>
    </div>
  </section>
</template>

<script setup>
import {
  getCarrito,
  agregarCursoCarrito,
  quitarCursoCarrito,
  vaciarCarrito,
  checkoutCarrito,
} from "@/api/carrito";

import { ref, onMounted } from "vue";

const carrito = ref(null);
const loading = ref(false);
const removingItem = ref(null);
const clearingCart = ref(false);
const processingCheckout = ref(false);

// 🔹 Cargar carrito desde API
const cargarCarrito = async () => {
  loading.value = true;
  try {
    const { data } = await getCarrito();
    carrito.value = data;
  } catch (error) {
    console.error("Error al cargar el carrito:", error);
  } finally {
    loading.value = false;
  }
};

// 🔹 Quitar un curso del carrito
const quitarItem = async (cursoId) => {
  if (!carrito.value) return;
  removingItem.value = cursoId;
  try {
    await quitarCursoCarrito(carrito.value.id, cursoId);
    await cargarCarrito();
  } catch (error) {
    console.error("Error al quitar curso:", error);
  } finally {
    removingItem.value = null;
  }
};

// 🔹 Vaciar el carrito
const vaciar = async () => {
  if (!carrito.value) return;
  clearingCart.value = true;
  try {
    await vaciarCarrito(carrito.value.id);
    await cargarCarrito();
  } catch (error) {
    console.error("Error al vaciar carrito:", error);
  } finally {
    clearingCart.value = false;
  }
};

// 🔹 Checkout / Comprar
const checkout = async () => {
  if (!carrito.value) return;
  processingCheckout.value = true;
  try {
    // Crear la preferencia de pago y redirigir al usuario a MercadoPago.
    // No vaciamos el carrito en el front hasta que el backend confirme
    // que el pago fue exitoso y marque el carrito como completado.
    const response = await checkoutCarrito(carrito.value.id);
    if (response && response.data && response.data.init_point) {
      window.location.href = response.data.init_point;
      return;
    }
    alert("No se pudo iniciar el pago. Intenta nuevamente.");
  } catch (error) {
    console.error("Error al hacer checkout:", error);
  } finally {
    processingCheckout.value = false;
  }
};

// Cargar carrito al montar el componente
onMounted(cargarCarrito);
</script>

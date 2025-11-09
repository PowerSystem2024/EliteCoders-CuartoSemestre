<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const username = computed(() => authStore.user?.username || authStore.user?.email || null)
const appName = import.meta.env.VITE_APP_NAME || 'E-Commerce'

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

const mobileOpen = ref(false)
function toggleMenu() {
  mobileOpen.value = !mobileOpen.value
}
function closeMenu() {
  mobileOpen.value = false
}
</script>

<template>
  <header class="header">
    <nav :class="{ 'mobile-open': mobileOpen }">
      <RouterLink class="brand" to="/" @click="closeMenu">{{ appName }}</RouterLink>

      <button class="hamburger" @click="toggleMenu" :aria-expanded="mobileOpen" aria-label="Abrir menú">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>

      <div class="links" role="menu">
        <RouterLink to="/about" @click="closeMenu">Acerca de</RouterLink>
        <RouterLink to="/courses" @click="closeMenu">Cursos</RouterLink>
        <RouterLink to="/plans" @click="closeMenu">Planes</RouterLink>
        <RouterLink to="/cart" @click="closeMenu">Carrito</RouterLink>
      </div>

      <div class="spacer" aria-hidden="true"></div>

      <div class="auth-actions">
        <template v-if="username">
          <RouterLink :to="'/mis-cursos'" class="tag" @click="closeMenu">{{ username }}</RouterLink>
          <button class="btn secondary" @click="handleLogout" :disabled="authStore.isLoading">Salir</button>
        </template>

        <template v-else>
          <RouterLink to="/login" @click="closeMenu">Entrar</RouterLink>
        </template>
      </div>
    </nav>
  </header>
</template>

<style scoped>
.header {
  width: 100%;
  box-sizing: border-box;
  border-bottom: 1px solid #eee;
  padding: 8px 12px;
}
nav {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  max-width: 1200px;
  margin: 0 auto;
}

.brand {
  font-weight: 700;
  margin-right: 8px;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
}

.spacer {
  flex: 1 1 auto;
  min-width: 0;
}

.auth-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex: 0 0 auto;
  white-space: nowrap;
}

nav a, nav .tag, .btn {
  text-decoration: none;
  color: inherit;
  padding: 6px 8px;
  display: inline-block;
  white-space: nowrap;
}

@media (max-width: 600px) {
  nav {
    gap: 6px;
    padding: 4px 0;
    align-items: flex-start;
  }
  .brand {
    flex-basis: auto;
    flex: 0 0 auto;
  }
  .auth-actions {
    margin-left: 6px;
  }
  .hamburger { display: inline-flex !important; }
  .links {
    display: flex;
    flex-direction: column;
    gap: 6px;
    width: 100%;
    padding: 0;
    box-sizing: border-box;
    overflow: hidden;
    max-height: 0;
    opacity: 0;
    pointer-events: none;
    transform-origin: top center;
    transition: max-height 260ms ease, opacity 200ms ease, transform 220ms ease;
  }
  nav.mobile-open .links {
    max-height: 480px;
    opacity: 1;
    pointer-events: auto;
    transform: none;
    padding: 8px 0;
  }
  .auth-actions {
    transition: opacity 200ms ease, transform 220ms ease;
  }
  .auth-actions { opacity: 1; transform: none; }
  nav:not(.mobile-open) .auth-actions { opacity: 1; transform: none; }
  nav.mobile-open .auth-actions { order: 3; width: 100%; justify-content: flex-end; }
}

.hamburger {
  background: transparent;
  border: 0;
  padding: 6px;
  cursor: pointer;
  align-items: center;
  justify-content: center;
  line-height: 0;
  z-index: 60;
}
.hamburger svg { display: block; width: 24px; height: 24px; }

.header, nav { overflow-x: hidden; }
</style>

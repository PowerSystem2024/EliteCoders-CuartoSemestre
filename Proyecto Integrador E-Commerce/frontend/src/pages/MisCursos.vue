<template>
  <section class="container">
    <h1 class="h1">Mis cursos</h1>

    <div v-if="loading" class="center">⏳ Cargando tus cursos...</div>

    <div v-else>
      <div v-if="courses.length === 0" class="center">
        <div class="card" style="max-width:400px">
          <div class="card-content">
            <h2 class="h2">No tienes cursos inscritos</h2>
            <p style="color:var(--muted)">Explora nuestro catálogo y encuentra el curso perfecto para ti.</p>
          </div>
          <div class="card-footer">
            <RouterLink to="/courses" class="btn block">Ver cursos disponibles</RouterLink>
          </div>
        </div>
      </div>

      <div class="grid" v-else style="grid-template-columns:repeat(auto-fit,minmax(240px,1fr));">
        <article class="card" v-for="c in courses" :key="c.id">
          <div class="card-content">
            <h2 class="h2">{{ c.titulo }}</h2>
            <div style="display:flex;gap:.5rem;flex-wrap:wrap;margin:.3rem 0">
              <span class="tag">{{ c.categoria }}</span>
            </div>
          </div>
          <div class="card-footer">
            <div class="hr"></div>
            <div style="display:flex;justify-content:space-between;align-items:center;gap:0.5rem;flex-wrap:wrap">
              <strong>{{ formatPrice(c.precio) }}</strong>
              <div style="display:flex;gap:0.5rem;flex-wrap:wrap">
                <RouterLink class="btn" :to="`/courses/${c.id}`">
                  📖 Ver curso
                </RouterLink>
                <button 
                  class="btn secondary"
                  style="font-size:0.8rem;padding:0.5rem 0.8rem"
                  @click="confirmUninscript(c)"
                  :disabled="uninscribing === c.id"
                >
                  {{ uninscribing === c.id ? '⏳' : '❌' }}
                </button>
              </div>
            </div>
          </div>
        </article>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <div v-if="showConfirmation" class="modal-overlay" @click="closeConfirmation">
      <div class="modal-card" @click.stop>
        <div class="card">
          <div class="card-content">
            <h2 class="h2">⚠️ Confirmar desinscripción</h2>
            <p>¿Estás seguro de que quieres desinscribirte del curso:</p>
            <p><strong>{{ courseToUninscript?.titulo }}</strong></p>
            <p style="color:var(--muted);font-size:0.9rem">
              Esta acción no se puede deshacer. Perderás el acceso a todas las lecciones y tu progreso.
            </p>
          </div>
          <div class="card-footer">
            <div class="hr"></div>
            <div style="display:flex;gap:0.5rem;justify-content:flex-end">
              <button class="btn secondary" @click="closeConfirmation">
                Cancelar
              </button>
              <button 
                class="btn" 
                style="background:var(--error)"
                @click="executeUninscript"
                :disabled="uninscribing"
              >
                {{ uninscribing ? '⏳ Desinscribiendo...' : '✓ Confirmar' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMisCursos, uninscriptFromCourse } from '@/api/cursos'
import { formatPrice } from '../utils/stringUtils'

const courses = ref([])
const loading = ref(true)
const error = ref(null)
const uninscribing = ref(null)
const showConfirmation = ref(false)
const courseToUninscript = ref(null)

// 🔹 Load user courses
onMounted(async () => {
  await loadCourses()
})

const loadCourses = async () => {
  loading.value = true
  try {
    const { data } = await getMisCursos()
    courses.value = data
  } catch (err) {
    console.error('Error fetching mis cursos', err)
    // If unauthorized, redirect to login so user can authenticate
    if (err?.response?.status === 401) {
      // preserve next so user returns here after login
      window.location.href = `/login?next=/mis-cursos`
      return
    }
    error.value = err?.response?.data || 'No se pudieron cargar los cursos.'
  } finally {
    loading.value = false
  }
}

// 🔹 Show confirmation modal
const confirmUninscript = (course) => {
  courseToUninscript.value = course
  showConfirmation.value = true
}

// 🔹 Close confirmation modal
const closeConfirmation = () => {
  showConfirmation.value = false
  courseToUninscript.value = null
}

// 🔹 Execute uninscript action
const executeUninscript = async () => {
  if (!courseToUninscript.value) return
  
  uninscribing.value = courseToUninscript.value.id
  
  try {
    // Call the API to uninscript from course
    await uninscriptFromCourse(courseToUninscript.value.id)
    
    // Remove course from local list
    courses.value = courses.value.filter(c => c.id !== courseToUninscript.value.id)
    
    // Show success message
    alert(`Te has desinscrito exitosamente del curso "${courseToUninscript.value.titulo}"`)
    
    closeConfirmation()
    
  } catch (error) {
    console.error('Error uninscribing from course:', error)
    let errorMessage = 'Error al desinscribirse del curso. Inténtalo de nuevo.'
    
    // Handle specific error cases
    if (error?.response?.status === 404) {
      errorMessage = 'El curso no fue encontrado o ya no estás inscrito.'
    } else if (error?.response?.status === 403) {
      errorMessage = 'No tienes permisos para desinscribirte de este curso.'
    }
    
    alert(errorMessage)
  } finally {
    uninscribing.value = null
  }
}
</script>

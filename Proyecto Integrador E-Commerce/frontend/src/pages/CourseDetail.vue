
<script setup>
import { useRoute, useRouter } from 'vue-router'
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getCursoById, getMisCursos, getCursoLecciones } from '@/api/cursos'
import { getCarrito, agregarCursoCarrito } from '@/api/carrito'
import { formatPrice } from '../utils/stringUtils'

const route = useRoute()
const router = useRouter()

const course = ref(null)
const carrito = ref(null)
const userCourses = ref([])
const courseLessons = ref([])
const lessonsLoading = ref(false)
const pageLoading = ref(true)
const authStore = useAuthStore()

const extra = {
  1: { modalidad: "Remoto", ubicacion: "Online", duracion: "12h", nivel: "Inicial" },
  2: { modalidad: "Remoto", ubicacion: "Online", duracion: "8h",  nivel: "Intermedio" },
  3: { modalidad: "Remoto", ubicacion: "Online", duracion: "10h", nivel: "Inicial" },
  4: { modalidad: "Remoto", ubicacion: "Online", duracion: "9h",  nivel: "Inicial" }
}

const isEnrolled = computed(() => {
  if (!course.value || !userCourses.value.length) return false
  return userCourses.value.some(c => c.id === course.value.id)
})

const isInCart = computed(() => {
  if (!course.value || !carrito.value?.items) return false
  return carrito.value.items.some(item => item.curso === course.value.id)
})

const cartButtonText = computed(() => {
  if (isEnrolled.value) return 'Ya estás inscripto'
  if (isInCart.value) return 'Ya está en el carrito'
  return 'AGREGAR AL CARRITO'
})

const cartButtonDisabled = computed(() => isEnrolled.value || isInCart.value)

onMounted(async () => {
  const courseId = Number(route.params.id)
  pageLoading.value = true
  try {
    const promises = [ getCursoById(courseId), cargarCarrito() ]
    if (authStore.token) promises.push(cargarCursosUsuario())
    const [courseResponse] = await Promise.all(promises)
    course.value = { ...courseResponse.data, ...(extra[courseId] || {}) }
    if (authStore.token && isEnrolled.value) {
      await cargarLecciones(courseId)
    }
  } catch (e) {
    console.error(e)
  } finally {
    pageLoading.value = false
  }
})

const cargarLecciones = async (courseId) => {
  if (!authStore.token) return
  lessonsLoading.value = true
  try {
    const { data } = await getCursoLecciones(courseId)
    courseLessons.value = data
  } finally {
    lessonsLoading.value = false
  }
}

const cargarCursosUsuario = async () => {
  if (!authStore.token) return
  try {
    const { data } = await getMisCursos()
    userCourses.value = data
  } catch (e) { console.error(e) }
}

const cargarCarrito = async () => {
  if (!authStore.token) return
  try {
    const { data } = await getCarrito()
    carrito.value = data
  } catch (e) { console.error(e) }
}

function comprar() {
  if (!authStore.token) {
    router.push({ path: '/login', query: { next: `/checkout?course=${course.value?.id}` } })
    return
  }
  if (course.value) router.push(`/checkout?course=${course.value.id}`)
}

async function agregarAlCarrito() {
  if (!authStore.token) {
    router.push({ path: '/login', query: { next: route.fullPath } })
    return
  }
  if (isEnrolled.value || isInCart.value) return
  if (!course.value || !carrito.value) return
  try {
    await agregarCursoCarrito(carrito.value.id, course.value.id)
    await cargarCarrito()
    alert(`Curso "${course.value.titulo}" agregado al carrito.`)
  } catch (e) {
    console.error(e)
    alert("No se pudo agregar el curso al carrito.")
  }
}

function viewLesson(lesson, index) {
  const lessonId = lesson.id || (index + 1)
  router.push({
    path: `/courses/${course.value.id}/lessons/${lessonId}`,
  })
}
</script>

<template>
  <div v-if="pageLoading" class="container">
    <div class="center">
      <div class="card" style="max-width:400px">
        <div class="card-content" style="text-align:center">
          <h2 class="h2">⏳ Cargando curso...</h2>
          <p style="color:var(--muted);margin:1rem 0">Obteniendo información del curso y verificando tu acceso.</p>
          <div style="display:flex;justify-content:center;gap:0.5rem;margin-top:1rem">
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <section v-else-if="course" class="container">
    <h1 class="h1">{{ course.titulo }}</h1>

    <div v-if="isEnrolled" class="sidebar-grid">
      <div>
        <div class="card" style="margin-bottom: 1rem">
          <div class="card-content">
            <h2 class="h2">🎓 Estás inscrito en este curso</h2>
            <p style="color: var(--muted)">Accedé a todo el contenido.</p>
          </div>
        </div>

        <div class="card">
          <div class="card-content">
            <h3 class="h2">📚 Lecciones del curso</h3>

            <div v-if="lessonsLoading" style="text-align:center;margin:1rem 0">
              <p style="color:var(--muted)">⏳ Cargando lecciones...</p>
            </div>

            <div v-else-if="courseLessons.length === 0" style="text-align:center;margin:1rem 0">
              <p style="color:var(--muted)">📭 No hay lecciones disponibles.</p>
            </div>

            <div v-else class="grid" style="gap:0.5rem;margin-top:1rem">
              <div
                v-for="(lesson, index) in courseLessons"
                :key="lesson.id || index"
                class="list-pill lesson-item"
                @click="viewLesson(lesson, index)"
              >
                <span>
                  <strong>Lección {{ index + 1 }}:</strong> {{ lesson.titulo || lesson.title }}
                  <span v-if="lesson.duracion || lesson.duration" style="color:var(--muted);font-weight:normal">
                    ({{ lesson.duracion || lesson.duration }})
                  </span>
                </span>
                <span>▶️</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <aside class="card">
        <div class="card-content">
          <h2 class="h2">Información del curso</h2>
          <p style="color:var(--muted)">{{ course.descripcion }}</p>

          <div class="mt-3 p-3 rounded-lg" style="background:#f8fafc">
            <h4 class="h3" style="margin-bottom:0.5rem">🧾 Ficha técnica</h4>
            <ul class="text-sm" style="color:#334155">
              <li><strong>Modalidad:</strong> {{ course.modalidad || 'Remoto' }}</li>
              <li><strong>Ubicación:</strong> {{ course.ubicacion || 'Online' }}</li>
              <li><strong>Duración:</strong> {{ course.duracion  || '8h' }}</li>
              <li><strong>Nivel:</strong>     {{ course.nivel     || 'Inicial' }}</li>
            </ul>
          </div>

          <div style="margin: 1rem 0">
            <p><strong>👨‍🏫 Instructor:</strong> {{ course.instructor?.nombre || '—' }}</p>
            <p><strong>📂 Categoría:</strong> {{ course.categoria?.nombre || '—' }}</p>
            <p><strong>💰 Precio:</strong> {{ formatPrice(course.precio) }}</p>
          </div>
        </div>
        <div class="card-footer">
          <div class="hr"></div>
          <RouterLink to="/mis-cursos" class="btn secondary block">📋 Ir a Mis Cursos</RouterLink>
        </div>
      </aside>
    </div>

    <div v-else class="sidebar-grid">
      <div>
        <div class="list-pill">Modalidad</div>
        <div class="list-pill">Programa</div>
        <div class="list-pill">Salida laboral y testimonios</div>
        <div class="list-pill">Preguntas Frecuentes</div>

        <div class="list-pill"><strong>{{ formatPrice(course.precio) }}</strong></div>

        <button
          class="btn block"
          :class="{ 'btn-disabled': cartButtonDisabled }"
          style="margin-top:0.5rem"
          @click="agregarAlCarrito"
          :disabled="cartButtonDisabled"
        >
          {{ cartButtonText }}
        </button>
      </div>

      <aside class="card">
        <div class="card-content">
          <h2 class="h2">Resumen del curso</h2>
          <p style="color:var(--muted)">{{ course.descripcion }}</p>

          <div class="mt-3 p-3 rounded-lg" style="background:#f8fafc">
            <h4 class="h3" style="margin-bottom:0.5rem">🧾 Ficha técnica</h4>
            <ul class="text-sm" style="color:#334155">
              <li><strong>Modalidad:</strong> {{ course.modalidad || 'Remoto' }}</li>
              <li><strong>Ubicación:</strong> {{ course.ubicacion || 'Online' }}</li>
              <li><strong>Duración:</strong> {{ course.duracion  || '8h' }}</li>
              <li><strong>Nivel:</strong>     {{ course.nivel     || 'Inicial' }}</li>
            </ul>
          </div>

          <p class="mt-3"><strong>👨‍🏫 Instructor:</strong> {{ course.instructor?.nombre || '—' }}</p>
          <p><strong>📂 Categoría:</strong> {{ course.categoria?.nombre || '—' }}</p>
        </div>
      </aside>
    </div>
  </section>

  <div v-else class="container">
    <div class="center">
      <div class="card" style="max-width:400px">
        <div class="card-content" style="text-align:center">
          <h2 class="h2">❌ Error al cargar</h2>
          <p style="color:var(--muted)">No se pudo cargar la información del curso.</p>
        </div>
        <div class="card-footer">
          <button class="btn block" @click="$router.go(-1)">← Volver</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>

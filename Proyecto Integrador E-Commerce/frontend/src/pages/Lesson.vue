<template>
	<div class="lesson-page">
		<div v-if="loading" class="loading">Cargando lección...</div>
		<div v-else-if="error" class="error">{{ error }}</div>

		<article v-else class="lesson-article">
			<h1 class="title">{{ lesson.titulo }}</h1>
			<p class="meta">Curso: <strong>{{ courseTitle }}</strong></p>

			<div v-if="lesson.video_url" class="video-wrapper">
				<iframe
					:src="embedVideoUrl(lesson.video_url)"
					frameborder="0"
					allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
					allowfullscreen
				></iframe>
			</div>

			<div v-if="lesson.contenido_texto" class="content" v-html="lesson.contenido_texto"></div>

			<div v-if="lesson.material_adjunto" class="material">
				<a :href="lesson.material_adjunto" target="_blank" rel="noopener">📎 Descargar material</a>
			</div>

			<div class="actions">
				<button @click="goBack" class="btn">Volver al curso</button>
			</div>
		</article>
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

// Priorizar la convención de rutas frontend: /courses/:id/lessons/:lessonId
// Mantener compatibilidad con nombres antiguos (cursoId, curso_pk, leccion_pk, etc.).
const cursoId = (
	route.params.id ||
	route.params.courseId ||
	route.params.cursoId ||
	route.params.curso_pk ||
	route.params.curso ||
	null
)

const lessonId = (
	route.params.lessonId ||
	route.params.lesson_id ||
	route.params.leccion_pk ||
	route.params.leccionId ||
	route.params.pk ||
	null
)

const lesson = ref(null)
const loading = ref(true)
const error = ref(null)
const courseTitle = ref('')

async function fetchLesson() {
	loading.value = true
	error.value = null
	try {
		if (!cursoId || !lessonId) throw new Error('Parámetros de ruta incompletos')
		// Endpoint esperado (ver `LeccionViewSet` en backend): /api/v1/cursos/:curso_pk/lecciones/:pk/
		const url = `/api/v1/cursos/${cursoId}/lecciones/${lessonId}/`
		const res = await axios.get(url)
		lesson.value = res.data
		courseTitle.value = lesson.value.curso?.titulo || ''
	} catch (err) {
		console.error('Error fetching lesson', err)
		if (err.response && err.response.status === 404) {
			error.value = 'Lección no encontrada'
		} else {
			error.value = 'Error cargando la lección. Revisa la consola para más detalles.'
		}
	} finally {
		loading.value = false
	}
}

onMounted(fetchLesson)

function embedVideoUrl(url) {
	if (!url) return ''
	try {
		// Detectar enlaces de YouTube y convertirlos a embed si es posible
		if (url.includes('youtube.com') || url.includes('youtu.be')) {
			// Extraer id del video
			const idMatch = url.match(/(?:v=|\/|be\/)([A-Za-z0-9_-]{11})/)
			const id = idMatch ? idMatch[1] : null
			if (id) return `https://www.youtube.com/embed/${id}`
		}
	} catch (e) {
		// fallthrough
	}
	// Si no es YouTube o no se pudo extraer, devolver la URL tal cual
	return url
}

function goBack() {
	// Intentar volver a la vista del curso; si no existe, navegar atrás en el historial
	if (cursoId) {
		// Nombre de ruta tentativa: 'CourseDetail' o 'CursoDetalle' — usamos push por path si no se conoce el nombre
		router.push({ path: `/courses/${cursoId}` }).catch(() => router.back())
	} else {
		router.back()
	}
}
</script>

<style scoped>
.lesson-page {
	max-width: 900px;
	margin: 24px auto;
	padding: 0 16px;
}
.loading, .error { text-align: center; margin: 16px 0; }
.title { font-size: 1.8rem; margin-bottom: 6px; }
.meta { color: #555; margin-bottom: 12px; }
.video-wrapper { margin: 16px 0; position: relative; padding-bottom: 56.25%; height: 0; }
.video-wrapper iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
.content { margin: 12px 0; line-height: 1.6; }
.material { margin: 12px 0; }
.actions { margin-top: 18px; }
.btn { background: #2b6cb0; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; }
.btn:hover { background: #234e7a; }
</style>


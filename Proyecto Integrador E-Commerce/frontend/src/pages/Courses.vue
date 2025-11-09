<script setup>
import { ref, onMounted } from "vue";
import { RouterLink } from "vue-router";
import { getCursos } from "@/api/cursos";
import vueCourse      from "@/assets/courses/vue-course.jpg";
import uxCourse       from "@/assets/courses/ux-course.jpg";
import dataCourse     from "@/assets/courses/data-course.png";
import marketingCourse from "@/assets/courses/marketing-course.jpg";
import placeholder    from "@/assets/courses/placeholder.jpg";
import { formatPrice } from "../utils/stringUtils";

const cursos = ref([]);
const loading = ref(true);

// Mapea el ID de curso a su imagen local
const imgById = {
  1: vueCourse,
  2: uxCourse,
  3: dataCourse,
  4: marketingCourse,
};

onMounted(async () => {
  try {
    const { data } = await getCursos();
    // combinamos datos de API + imagen/import + meta extra
    cursos.value = data.map(c => ({
      ...c,
      imagen: imgById[c.id] || placeholder,
      modalidad: c.modalidad || (c.id === 2 ? "Presencial" : "Remoto"),
      ubicacion: c.ubicacion || (c.id === 2 ? "Sede Centro" : "Online"),
      duracion:  c.duracion  || (c.id === 1 ? "12h" : c.id === 3 ? "10h" : "8h"),
      nivel:     c.nivel     || (c.id === 2 ? "Intermedio" : "Inicial"),
    }));
  } catch (e) {
    console.error("Error cargando cursos:", e);
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <section class="courses-section">
    <h1 class="title">Nuestros Cursos</h1>
    <p class="lead">Elegí un curso y hacé clic para ver el detalle.</p>

    <div v-if="loading" class="loading">Cargando cursos...</div>

    <div v-else class="courses-grid">
      <RouterLink
        v-for="c in cursos"
        :key="c.id"
        :to="`/courses/${c.id}`"
        class="course-card"
      >
        <!-- ✅ ahora usa la variable importada -->
        <img :src="c.imagen" :alt="c.titulo" class="course-img" />
        <div class="course-body">
          <h3 class="course-title">{{ c.titulo }}</h3>
          <p class="course-desc">{{ c.descripcion }}</p>

          <div class="chips">
            <span class="chip chip-blue">{{ c.modalidad }}</span>
            <span class="chip chip-green">{{ c.nivel }}</span>
            <span class="chip chip-gray">{{ c.duracion }}</span>
            <span class="chip chip-purple">{{ c.ubicacion }}</span>
          </div>

          <div class="course-footer">
            <div class="price">{{ formatPrice(c.precio) }}</div>
            <span class="ver-mas">Ver detalle →</span>
          </div>
        </div>
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.courses-section { padding: 2rem 1rem; max-width: 1120px; margin: 0 auto; }
.title { font-size: 2rem; font-weight: 700; text-align: center; }
.lead { text-align: center; color: #64748b; margin-top: .5rem; }
.loading { text-align: center; margin-top: 2rem; color: #475569; }

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.25rem; margin-top: 1.5rem;
}
.course-card {
  display: block; text-decoration: none; color: inherit;
  background: #fff; border: 1px solid #e2e8f0;
  border-radius: 14px; overflow: hidden;
  transition: transform .2s, box-shadow .2s, border-color .2s;
}
.course-card:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,.06); border-color: #cbd5e1; }
.course-img { width: 100%; max-height: 220px; object-fit: cover; display: block; }
.course-body { padding: 12px 14px 14px; }
.course-title { font-weight: 600; font-size: 1.05rem; color: #000; }
.course-desc { margin-top: .25rem; color: #64748b; font-size: .92rem; min-height: 44px; }

.chips { display: flex; flex-wrap: wrap; gap: .4rem; margin-top: .6rem; }
.chip { font-size: .75rem; padding: .25rem .5rem; border-radius: 999px; border: 1px solid transparent; }
.chip-blue   { background: #eff6ff; color: #2563eb; border-color:#bfdbfe; }
.chip-green  { background: #ecfdf5; color: #059669; border-color:#a7f3d0; }
.chip-gray   { background: #f1f5f9; color: #334155; border-color:#e2e8f0; }
.chip-purple { background: #f5f3ff; color: #7c3aed; border-color:#ddd6fe; }

.course-footer { margin-top: .75rem; display: flex; align-items: center; justify-content: space-between; }
.price { font-weight: 700; font-size: 1.05rem; color: var(--mint) }
.ver-mas { color: #2563eb; font-weight: 600; font-size: .9rem; }
</style>

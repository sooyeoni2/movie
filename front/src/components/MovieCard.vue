<template>
  <div class="card" @click="$router.push(`/movies/${movie.id}`)">
    <div class="poster-wrapper">
      <img :src="posterUrl" class="poster" alt="poster" />

      <!-- Hover Info -->
      <div class="movie-hover-info">
        <h3 class="title">{{ movie.title }}</h3>
        <p class="meta-info">
          {{ directorName }} · ⭐ {{ movie.vote_average.toFixed(1) }}
        </p>
        <p class="overview">{{ movie.overview }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  movie: { type: Object, required: true }
})

const posterUrl = props.movie.poster_path
  ? `https://image.tmdb.org/t/p/w500${props.movie.poster_path}`
  : 'https://via.placeholder.com/500x750'

const directorName = ref('')

onMounted(async () => {
  try {
    const res = await axios.get(
      `https://api.themoviedb.org/3/movie/${props.movie.id}/credits`,
      {
        params: {
          api_key: import.meta.env.VITE_TMDB_API_KEY,
          language: 'ko-KR'
        }
      }
    )
    const director = res.data.crew.find(p => p.job === 'Director')
    directorName.value = director?.name || '정보 없음'
  } catch (err) {
    console.error(err)
  }
})
</script>

<style scoped>
/* CARD */
.card {
  background: #1c1c1c;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  height: 100%;                /* ⭐ grid 셀 높이 고정 */
  transition: box-shadow 0.3s ease;
}

.card:hover {
  box-shadow: 0 18px 40px rgba(0,0,0,0.45);
}

/* POSTER */
.poster-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 2 / 3;         /* ⭐ 핵심 */
  overflow: hidden;
}

.poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.card:hover .poster {
  transform: scale(1.05);      /* 포스터만 확대 */
}

/* HOVER INFO */
.movie-hover-info {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.78);
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 18px;
  text-align: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.card:hover .movie-hover-info {
  opacity: 1;
}

/* TEXT */
.title {
  font-size: 0.95rem;
  font-weight: 700;
  margin-bottom: 8px;
  line-height: 1.3;
}

.meta-info {
  font-size: 0.8rem;
  color: #ddd;
  margin-bottom: 12px;
}

.overview {
  font-size: 0.78rem;
  line-height: 1.4;
  color: #ccc;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
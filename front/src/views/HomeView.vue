<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()

const movies = ref([])
const currentIndex = ref(0)
const intervalId = ref(null)
const keyword = ref('')

const fetchPopularMovies = async () => {
  try {
    const response = await axios.get(
      'https://api.themoviedb.org/3/movie/popular',
      {
        params: {
          api_key: import.meta.env.VITE_TMDB_API_KEY,
          language: 'ko-KR',
          page: 1,
        },
      }
    )
    movies.value = response.data.results

    if (movies.value.length > 0) {
      startBackgroundRotation()
    }
  } catch (error) {
    console.error(error)
  }
}

const startBackgroundRotation = () => {
  intervalId.value = setInterval(() => {
    currentIndex.value = (currentIndex.value + 1) % movies.value.length
  }, 5000)
}

const getBackgroundUrl = computed(() => {
  if (movies.value.length === 0) return ''
  const movie = movies.value[currentIndex.value]
  return `https://image.tmdb.org/t/p/original/${
    movie.backdrop_path || movie.poster_path
  }`
})

// 로그인 체크 추가
const handleSearch = () => {
  if (!keyword.value.trim()) return

  // 로그인 체크
  if (!authStore.isLoggedIn) {
    alert('로그인이 필요합니다.')
    router.push('/login')
    return
  }

  router.push({
    path: '/review-search',
    query: { q: keyword.value.trim() },
  })
}

onMounted(() => {
  fetchPopularMovies()
})

onBeforeUnmount(() => {
  if (intervalId.value) {
    clearInterval(intervalId.value)
  }
})
</script>

<template>
  <div
    class="background-container"
    :style="{ backgroundImage: `url(${getBackgroundUrl})` }"
  >
    <div class="overlay"></div>

    <div class="intro-text-container">
      <!-- 🔹 텍스트 로고 이미지 -->
      <img
        src="@/assets/logo.png"
        alt="Movie Archive Manager"
        class="logo"
      />

      <p class="tagline">영화를 기록하고, 다시 발견하다</p>

      <!-- 🔹 검색 영역 -->
      <div class="search-container">
        <input
          v-model="keyword"
          type="text"
          placeholder="영화 제목 또는 리뷰 키워드"
          @keyup.enter="handleSearch"
        />
        <button type="button" class="btn-primary" @click="handleSearch">
          검색
        </button>
      </div>
    </div>
  </div>
</template>


<style scoped>
.background-container {
  position: relative;
  width: 100%;
  height: 100vh;
  background-size: cover;
  background-position: center;
  transition: background-image 1s ease-in-out;
}

/* 다크 오버레이 + 살짝 블러 느낌 */
.overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    rgba(0, 0, 0, 0.65),
    rgba(0, 0, 0, 0.65)
  );
  z-index: 1;
}

/* 중앙 히어로 영역 */
.intro-text-container {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 2;
  color: white;
  text-align: center;
  padding: 20px;
}

/* 로고 */
.logo {
  width: 500px;
  max-width: 100%;
}

/* 서브 문구 */
.tagline {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 40px;
}

.search-container {
  display: flex;
  gap: 10px;
  width: 100%;
  max-width: 500px;  

  padding: 12px 16px;  
  border-radius: 18px;

  background: rgba(28, 28, 28, 0.5); 
  backdrop-filter: blur(12px);

  box-shadow: 0 16px 40px rgba(0,0,0,0.3);  
}

.search-container input {
  flex: 1;
  padding: 10px 12px;  
  font-size: 0.95rem;  

  border-radius: 12px;
  border: none;
  outline: none;

  background: rgba(31, 31, 31, 0.6); 
  color: #f9fafb;
}

.search-container input::placeholder {
  color: #8b8b8b;
}

.search-container input:focus {
  outline: 2px solid #7dd3fc;
  background: rgba(31, 31, 31, 0.8); 
}

.btn-primary {
  padding: 10px 20px;  
  font-size: 0.9rem; 
  font-weight: 600;

  border-radius: 12px;
  border: none;
  cursor: pointer;

  background: linear-gradient(
    135deg,
    #7dd3fc,
    #38bdf8
  );
  color: #0f172a;

  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(125, 211, 252, 0.45);
}

/* 반응형 */
@media (max-width: 768px) {
  .logo {
    width: 280px;
  }

  .search-container {
    flex-direction: column;
    width: 100%;
    max-width: 90%;
  }

  .search-container input,
  .btn-primary {
    width: 100%;
  }
}
</style>
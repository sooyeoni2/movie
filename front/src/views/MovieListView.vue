<template>
  <div class="page">

    <!-- HERO -->
    <section class="list-hero">
      <img
        src="@/assets/logo.png"
        alt="Movie Archive"
        class="hero-logo"
      />
      <p>장르, 정렬, 제목 검색으로 원하는 영화를 찾아보세요</p>
    </section>

    <div class="wrapper">

      <!-- FILTER BAR -->
      <div class="filter-section">
        <div class="select-group">

          <!-- LEFT FILTERS -->
          <div class="left-group">
            <div class="select-item">
              <label class="label">장르</label>
              <select v-model="selectedGenre" @change="resetAndFetch">
                <option value="">모든 장르</option>
                <option
                  v-for="genre in genres"
                  :key="genre.id"
                  :value="genre.id"
                >
                  {{ genre.name }}
                </option>
              </select>
            </div>

            <div class="select-item">
              <label class="label">정렬</label>
              <select v-model="sortBy" @change="resetAndFetch">
                <option value="popularity.desc">인기순</option>
                <option value="primary_release_date.desc">최신순</option>
                <option value="vote_average.desc">평점순</option>
              </select>
            </div>
          </div>

          <!-- RIGHT SEARCH -->
          <div class="search-item">
            <input
              type="text"
              placeholder="영화 제목 검색"
              v-model="keyword"
              @keyup.enter="resetAndFetch"
            />
            <button class="search-btn" @click="resetAndFetch">
              검색
            </button>
          </div>

        </div>
      </div>

      <!-- CONTENT -->
      <div v-if="loading" class="state-text">
        영화 불러오는 중...
      </div>

      <div v-else-if="movies.length === 0" class="state-text">
        조건에 맞는 영화가 없습니다
      </div>

      <div v-else>
        <div class="grid">
          <MovieCard
            v-for="movie in movies"
            :key="movie.id"
            :movie="movie"
          />
        </div>

        <!-- 페이지네이션 추가 -->
        <div class="pagination" v-if="totalPages > 1">
          <button 
            @click="goToPage(currentPage - 1)" 
            :disabled="currentPage === 1"
            class="page-btn"
          >
            이전
          </button>

          <div class="page-numbers">
            <button
              v-for="page in displayPages"
              :key="page"
              @click="goToPage(page)"
              :class="{ active: page === currentPage }"
              class="page-num"
            >
              {{ page }}
            </button>
          </div>

          <button 
            @click="goToPage(currentPage + 1)" 
            :disabled="currentPage === totalPages"
            class="page-btn"
          >
            다음
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import MovieCard from '@/components/MovieCard.vue'

const route = useRoute()
const router = useRouter()

const movies = ref([])
const genres = ref([])
const selectedGenre = ref('')
const sortBy = ref('popularity.desc')
const keyword = ref('')
const loading = ref(false)

// 페이지네이션 추가
const currentPage = ref(1)
const totalPages = ref(1)

const API_KEY = import.meta.env.VITE_TMDB_API_KEY
const BASE_URL = 'https://api.themoviedb.org/3'

// 표시할 페이지 번호 계산
const displayPages = computed(() => {
  const pages = []
  const maxDisplay = 5

  let start = Math.max(1, currentPage.value - 2)
  let end = Math.min(totalPages.value, start + maxDisplay - 1)

  if (end - start < maxDisplay - 1) {
    start = Math.max(1, end - maxDisplay + 1)
  }

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  return pages
})

// 페이지 이동
const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  updateURLQuery()
  fetchMovies()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 필터 변경 시 첫 페이지로 리셋
const resetAndFetch = () => {
  currentPage.value = 1
  updateURLQuery()
  fetchMovies()
}

// URL 쿼리 업데이트 함수
const updateURLQuery = () => {
  const query = {}
  
  if (selectedGenre.value) {
    query.genre = selectedGenre.value
  }
  if (sortBy.value !== 'popularity.desc') {
    query.sort = sortBy.value
  }
  if (keyword.value) {
    query.keyword = keyword.value
  }
  if (currentPage.value > 1) {
    query.page = currentPage.value
  }
  
  router.push({ query })
}

onMounted(async () => {
  // URL 쿼리에서 필터 상태 복원
  if (route.query.genre) {
    selectedGenre.value = route.query.genre
  }
  if (route.query.sort) {
    sortBy.value = route.query.sort
  }
  if (route.query.keyword) {
    keyword.value = route.query.keyword
  }
  if (route.query.page) {
    currentPage.value = Number(route.query.page)
  }

  try {
    const genreRes = await axios.get(
      `${BASE_URL}/genre/movie/list`,
      {
        params: {
          api_key: API_KEY,
          language: 'ko-KR'
        }
      }
    )
    genres.value = genreRes.data.genres
    fetchMovies()
  } catch (err) {
    console.error(err)
  }
})

// 필터 변경 시 URL 쿼리 업데이트
watch([selectedGenre, sortBy, keyword], () => {
  updateURLQuery()
})

const fetchMovies = async () => {
  loading.value = true

  try {
    let results = []
    let totalPagesFromAPI = 1

    // 🔹 검색어가 있을 때 (search + 프론트 필터/정렬)
    if (keyword.value.trim()) {
      const res = await axios.get(
        `${BASE_URL}/search/movie`,
        {
          params: {
            api_key: API_KEY,
            language: 'ko-KR',
            query: keyword.value,
            page: currentPage.value
          }
        }
      )

      results = res.data.results
      totalPagesFromAPI = res.data.total_pages

      // 장르 필터 (프론트)
      if (selectedGenre.value) {
        results = results.filter(movie =>
          movie.genre_ids?.includes(Number(selectedGenre.value))
        )
      }

      // 정렬 (프론트)
      if (sortBy.value === 'popularity.desc') {
        results.sort((a, b) => b.popularity - a.popularity)
      } else if (sortBy.value === 'primary_release_date.desc') {
        results.sort(
          (a, b) =>
            new Date(b.release_date || 0) -
            new Date(a.release_date || 0)
        )
      } else if (sortBy.value === 'vote_average.desc') {
        results = results
          .filter(m => m.vote_count >= 100)
          .sort((a, b) => b.vote_average - a.vote_average)
      }

    } else {
      // 🔹 검색어 없을 때 (discover API)
      const params = {
        api_key: API_KEY,
        language: 'ko-KR',
        page: currentPage.value,
        sort_by: sortBy.value,
        with_genres: selectedGenre.value || undefined
      }

      if (sortBy.value === 'vote_average.desc') {
        params['vote_count.gte'] = 100
      }

      const res = await axios.get(
        `${BASE_URL}/discover/movie`,
        { params }
      )

      results = res.data.results
      totalPagesFromAPI = res.data.total_pages
    }

    movies.value = results
    totalPages.value = Math.min(totalPagesFromAPI, 500)

  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* PAGE */
.page {
  background: #111;
  min-height: 100vh;
}

/* HERO */
.list-hero {
  padding: 102px 40px 40px;
  text-align: center;

  background:
    radial-gradient(
      ellipse at top,
      rgba(120, 200, 255, 0.15),
      transparent 60%
    ),
    linear-gradient(to bottom, #000, #111);
}

.hero-logo {
  height: 64px;
  object-fit: contain;
  filter:
    drop-shadow(0 4px 14px rgba(120, 200, 255, 0.5))
    drop-shadow(0 0 24px rgba(120, 200, 255, 0.35));
}

.list-hero p {
  margin-top: 20px;
  font-size: 1.1rem;
  color: #aaa;
}

/* WRAPPER */
.wrapper {
  max-width: 1600px;
  margin: 0 auto;
  padding: 40px 20px 80px;
}

/* FILTER */
.filter-section {
  position: sticky;
  top: 90px;
  z-index: 10;

  margin-bottom: 40px;
  padding: 20px 24px;

  background: rgba(28, 28, 28, 0.85);
  backdrop-filter: blur(10px);
  border-radius: 16px;

  box-shadow: 0 12px 30px rgba(0,0,0,0.35);
}

.select-group {
  display: flex;
  align-items: center;
  gap: 24px;
}

.left-group {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.select-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.label {
  font-weight: 600;
  color: #ddd;
}

select {
  padding: 8px 14px;
  font-size: 0.95rem;
  border-radius: 8px;
  border: none;
  background: #2a2a2a;
  color: #fff;
  cursor: pointer;
}

select:focus {
  outline: 2px solid #7dd3fc;
}

/* SEARCH */
.search-item {
  margin-left: auto;
  display: flex;
  gap: 10px;
}

.search-item input {
  width: 240px;
  padding: 9px 14px;
  border-radius: 10px;
  border: none;
  background: #2a2a2a;
  color: #fff;
  font-size: 0.95rem;
}

.search-item input::placeholder {
  color: #888;
}

.search-item input:focus {
  outline: 2px solid #7dd3fc;
}

/* ⭐ 검색 버튼 */
.search-btn {
  padding: 9px 20px;
  border-radius: 10px;
  border: none;
  background: #7dd3fc;
  color: #000;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.search-btn:hover {
  background: #5bb8f0;
  transform: translateY(-1px);
}

.search-btn:active {
  transform: translateY(0);
}

/* STATES */
.state-text {
  text-align: center;
  padding: 100px 0;
  color: #bbb;
  font-size: 1.1rem;
}

/* GRID */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 32px;
}

/* 페이지네이션 스타일 추가 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 50px;
  padding-top: 30px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.page-btn {
  padding: 10px 20px;
  background: #2a2a2a;
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #3a3a3a;
  transform: translateY(-1px);
}

.page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 6px;
}

.page-num {
  min-width: 40px;
  padding: 10px;
  background: #2a2a2a;
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.page-num:hover {
  background: #3a3a3a;
  transform: translateY(-1px);
}

.page-num.active {
  background: #7dd3fc;
  color: #000;
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .hero-logo {
    height: 52px;
  }

  .select-group {
    flex-direction: column;
    align-items: stretch;
  }

  .search-item {
    margin-left: 0;
  }

  .search-item input {
    width: 100%;
  }

  .pagination {
    flex-wrap: wrap;
    gap: 8px;
  }

  .page-numbers {
    order: 3;
    width: 100%;
    justify-content: center;
  }
}
</style>
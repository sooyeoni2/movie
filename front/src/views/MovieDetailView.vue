<template>
  <div class="detail-page">
    <section class="hero">
      <!-- 닫기 버튼 -->
      <button class="close-btn" @click="goBack">✕</button>

      <!-- Background Trailer -->
      <iframe
        v-if="trailerKey"
        class="hero-video"
        :src="youtubeBgUrl"
        frameborder="0"
        allow="autoplay; encrypted-media"
      ></iframe>

      <!-- Overlay -->
      <div
        class="hero-overlay"
        :class="{ hidden: !showInfo }"
      >
        <div class="hero-content">
          <img class="poster" :src="posterUrl" alt="poster" />
          <h1 class="hero-title">{{ movie.title }}</h1>

          <div class="hero-meta">
            <span>{{ movie.release_date }}</span>
            <span>{{ movie.runtime }}분</span>
            <span>⭐ {{ rating }}</span>
          </div>

          <p class="hero-overview">{{ movie.overview }}</p>
        </div>
      </div>

      <!-- 버튼 묶음 -->
      <div class="action-group">
        <!-- 영화 찜 -->
        <button
          v-if="!watchlistStore.isInWatchlist(movie.id)"
          class="action-btn"
          @click="addToWatchlist">+ 나중에 볼 영화</button>

        <button
          v-else
          class="watchlist-btn added"
          @click="removeFromWatchlist">✓ 나중에 볼 영화        </button>

        <!-- Action Button (원본) -->
        <button class="action-btn" @click="toggleInfo">
          <span v-if="showInfo">▶ 예고편 보기</span>
          <span v-else>☰ 설명 보기</span>
        </button>
      </div>
    </section>

    <!-- 리뷰 섹션 -->
    <section class="reviews-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">
            사용자 리뷰 ({{ reviews.length }})
          </h2>
        </div>

        <div v-if="loadingReviews" class="loading">
          리뷰를 불러오는 중...
        </div>

        <div v-else-if="reviews.length === 0" class="no-reviews">
          <p>아직 작성된 리뷰가 없습니다.</p>
          <button class="btn-write" @click="goToWriteReview">
            리뷰 작성하기
          </button>
        </div>

        <div v-else class="reviews-list">
          <div 
            v-for="review in reviews" 
            :key="review.id"
            class="review-card"
            @click="goToReviewDetail(review.id)"
          >
            <div class="review-header">
              <div class="user-info">
                <span class="username">{{ review.user_name || review.username || '익명' }}</span>
                <span class="rating">⭐ {{ review.rating }}</span>
              </div>
              <span class="time">{{ formatDate(review.created_at) }}</span>
            </div>
            <p class="review-content">{{ review.content }}</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useWatchlistStore } from '@/stores/watchlist'

const route = useRoute()
const router = useRouter()
const movieId = route.params.movieId
const apiKey = import.meta.env.VITE_TMDB_API_KEY
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const watchlistStore = useWatchlistStore()

const movie = ref({})
const trailerKey = ref('')
const showInfo = ref(true)
const reviews = ref([])
const loadingReviews = ref(false)

const rating = computed(() =>
  movie.value.vote_average ? movie.value.vote_average.toFixed(1) : '0.0'
)

const posterUrl = computed(() =>
  movie.value.poster_path
    ? `https://image.tmdb.org/t/p/w500${movie.value.poster_path}`
    : ''
)

// 리뷰 불러오기
const loadReviews = async () => {
  loadingReviews.value = true
  try {
    const response = await axios.get(`${API_URL}/api/accounts/reviews/`)
    // 현재 영화 제목과 일치하는 리뷰만 필터링
    reviews.value = response.data.filter(
      review => review.movie_id === parseInt(movieId) || 
                review.movie_title === movie.value.title
    )
  } catch (error) {
    console.error('리뷰 로딩 실패:', error)
    reviews.value = []
  } finally {
    loadingReviews.value = false
  }
}

// 날짜 포맷 함수
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (days > 7) {
    return date.toLocaleDateString('ko-KR', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    })
  } else if (days > 0) {
    return `${days}일 전`
  } else if (hours > 0) {
    return `${hours}시간 전`
  } else if (minutes > 0) {
    return `${minutes}분 전`
  } else {
    return '방금 전'
  }
}

// 커뮤니티 페이지로 이동
const goToCommunity = () => {
  router.push('/community')
}

// 리뷰 상세 페이지로 이동
const goToReviewDetail = (reviewId) => {
  router.push(`/community/${reviewId}`)
}

// 리뷰 작성하기 (영화 정보 전달)
const goToWriteReview = () => {
  router.push({
    path: '/community',
    query: {
      movieId: movie.value.id,
      movieTitle: movie.value.title,
      posterPath: movie.value.poster_path,
      releaseDate: movie.value.release_date
    }
  })
}

onMounted(async () => {
  const movieRes = await axios.get(
    `https://api.themoviedb.org/3/movie/${movieId}?api_key=${apiKey}&language=ko-KR`
  )
  movie.value = movieRes.data

  const videoRes = await axios.get(
    `https://api.themoviedb.org/3/movie/${movieId}/videos?api_key=${apiKey}&language=ko-KR`
  )

  const trailer = videoRes.data.results.find(
    v => v.type === 'Trailer' && v.site === 'YouTube'
  )

  trailerKey.value = trailer?.key || ''
  
  // 리뷰 로드
  await loadReviews()
})

const youtubeBgUrl = computed(() =>
  trailerKey.value
    ? `https://www.youtube.com/embed/${trailerKey.value}?autoplay=1&mute=0&loop=1&playlist=${trailerKey.value}&controls=0&modestbranding=1&playsinline=1`
    : ''
)

const toggleInfo = () => {
  showInfo.value = !showInfo.value
}

const goBack = () => {
  router.back()  // 브라우저 히스토리에서 이전 페이지로 (쿼리 유지)
}

const addToWatchlist = () => {
  watchlistStore.addToWatchlist(movie.value)
}

const removeFromWatchlist = () => {
  watchlistStore.removeFromWatchlist(movie.value.id)
}
</script>

<style scoped>
.detail-page {
  padding: 50px;
  min-height: 100vh;
  background: #000;
  color: #fff;
}

.hero {
  position: relative;
  height: 85vh;
  overflow: hidden;
}

.hero-video {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 100%;
  transform: translate(-50%, -50%);
  pointer-events: none;
  object-fit: cover;
}

.close-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 20;
  background: rgba(0,0,0,0.6);
  border: none;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  color: #fff;
  font-size: 28px;
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(255,255,255,0.2);
  transform: scale(1.1);
}

.hero-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 60px;
  background: linear-gradient(transparent, rgba(0,0,0,0.9));
  transition: opacity 0.3s;
}

.hero-overlay.hidden {
  opacity: 0;
  pointer-events: none;
}

.hero-content {
  max-width: 800px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.poster {
  width: 120px;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.5);
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  margin: 0;
}

.hero-meta {
  display: flex;
  gap: 16px;
  color: #ccc;
  font-size: 16px;
}

.hero-overview {
  font-size: 18px;
  line-height: 1.6;
  color: #ddd;
  max-width: 700px;
}

/* 버튼 묶음 */
.action-group {
  position: absolute;
  bottom: 40px;
  right: 40px;
  display: flex;
  gap: 16px;
  z-index: 10;
}

.action-btn {
  padding: 14px 28px;
  background: rgba(255,255,255,0.9);
  color: #000;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 700;
  font-size: 16px;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #fff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255,255,255,0.3);
}

.btn-write {
  padding: 14px 28px;
  background: #7dd3fc;
  color: #000;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 700;
  font-size: 16px;
  transition: all 0.2s;
}

.watchlist-btn {
  padding: 14px 28px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 700;
  font-size: 16px;
  transition: all 0.2s;
}

.watchlist-btn.added {
  background: rgba(76,175,80,0.9);
  color: #fff;
}

.watchlist-btn.added:hover {
  background: rgba(76,175,80,1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76,175,80,0.4);
}

/* 리뷰 섹션 스타일 */
.reviews-section {
  background: #111;
  padding: 60px 20px;
  min-height: 400px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.1);
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.loading,
.no-reviews {
  text-align: center;
  padding: 60px 20px;
  color: #999;
  font-size: 16px;
}

.no-reviews p {
  margin-bottom: 20px;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.review-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.review-card:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  border-color: rgba(255, 255, 255, 0.2);
}

.review-card:hover .click-hint {
  opacity: 1;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  font-weight: 600;
  font-size: 16px;
  color: #fff;
}

.rating {
  font-size: 18px;
  color: #ffd700;
}

.time {
  font-size: 14px;
  color: #999;
}

.review-content {
  font-size: 15px;
  line-height: 1.6;
  color: #ddd;
  margin: 0 0 12px 0;
  white-space: pre-wrap;
  /* 최대 3줄까지만 표시 */
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.click-hint {
  font-size: 13px;
  color: #0066cc;
  font-weight: 600;
  opacity: 0;
  transition: opacity 0.3s;
  text-align: right;
  margin-top: 8px;
}

@media (max-width: 768px) {
  .hero-overlay {
    padding: 30px;
  }

  .hero-title {
    font-size: 32px;
  }

  .hero-overview {
    font-size: 14px;
  }

  .action-group {
    bottom: 100px;
    right: 30px;
    flex-direction: column;
  }

  .action-btn,
  .watchlist-btn {
    padding: 12px 20px;
    font-size: 14px;
  }

  .reviews-section {
    padding: 40px 15px;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .section-title {
    font-size: 24px;
  }

  .review-card {
    padding: 20px;
  }

  .review-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .click-hint {
    opacity: 1;
  }
}
</style>
<template>
  <div class="watchlist-page">
    <div class="container">
      <div class="page-header">
        <h2>나중에 볼 영화 ({{ watchlistStore.watchlistCount }})</h2>
        <button 
          v-if="watchlistStore.watchlistCount > 0" 
          @click="clearAll" 
          class="btn-clear"
        >
          전체 삭제
        </button>
      </div>

      <div v-if="watchlistStore.watchlistCount === 0" class="empty-state">
        <p>나중에 볼 영화가 없습니다.</p>
        <router-link to="/movies" class="btn-browse">영화 둘러보기</router-link>
      </div>

      <!-- 멀티 캐러셀 슬라이더 -->
      <div v-else class="carousel-container">
        <button 
          @click="prevSlide" 
          class="carousel-btn carousel-btn-prev"
          :disabled="currentIndex === 0"
        >
          ‹
        </button>

        <div class="carousel-viewport">
          <div 
            class="carousel-track"
            :style="{ 
              transform: transformValue,
              gap: `${cardGap}px`,
              padding: centerPadding
            }"
          >
            <div 
              v-for="(movie, index) in watchlistStore.watchlist" 
              :key="movie.id" 
              class="carousel-card"
              :class="getCardClass(index)"
              :style="{ width: `${cardWidth}px` }"
            >
              <router-link :to="`/movies/${movie.id}`" class="movie-link">
                <img 
                  :src="`https://image.tmdb.org/t/p/w500${movie.poster_path}`" 
                  :alt="movie.title"
                  class="poster"
                />
                <div class="movie-info">
                  <h3>{{ movie.title }}</h3>
                  <p class="rating">⭐ {{ movie.vote_average }}</p>
                  <p class="date">{{ movie.release_date }}</p>
                </div>
              </router-link>
              <button 
                @click.prevent="removeMovie(movie.id)" 
                class="btn-remove"
              >
                ✕
              </button>
            </div>
          </div>
        </div>

        <button 
          @click="nextSlide" 
          class="carousel-btn carousel-btn-next"
          :disabled="currentIndex >= watchlistStore.watchlistCount - 1"
        >
          ›
        </button>

        <!-- 인디케이터 -->
        <div class="carousel-indicators">
          <button
            v-for="(movie, index) in watchlistStore.watchlist"
            :key="index"
            @click="goToSlide(index)"
            class="indicator"
            :class="{ active: index === currentIndex }"
          ></button>
        </div>
      </div>

      <!-- AI DNA 분석 및 추천 섹션 -->
      <div v-if="watchlistStore.watchlistCount > 0" class="ai-recommendations">
        <div class="section-header">
          <h2>
            <span class="ai-badge">🧬 AI</span>
            영화 DNA 분석 & 추천
          </h2>
          <button 
            @click="getAIRecommendations" 
            :disabled="loadingRecommendations"
            class="btn-recommend"
          >
            {{ loadingRecommendations ? '분석 중...' : '🧬 DNA 분석 시작' }}
          </button>
        </div>

        <!-- 로딩 -->
        <div v-if="loadingRecommendations" class="loading-state">
          <div class="spinner"></div>
          <p>AI가 당신의 영화 DNA를 분석하고 있습니다...</p>
        </div>

        <!-- DNA 분석 결과 -->
        <div v-else-if="dnaAnalysis" class="dna-analysis-container">
          <div class="dna-card">
            <h3 class="dna-title">🧬 당신의 영화 DNA</h3>
            
            <!-- 레이더 차트 추가 -->
            <div class="radar-chart-container">
              <svg :width="radarSize" :height="radarSize" class="radar-chart">
                <!-- 배경 격자 -->
                <g v-for="level in 5" :key="level" class="grid-level">
                  <polygon
                    :points="getPolygonPoints(level / 5)"
                    fill="none"
                    :stroke="'rgba(255, 255, 255, ' + (0.1 - level * 0.01) + ')'"
                    stroke-width="1"
                  />
                </g>

                <!-- 축 선 -->
                <g v-for="(axis, index) in radarAxes" :key="index" class="axis-line">
                  <line
                    :x1="radarCenter"
                    :y1="radarCenter"
                    :x2="getAxisPoint(index, 1).x"
                    :y2="getAxisPoint(index, 1).y"
                    stroke="rgba(255, 255, 255, 0.2)"
                    stroke-width="1"
                  />
                  <text
                    :x="getAxisPoint(index, 1.2).x"
                    :y="getAxisPoint(index, 1.2).y"
                    text-anchor="middle"
                    dominant-baseline="middle"
                    fill="#fff"
                    font-size="13"
                    font-weight="600"
                  >
                    {{ axis.label }}
                  </text>
                </g>

                <!-- 데이터 영역 -->
                <polygon
                  :points="getDataPoints()"
                  fill="url(#radarGradient)"
                  stroke="#3b82f6"
                  stroke-width="3"
                  opacity="0.7"
                />

                <!-- 데이터 포인트 -->
                <circle
                  v-for="(point, index) in getDataPointsArray()"
                  :key="index"
                  :cx="point.x"
                  :cy="point.y"
                  r="6"
                  fill="#3b82f6"
                  stroke="#fff"
                  stroke-width="2"
                />

                <!-- 그라디언트 정의 -->
                <defs>
                  <linearGradient id="radarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:0.6" />
                    <stop offset="100%" style="stop-color:#9333ea;stop-opacity:0.6" />
                  </linearGradient>
                </defs>
              </svg>
            </div>

            <div class="dna-section">
              <h4>선호 장르</h4>
              <div class="genre-tags">
                <span 
                  v-for="(genre, index) in dnaAnalysis.genres" 
                  :key="index"
                  class="genre-tag"
                >
                  {{ genre }}
                </span>
              </div>
            </div>

            <div class="dna-section">
              <h4>반복되는 테마</h4>
              <div class="theme-tags">
                <span 
                  v-for="(theme, index) in dnaAnalysis.themes" 
                  :key="index"
                  class="theme-tag"
                >
                  {{ theme }}
                </span>
              </div>
            </div>

            <div class="dna-section">
              <h4>선호하는 분위기</h4>
              <p class="mood-text">{{ dnaAnalysis.mood }}</p>
            </div>

            <div class="dna-section">
              <h4>감독 스타일</h4>
              <p class="director-text">{{ dnaAnalysis.director_style }}</p>
            </div>
          </div>

          <!-- 추천 영화 -->
          <div v-if="recommendations.length > 0" class="recommendations-container">
            <div class="recommendation-header">
              <h3>✨ DNA 기반 추천 영화</h3>
              <p class="explanation">{{ aiExplanation }}</p>
            </div>
            
            <div class="recommendations-grid">
              <div 
                v-for="movie in recommendations" 
                :key="movie.id"
                class="recommendation-card"
                @click="goToMovie(movie.id)"
              >
                <img 
                  v-if="movie.poster_path"
                  :src="`https://image.tmdb.org/t/p/w500${movie.poster_path}`" 
                  :alt="movie.title"
                  class="poster"
                />
                <div v-else class="poster-placeholder">
                  <span>🎬</span>
                </div>
                <div class="movie-info">
                  <h3>{{ movie.title }}</h3>
                  <p class="rating" v-if="movie.vote_average">⭐ {{ movie.vote_average?.toFixed(1) }}</p>
                  <p class="reason">{{ movie.reason }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 초기 상태 -->
        <div v-else class="ai-prompt">
          <div class="prompt-icon">🧬</div>
          <p class="prompt-title">당신의 영화 DNA를 분석해보세요</p>
          <p class="prompt-text">찜한 영화를 바탕으로 AI가 취향을 분석하고<br>맞춤 영화를 추천해드립니다</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWatchlistStore } from '@/stores/watchlist'
import axios from 'axios'

const router = useRouter()
const watchlistStore = useWatchlistStore()
const TMDB_API_KEY = import.meta.env.VITE_TMDB_API_KEY
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const recommendations = ref([])
const loadingRecommendations = ref(false)
const aiExplanation = ref('')
const dnaAnalysis = ref(null)

// 레이더 차트 설정
const radarSize = ref(400)
const radarCenter = computed(() => radarSize.value / 2)
const radarRadius = computed(() => radarSize.value / 2 - 80)

// 레이더 차트 축 (6각형)
const radarAxes = ref([
  { label: '감정 몰입', key: 'emotional', value: 0 },
  { label: '철학적 호기심', key: 'intellectual', value: 0 },
  { label: '긴장/자극', key: 'thrill', value: 0 },
  { label: '유머/재미', key: 'humor', value: 0 },
  { label: '로맨스/감성', key: 'romance', value: 0 },
  { label: '창의적 상상', key: 'imagination', value: 0 }
])

// 레이더 차트 함수들
const getAngle = (index) => {
  return (Math.PI * 2 * index) / radarAxes.value.length - Math.PI / 2
}

const getAxisPoint = (index, scale) => {
  const angle = getAngle(index)
  return {
    x: radarCenter.value + Math.cos(angle) * radarRadius.value * scale,
    y: radarCenter.value + Math.sin(angle) * radarRadius.value * scale
  }
}

const getPolygonPoints = (scale) => {
  return radarAxes.value
    .map((_, index) => {
      const point = getAxisPoint(index, scale)
      return `${point.x},${point.y}`
    })
    .join(' ')
}

const getDataPoints = () => {
  return radarAxes.value
    .map((axis, index) => {
      const point = getAxisPoint(index, axis.value)
      return `${point.x},${point.y}`
    })
    .join(' ')
}

const getDataPointsArray = () => {
  return radarAxes.value.map((axis, index) => getAxisPoint(index, axis.value))
}

// 장르 분석 함수
const analyzeGenres = () => {
  const scores = {
    emotional: 0,      // 감정 몰입
    intellectual: 0,   // 철학적 호기심
    thrill: 0,         // 긴장/자극
    humor: 0,          // 유머/재미
    romance: 0,        // 로맨스/감성
    imagination: 0     // 창의적 상상
  }

  if (!dnaAnalysis.value?.genres) return

  const genres = dnaAnalysis.value.genres.map(g => g.toLowerCase())
  const themes = dnaAnalysis.value.themes?.map(t => t.toLowerCase()) || []
  const mood = dnaAnalysis.value.mood?.toLowerCase() || ''
  const directorStyle = dnaAnalysis.value.director_style?.toLowerCase() || ''

  // 장르 기반 분석
  genres.forEach(genre => {
    // 감정 몰입
    if (genre.includes('드라마') || genre.includes('drama') || 
        genre.includes('멜로') || genre.includes('가족')) {
      scores.emotional += 0.35
    }
    
    // 철학적 호기심
    if (genre.includes('스릴러') || genre.includes('thriller') || 
        genre.includes('미스터리') || genre.includes('범죄') ||
        genre.includes('다큐') || genre.includes('전기')) {
      scores.intellectual += 0.35
    }
    
    // 긴장/자극
    if (genre.includes('액션') || genre.includes('action') ||
        genre.includes('공포') || genre.includes('horror') ||
        genre.includes('서스펜스') || genre.includes('스릴러')) {
      scores.thrill += 0.35
    }
    
    // 유머/재미
    if (genre.includes('코미디') || genre.includes('comedy') ||
        genre.includes('애니메이션')) {
      scores.humor += 0.35
    }
    
    // 로맨스/감성
    if (genre.includes('로맨스') || genre.includes('romance') ||
        genre.includes('멜로') || genre.includes('사랑')) {
      scores.romance += 0.35
    }
    
    // 창의적 상상
    if (genre.includes('sf') || genre.includes('공상') || 
        genre.includes('판타지') || genre.includes('fantasy') ||
        genre.includes('애니메이션') || genre.includes('모험')) {
      scores.imagination += 0.35
    }
  })

  // 테마 기반 분석
  themes.forEach(theme => {
    // 감정 몰입
    if (theme.includes('감동') || theme.includes('눈물') || 
        theme.includes('가족') || theme.includes('우정') ||
        theme.includes('성장') || theme.includes('인생')) {
      scores.emotional += 0.25
    }
    
    // 철학적 호기심
    if (theme.includes('사회') || theme.includes('정치') ||
        theme.includes('철학') || theme.includes('진실') ||
        theme.includes('정체성') || theme.includes('도덕') ||
        theme.includes('미스터리') || theme.includes('비밀')) {
      scores.intellectual += 0.25
    }
    
    // 긴장/자극
    if (theme.includes('긴장') || theme.includes('추격') ||
        theme.includes('서스펜스') || theme.includes('전투') ||
        theme.includes('위험') || theme.includes('생존') ||
        theme.includes('복수')) {
      scores.thrill += 0.25
    }
    
    // 유머/재미
    if (theme.includes('유머') || theme.includes('웃음') ||
        theme.includes('재미') || theme.includes('코믹') ||
        theme.includes('풍자') || theme.includes('유쾌')) {
      scores.humor += 0.25
    }
    
    // 로맨스/감성
    if (theme.includes('사랑') || theme.includes('관계') ||
        theme.includes('이별') || theme.includes('만남') ||
        theme.includes('연애') || theme.includes('감성')) {
      scores.romance += 0.25
    }
    
    // 창의적 상상
    if (theme.includes('미래') || theme.includes('과거') ||
        theme.includes('마법') || theme.includes('초능력') ||
        theme.includes('외계') || theme.includes('시간여행') ||
        theme.includes('상상') || theme.includes('환상')) {
      scores.imagination += 0.25
    }
  })

  // 분위기 기반 분석
  if (mood.includes('감동') || mood.includes('따뜻') || mood.includes('진지')) {
    scores.emotional += 0.2
  }
  if (mood.includes('생각') || mood.includes('복잡') || mood.includes('깊이')) {
    scores.intellectual += 0.2
  }
  if (mood.includes('긴장') || mood.includes('스릴') || mood.includes('강렬')) {
    scores.thrill += 0.2
  }
  if (mood.includes('유쾌') || mood.includes('밝은') || mood.includes('즐거운')) {
    scores.humor += 0.2
  }
  if (mood.includes('로맨틱') || mood.includes('감성') || mood.includes('애틋')) {
    scores.romance += 0.2
  }
  if (mood.includes('환상') || mood.includes('몽환') || mood.includes('독특')) {
    scores.imagination += 0.2
  }

  // 감독 스타일 기반 분석
  if (directorStyle.includes('감정') || directorStyle.includes('섬세')) {
    scores.emotional += 0.15
  }
  if (directorStyle.includes('철학') || directorStyle.includes('메시지') || 
      directorStyle.includes('주제')) {
    scores.intellectual += 0.15
  }
  if (directorStyle.includes('액션') || directorStyle.includes('박진감')) {
    scores.thrill += 0.15
  }
  if (directorStyle.includes('유머') || directorStyle.includes('위트')) {
    scores.humor += 0.15
  }
  if (directorStyle.includes('감성') || directorStyle.includes('낭만')) {
    scores.romance += 0.15
  }
  if (directorStyle.includes('독창') || directorStyle.includes('상상력') || 
      directorStyle.includes('시각')) {
    scores.imagination += 0.15
  }

  // 정규화 (최대값을 1로)
  const maxScore = Math.max(...Object.values(scores), 0.1)
  Object.keys(scores).forEach(key => {
    scores[key] = Math.min(scores[key] / maxScore, 1)
  })

  // 최소값 보정 (너무 작은 값은 0.2로)
  Object.keys(scores).forEach(key => {
    if (scores[key] > 0 && scores[key] < 0.2) {
      scores[key] = 0.2
    }
  })

  radarAxes.value = [
    { label: '감정 몰입', key: 'emotional', value: scores.emotional || 0.3 },
    { label: '철학적 호기심', key: 'intellectual', value: scores.intellectual || 0.3 },
    { label: '긴장/자극', key: 'thrill', value: scores.thrill || 0.3 },
    { label: '유머/재미', key: 'humor', value: scores.humor || 0.3 },
    { label: '로맨스/감성', key: 'romance', value: scores.romance || 0.3 },
    { label: '창의적 상상', key: 'imagination', value: scores.imagination || 0.3 }
  ]
}

// 캐러셀 관련
const currentIndex = ref(0)
const cardWidth = ref(300)
const cardGap = ref(30)

const updateCardWidth = () => {
  const screenWidth = window.innerWidth
  
  if (screenWidth >= 1920) {
    cardWidth.value = 380
    cardGap.value = 40
    radarSize.value = 500
  } else if (screenWidth >= 1600) {
    cardWidth.value = 340
    cardGap.value = 35
    radarSize.value = 450
  } else if (screenWidth >= 1200) {
    cardWidth.value = 300
    cardGap.value = 30
    radarSize.value = 420
  } else if (screenWidth >= 768) {
    cardWidth.value = 260
    cardGap.value = 25
    radarSize.value = 380
  } else {
    cardWidth.value = 220
    cardGap.value = 20
    radarSize.value = 320
  }
}

const centerPadding = computed(() => {
  return `0 calc(50% - ${cardWidth.value / 2}px)`
})

const transformValue = computed(() => {
  return `translateX(-${currentIndex.value * (cardWidth.value + cardGap.value)}px)`
})

onMounted(() => {
  updateCardWidth()
  window.addEventListener('resize', updateCardWidth)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateCardWidth)
})

const getCardClass = (index) => {
  const diff = index - currentIndex.value
  if (diff === 0) return 'center'
  if (diff === -1 || diff === 1) return 'side'
  if (diff === -2 || diff === 2) return 'far'
  return 'hidden'
}

const prevSlide = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

const nextSlide = () => {
  if (currentIndex.value < watchlistStore.watchlistCount - 1) {
    currentIndex.value++
  }
}

const goToSlide = (index) => {
  currentIndex.value = index
}

const removeMovie = (movieId) => {
  if (confirm('이 영화를 목록에서 제거하시겠습니까?')) {
    watchlistStore.removeFromWatchlist(movieId)
    if (currentIndex.value >= watchlistStore.watchlistCount) {
      currentIndex.value = Math.max(0, watchlistStore.watchlistCount - 1)
    }
  }
}

const clearAll = () => {
  if (confirm('전체 목록을 삭제하시겠습니까?')) {
    watchlistStore.clearWatchlist()
    currentIndex.value = 0
    dnaAnalysis.value = null
    recommendations.value = []
  }
}

const goToMovie = (movieId) => {
  router.push(`/movies/${movieId}`)
}

// AI DNA 분석 및 추천
const getAIRecommendations = async () => {
  loadingRecommendations.value = true
  recommendations.value = []
  aiExplanation.value = ''
  dnaAnalysis.value = null

  try {
    const watchlistMovies = watchlistStore.watchlist
    const movieTitles = watchlistMovies.map(m => m.title)

    const token = localStorage.getItem('token')
    const response = await axios.post(
      `${API_URL}/api/accounts/ai-recommendations/`,
      {
        movie_titles: movieTitles
      },
      {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        }
      }
    )

    const aiResponse = response.data
    
    // DNA 분석 결과 저장
    dnaAnalysis.value = aiResponse.dna_analysis
    aiExplanation.value = aiResponse.explanation

    // 레이더 차트 데이터 생성
    analyzeGenres()

    // 영화 추천 데이터 처리
    const moviePromises = aiResponse.movies.map(async (movie) => {
      try {
        const searchResponse = await axios.get(
          `https://api.themoviedb.org/3/search/movie`,
          {
            params: {
              api_key: TMDB_API_KEY,
              query: movie.title,
              language: 'ko-KR'
            }
          }
        )

        if (searchResponse.data.results.length > 0) {
          const tmdbMovie = searchResponse.data.results[0]
          return {
            id: tmdbMovie.id,
            title: tmdbMovie.title,
            poster_path: tmdbMovie.poster_path,
            vote_average: tmdbMovie.vote_average,
            reason: movie.reason
          }
        }
        return null
      } catch (error) {
        console.error(`영화 검색 실패: ${movie.title}`, error)
        return null
      }
    })

    const movieResults = await Promise.all(moviePromises)
    recommendations.value = movieResults.filter(m => m !== null)

  } catch (error) {
    console.error('AI 추천 실패:', error)
    if (error.response?.status === 401) {
      alert('로그인이 필요합니다.')
    } else {
      alert('추천을 받는 중 오류가 발생했습니다.')
    }
  } finally {
    loadingRecommendations.value = false
  }
}
</script>

<style scoped>
.watchlist-page {
  padding: 102px 40px 20px;
  min-height: 100vh;
  background-color: #111;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 50px;
  padding-bottom: 15px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.1);
}

.page-header h2 {
  font-size: 28px;
  color: #fff;
  font-weight: 700;
}

.btn-clear {
  padding: 10px 20px;
  background-color: #ff6b6b;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-clear:hover {
  background-color: #ff5252;
  transform: translateY(-2px);
}

.empty-state {
  text-align: center;
  padding: 100px 20px;
}

.empty-state p {
  font-size: 18px;
  color: #999;
  margin-bottom: 20px;
}

.btn-browse {
  display: inline-block;
  padding: 12px 24px;
  background-color: #0066cc;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-browse:hover {
  background-color: #0052a3;
  transform: translateY(-2px);
}

/* 캐러셀 */
.carousel-container {
  position: relative;
  margin-bottom: 80px;
  padding: 40px 0 50px 0;
  max-width: 100%;
}

.carousel-viewport {
  overflow: hidden;
  padding: 60px 0;
}

.carousel-track {
  display: flex;
  transition: transform 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.carousel-card {
  flex-shrink: 0;
  transition: all 0.6s ease;
  position: relative;
}

.carousel-card.center {
  opacity: 1;
  transform: scale(1.08);
  filter: blur(0);
  z-index: 3;
}

.carousel-card.side {
  opacity: 0.6;
  transform: scale(0.95);
  filter: blur(1px);
  z-index: 2;
}

.carousel-card.far {
  opacity: 0.3;
  transform: scale(0.85);
  filter: blur(2px);
  z-index: 1;
}

.carousel-card.hidden {
  opacity: 0;
  transform: scale(0.7);
  filter: blur(3px);
  pointer-events: none;
}

.carousel-card .movie-link {
  display: block;
  width: 100%;
  text-decoration: none;
  color: inherit;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
}

.carousel-card.center .movie-link {
  box-shadow: 0 20px 80px rgba(0, 0, 0, 0.8);
}

.poster {
  width: 100%;
  aspect-ratio: 2/3;
  object-fit: cover;
}

.movie-info {
  padding: 20px;
  background: linear-gradient(to top, rgba(71, 71, 71, 0.9), transparent);
}

.movie-info h3 {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rating {
  font-size: 15px;
  color: #ffd700;
  margin-bottom: 6px;
}

.date {
  font-size: 13px;
  color: #999;
}

.btn-remove {
  position: absolute;
  top: 13px;
  right: 12px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 700;
  transition: all 0.2s;
  z-index: 10;
}

.btn-remove:hover {
  background-color: rgba(255, 0, 0, 0.8);
}

.carousel-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 60px;
  height: 60px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(10px);
  border: rgba(0, 0, 0, 0.2);
  border-radius: 50%;
  color: white;
  font-size: 45px;
  cursor: pointer;
  transition: all 0.3s;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}

.carousel-btn:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.8);
  transform: translateY(-50%) scale(1.1);
}

.carousel-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.carousel-btn-prev {
  left: 40px;
}

.carousel-btn-next {
  right: 40px;
}

.carousel-indicators {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 100px;
}

.indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  border: none;
  cursor: pointer;
  transition: all 0.3s;
}

.indicator:hover {
  background: rgba(255, 255, 255, 0.5);
}

.indicator.active {
  background: linear-gradient(135deg, #3b82f6, #9333ea);
  width: 30px;
  border-radius: 5px;
}

/* AI 추천 섹션 */
.ai-recommendations {
  margin-top: 60px;
  padding: 40px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(147, 51, 234, 0.1));
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.section-header h2 {
  font-size: 24px;
  color: #fff;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-badge {
  display: inline-block;
  padding: 6px 12px;
  background: linear-gradient(135deg, #3b82f6, #9333ea);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
}

.btn-recommend {
  padding: 12px 24px;
  background: linear-gradient(135deg, #3b82f6, #9333ea);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 15px;
  transition: all 0.3s;
}

.btn-recommend:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(59, 130, 246, 0.4);
}

.btn-recommend:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 로딩 */
.loading-state {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-state p {
  color: #999;
  font-size: 16px;
}

/* DNA 분석 결과 */
.dna-analysis-container {
  margin-top: 30px;
}

.dna-card {
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(59, 130, 246, 0.3);
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 40px;
}

.dna-title {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 32px;
  text-align: center;
}

/* 레이더 차트 */
.radar-chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 40px;
  padding: 20px;
}

.radar-chart {
  filter: drop-shadow(0 0 20px rgba(59, 130, 246, 0.3));
}

.dna-section {
  margin-bottom: 24px;
}

.dna-section h4 {
  font-size: 16px;
  color: #7dd3fc;
  margin-bottom: 12px;
  font-weight: 600;
}

.genre-tags,
.theme-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.genre-tag {
  padding: 8px 16px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.theme-tag {
  padding: 8px 16px;
  background: linear-gradient(135deg, #9333ea, #7e22ce);
  color: white;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.mood-text,
.director-text {
  color: #ddd;
  font-size: 15px;
  line-height: 1.6;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border-left: 4px solid #3b82f6;
}

/* 추천 영화 */
.recommendations-container {
  margin-top: 40px;
}

.recommendation-header {
  margin-bottom: 24px;
}

.recommendation-header h3 {
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 12px;
}

.explanation {
  color: #aaa;
  font-size: 15px;
  line-height: 1.5;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 24px;
}

.recommendation-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s;
  cursor: pointer;
  border: 2px solid transparent;
}

.recommendation-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);
  border-color: #3b82f6;
}

.poster-placeholder {
  width: 100%;
  aspect-ratio: 2/3;
  background: linear-gradient(135deg, #1e293b, #334155);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
}

.reason {
  font-size: 13px;
  color: #aaa;
  margin-top: 8px;
  line-height: 1.4;
}

/* 초기 상태 */
.ai-prompt {
  text-align: center;
  padding: 80px 20px;
}

.prompt-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.prompt-title {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 12px;
}

.prompt-text {
  font-size: 16px;
  color: #999;
  line-height: 1.6;
}

/* 반응형 */
@media (max-width: 768px) {
  .watchlist-page {
    padding: 102px 20px 20px;
  }

  .section-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .btn-recommend {
    width: 100%;
  }

  .dna-card {
    padding: 24px;
  }

  .radar-chart-container {
    padding: 10px;
  }

  .recommendations-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}
</style>
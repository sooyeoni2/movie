<template>
  <div class="community-page">
    <div class="container">
      <h1 class="page-title">Community</h1>

      <!-- 영화 검색 -->
      <div class="search-section">
        <h2>영화 검색</h2>
        <div class="search-box">
          <input 
            v-model="searchQuery" 
            @keyup.enter="searchMovies"
            placeholder="영화 제목을 검색하세요"
            class="search-input"
          />
          <button @click="searchMovies" class="search-btn">검색</button>
        </div>

        <!-- 검색 결과 -->
        <div v-if="searchResults.length > 0" class="search-results">
          <div 
            v-for="movie in searchResults" 
            :key="movie.id"
            @click="selectMovie(movie)"
            class="movie-item"
          >
            <img 
              :src="`https://image.tmdb.org/t/p/w92${movie.poster_path}`" 
              :alt="movie.title"
              class="movie-poster"
            />
            <div class="movie-info">
              <h4>{{ movie.title }}</h4>
              <p>{{ movie.release_date }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 리뷰 작성 -->
      <div v-if="selectedMovie" class="review-form-section">
        <h2>{{ selectedMovie.title }}</h2>
        <h3>별점을 선택해주세요</h3>
        <div class="star-rating">
          <span 
            v-for="n in 5" 
            :key="n"
            @click="selectRating(n * 2)"
            class="star"
            :class="{ filled: rating >= n * 2 }"
          >
            ★
          </span>
          <span class="rating-text">{{ rating }}</span>
        </div>

        <textarea 
          v-model="reviewContent"
          placeholder="리뷰를 작성해주세요"
          class="review-textarea"
          rows="4"
        ></textarea>

        <button @click="submitReview" class="submit-btn">등록</button>
      </div>

      <!-- 리뷰 목록 -->
      <div class="reviews-section">
        <div class="reviews-header">
          <h2>리뷰</h2>
          <div class="sort-options">
            <select v-model="sortBy" class="sort-select">
              <option value="latest">최신순</option>
              <option value="recommended">추천순</option>
            </select>
          </div>
        </div>

        <div v-if="reviews.length === 0" class="no-reviews">
          아직 리뷰가 없습니다.
        </div>

        <div
          v-for="review in sortedReviews"
          :key="review.id"
          class="review-card"
        >
          <!-- ✅ 제목 + 별점(오른쪽) : 구조만 변경 -->
          <div class="title-row">
            <h4
              class="movie-title"
              @click="goDetail(review.id)"
              style="cursor: pointer"
            >
              {{ review.movie_title }}
            </h4>

            <div class="inline-rating">
              <span class="stars">
                <span
                  v-for="n in 5"
                  :key="n"
                  class="star small-star"
                  :class="{ filled: review.rating >= n * 2 }"
                >
                  ★
                </span>
              </span>
              <span class="rating-num">{{ review.rating }}</span>
            </div>
          </div>

          <!-- ✅ 기존 헤더(작성자/날짜/삭제) 유지 -->
          <div class="review-header">
            <div class="review-meta">
              <span class="username">{{ review.username }}</span>
              <span class="date">{{ formatDate(review.created_at) }}</span>
            </div>
          </div>

          <!-- 리뷰 내용 -->
          <div class="review-content">
            <p>{{ review.content }}</p>
          </div>

          <!-- 좋아요/싫어요 -->
          <div class="review-actions">
            <div class="left-actions">
              <button 
                @click="toggleLike(review.id, true)"
                class="like-btn"
                :class="{ active: review.user_like_status === 'like' }"
              >
                👍 {{ review.likes }}
              </button>

              <button 
                @click="toggleLike(review.id, false)"
                class="dislike-btn"
                :class="{ active: review.user_like_status === 'dislike' }"
              >
                👎 {{ review.dislikes }}
              </button>
            </div>

            <!-- ✅ 댓글 개수 오른쪽 -->
            <div class="comment-count">
              댓글 {{ review.comments?.length || 0 }}
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import axios from 'axios'

const authStore = useAuthStore()
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const TMDB_API_KEY = import.meta.env.VITE_TMDB_API_KEY

const router = useRouter()

const goDetail = (reviewId) => {
  router.push(`/community/${reviewId}`)
}

const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Token ${token}` } : {}
}

// 검색
const searchQuery = ref('')
const searchResults = ref([])
const selectedMovie = ref(null)

// 리뷰 작성
const rating = ref(10)
const reviewContent = ref('')

// 리뷰 목록
const reviews = ref([])
const sortBy = ref('latest')

// 댓글 (로직 유지)
const commentInputs = ref({})

// 정렬된 리뷰
const sortedReviews = computed(() => {
  const sorted = [...reviews.value]
  if (sortBy.value === 'latest') {
    return sorted.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  } else if (sortBy.value === 'recommended') {
    // 추천순 정렬 로직 (예: likes 수 기준으로 정렬)
    return sorted.sort((a, b) => b.likes - a.likes)
  } else {
    return sorted.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
  }
})


// 영화 검색
const searchMovies = async () => {
  if (!searchQuery.value.trim()) return
  
  try {
    const response = await axios.get(
      `https://api.themoviedb.org/3/search/movie?api_key=${TMDB_API_KEY}&language=ko-KR&query=${searchQuery.value}`
    )
    searchResults.value = response.data.results.slice(0, 5)
  } catch (error) {
    console.error('영화 검색 실패:', error)
    alert('영화 검색에 실패했습니다.')
  }
}

// 영화 선택
const selectMovie = (movie) => {
  selectedMovie.value = movie
  searchResults.value = []
  searchQuery.value = ''
}

// 별점 선택
const selectRating = (value) => {
  rating.value = value
}

// 리뷰 제출
const submitReview = async () => {
  if (!reviewContent.value.trim()) {
    alert('감상평을 작성해주세요.')
    return
  }

  try {
    const response = await axios.post(
      `${API_URL}/api/accounts/reviews/`, 
      {
        movie_id: selectedMovie.value.id,
        movie_title: selectedMovie.value.title,
        rating: rating.value,
        content: reviewContent.value
      },
      {
        headers: getAuthHeaders()
      }
    )

    reviews.value.unshift(response.data)
    
    selectedMovie.value = null
    rating.value = 10
    reviewContent.value = ''
    
    alert('리뷰가 등록되었습니다!')
  } catch (error) {
    console.error('리뷰 등록 실패:', error)
    console.error('에러 상세:', error.response?.data)
    alert('리뷰 등록에 실패했습니다.')
  }
}

// 리뷰 삭제
const deleteReview = async (reviewId) => {
  if (!confirm('리뷰를 삭제하시겠습니까?')) return

  try {
    await axios.delete(
      `${API_URL}/api/accounts/reviews/${reviewId}/`,
      { headers: getAuthHeaders() }
    )
    reviews.value = reviews.value.filter(r => r.id !== reviewId)
    alert('리뷰가 삭제되었습니다.')
  } catch (error) {
    console.error('리뷰 삭제 실패:', error)
    alert('리뷰 삭제에 실패했습니다.')
  }
}

// 좋아요/싫어요
const toggleLike = async (reviewId, isLike) => {
  try {
    await axios.post(
      `${API_URL}/api/accounts/reviews/${reviewId}/like/`, 
      { is_like: isLike },
      { headers: getAuthHeaders() }
    )
    await loadReviews()
  } catch (error) {
    console.error('좋아요/싫어요 실패:', error)
  }
}

// 댓글 로직 (유지용, 화면에만 안 보이게 처리했음)
const submitComment = async (reviewId) => {
  const content = commentInputs.value[reviewId]
  if (!content || !content.trim()) return

  try {
    await axios.post(
      `${API_URL}/api/accounts/reviews/${reviewId}/comments/`, 
      { content },
      { headers: getAuthHeaders() }
    )
    commentInputs.value[reviewId] = ''
    await loadReviews()
  } catch (error) {
    console.error('댓글 작성 실패:', error)
  }
}

const deleteComment = async (commentId) => {
  try {
    await axios.delete(
      `${API_URL}/api/accounts/comments/${commentId}/`,
      { headers: getAuthHeaders() }
    )
    await loadReviews()
  } catch (error) {
    console.error('댓글 삭제 실패:', error)
  }
}

// 리뷰 목록 불러오기
const loadReviews = async () => {
  try {
    const headers = authStore.isLoggedIn ? getAuthHeaders() : {}
    const response = await axios.get(
      `${API_URL}/api/accounts/reviews/`,
      { headers }
    )
    reviews.value = response.data
  } catch (error) {
    console.error('리뷰 목록 불러오기 실패:', error)
  }
}

// 날짜 포맷
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}.${month}.${day}. ${hours}:${minutes}`
}

onMounted(() => {
  loadReviews()
})
</script>

<style scoped>
.community-page {
  padding: 102px 40px 40px;
  background: #111;
  min-height: 100vh;
}


.page-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 30px;
  color: #ffffff;
}

.search-section {
  background: rgb(50, 50, 50);
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 24px;
}

.search-section h2 {
  font-size: 20px;
  margin-bottom: 16px;
  color: #fbfbfb;
}

.search-box {
  display: flex;
  gap: 12px;
}

.search-box input:focus {
  outline: 1px solid #7dd3fc;
}

.search-input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.search-btn {
  padding: 12px 22px;
  font-size: 0.95rem;
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

.search-btn:hover {
  background-color: #0052a3;
}

.search-results {
  margin-top: 16px;
}

.movie-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.movie-item:hover {
  background-color: #0f172a;
}

.movie-poster {
  width: 60px;
  height: 90px;
  object-fit: cover;
  border-radius: 4px;
}

.movie-info h4 {
  font-size: 16px;
  margin-bottom: 4px;
  color: #e8e8e8;
}

.movie-info p {
  font-size: 13px;
  color: #a3a3a3;
}

.review-form-section {
  background: #333;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 24px;
}

.review-form-section h2 {
  font-size: 20px;
  margin-bottom: 20px;
  color: #e8e8e8;
}

.review-form-section h3 {
  font-size: 16px;
  margin-bottom: 5px;
  color: #666;
}

.star-rating {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.star {
  font-size: 36px;
  color: #ddd;
  cursor: pointer;
  transition: color 0.2s;
}

.star.filled {
  color: #ffd700;
}

.star:hover {
  color: #ffc107;
}

.rating-text {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.review-textarea {
  width: 100%;
  padding: 12px;
  background: #2a2a2a;
  color: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  margin-bottom: 12px;
}

.submit-btn {
  padding: 12px 24px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.submit-btn:hover {
  background-color: #45a049;
}

.reviews-section {
  margin-top: 24px;
}

.reviews-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.reviews-header h2 {
  font-size: 20px;
  color: #ffffff;
  font-weight: 600;
}

.sort-options {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sort-select {
  padding: 8px 14px;
  font-size: 14px;
  border-radius: 8px;
  background-color: #2a2a2a;
  color: #fff;
  border: 1px solid #ddd;
  cursor: pointer;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.sort-select:focus {
  outline: 1px solid #7dd3fc;
}

.sort-select:hover {
  background-color: #444;
}

.sort-select option {
  background-color: #2a2a2a;
  color: #fff;
}


.no-reviews {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  color: #666;
}

.review-card {
  background: rgb(35, 35, 35);
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 16px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.movie-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 0; /* 라인에서 margin 제거 */
  color: #ffffff;    /* 다크 카드에서 보이도록 */
}

.movie-title:hover {
  text-decoration: underline;
}

/* 별점(제목 오른쪽) - 기존 filled 로직 유지 */
.inline-rating {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.small-star {
  font-size: 18px; /* 제목 옆이니 작게 */
  color: #666;     /* 기본은 어둡게 */
}

.small-star.filled {
  color: #ffd700;
}

.rating-num {
  font-size: 14px;
  font-weight: 600;
  color: #eaeaea; /* 다크 카드용 */
}

/* 기존 메타 스타일은 유지하되, 다크 카드에서 글자만 보이게 */
.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.review-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  font-weight: 600;
  color: #eaeaea; /* 다크 카드용 */
}

.date {
  font-size: 13px;
  color: #bdbdbd; /* 다크 카드용 */
}

.review-content {
  margin-bottom: 16px;
}

.review-content p {
  line-height: 1.6;
  color: #d9d9d9; /* 다크 카드용 */
}

.review-actions {
  display: flex;
  align-items: center;
  justify-content: space-between; /* 좌/우 분리 */
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.left-actions {
  display: flex;
  gap: 12px;
}

.comment-count {
  font-size: 14px;
  color: #cfcfcf;
  white-space: nowrap;
}

.like-btn,
.dislike-btn {
  padding: 8px 16px;
  background-color: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  color: #e0e0e0; /* 다크 카드용 */
}

.like-btn:hover,
.dislike-btn:hover {
  background-color: rgba(255, 255, 255, 0.10);
}

.like-btn.active {
  background-color: rgba(33, 150, 243, 0.15);
  border-color: rgba(33, 150, 243, 0.5);
  color: #90caf9;
}

.dislike-btn.active {
  background-color: rgba(244, 67, 54, 0.15);
  border-color: rgba(244, 67, 54, 0.5);
  color: #ef9a9a;
}

/* ✅ 댓글: 개수만 표시 */
.comments-section {
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.comments-section h5 {
  font-size: 14px;
  margin: 0;
  color: #cfcfcf; /* 다크 카드용 */
}

/* (기존 댓글 관련 스타일은 남겨도 무방하지만, 렌더링이 없으니 영향 없음) */
.comment {
  padding: 12px;
  background-color: #f9f9f9;
  border-radius: 6px;
  margin-bottom: 8px;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.comment-username {
  font-size: 13px;
  font-weight: 600;
  color: #333;
}

.comment-date {
  font-size: 12px;
  color: #999;
}

.comment-delete-btn {
  margin-left: auto;
  padding: 2px 8px;
  background-color: transparent;
  color: #999;
  border: none;
  cursor: pointer;
  font-size: 14px;
}

.comment-delete-btn:hover {
  color: #f44336;
}

.comment-content {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
}

.comment-form {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.comment-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 13px;
}

.comment-btn {
  padding: 8px 16px;
  background-color: #4fa1f4;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
}

.comment-btn:hover {
  background-color: #0052a3;
}
</style>
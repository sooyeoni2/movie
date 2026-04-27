<template>
  <div class="community-detail-page">
    <div class="container">
      <button class="back-btn" @click="$router.push('/community')">
        ← Back
      </button>

      <!-- 로딩 -->
      <div v-if="loading" class="loading">
        로딩 중...
      </div>

      <!-- 리뷰 카드 -->
      <div v-else-if="review" class="review-card">
        <!-- 리뷰 헤더 -->
        <div class="review-header">
          <div class="review-rating">
            <span class="stars">
              <span 
                v-for="n in 5" 
                :key="n" 
                class="star" 
                :class="{ filled: (isEditing ? editRating : review.rating) >= n * 2 }"
              >
                ★
              </span>
            </span>
            <span class="rating-num">{{ isEditing ? editRating : review.rating }}</span>
          </div>
          <div class="review-meta">
            <span class="username">{{ review.username }}</span>
            <span class="date">{{ formatDate(review.created_at) }}</span>
            <div v-if="authStore.currentUser?.username === review.username" class="action-btns">
              <button 
                v-if="!isEditing"
                @click="startEdit"
                class="edit-btn"
              >
                수정
              </button>
              <button 
                @click="deleteReview"
                class="delete-btn"
              >
                삭제
              </button>
            </div>
          </div>
        </div>

        <!-- 수정 모드 -->
        <div v-if="isEditing" class="edit-mode">
          <h4 class="movie-title">{{ review.movie_title }}</h4>
          
          <!-- 평점 선택 -->
          <div class="edit-rating">
            <label>평점 선택</label>
            <div class="star-selector">
              <span
                v-for="n in 5"
                :key="n"
                @click="editRating = n * 2"
                class="star-btn"
                :class="{ active: editRating >= n * 2 }"
              >
                ★
              </span>
            </div>
          </div>

          <!-- 리뷰 내용 수정 -->
          <div class="edit-content">
            <label>리뷰 내용</label>
            <textarea
              v-model="editContent"
              placeholder="리뷰를 작성해주세요"
              rows="6"
            ></textarea>
          </div>

          <!-- 버튼 -->
          <div class="edit-actions">
            <button @click="cancelEdit" class="cancel-btn">취소</button>
            <button @click="saveEdit" class="save-btn">저장</button>
          </div>
        </div>

        <!-- 읽기 모드 -->
        <div v-else class="review-content">
          <h4 class="movie-title">{{ review.movie_title }}</h4>
          <p>{{ review.content }}</p>
        </div>

        <!-- 좋아요/싫어요 -->
        <div class="review-actions" v-if="!isEditing">
          <button 
            @click="toggleLike(true)"
            class="like-btn"
            :class="{ active: review.user_like_status === 'like' }"
          >
            👍 {{ review.likes }}
          </button>
          <button 
            @click="toggleLike(false)"
            class="dislike-btn"
            :class="{ active: review.user_like_status === 'dislike' }"
          >
            👎 {{ review.dislikes }}
          </button>
        </div>

        <!-- 댓글 섹션 -->
        <div class="comments-section" v-if="!isEditing">
          <h5>댓글 {{ review.comments?.length || 0 }}</h5>
          
          <!-- 댓글 목록 -->
          <div v-for="comment in review.comments" :key="comment.id" class="comment">
            <div class="comment-header">
              <span class="comment-username">{{ comment.username }}</span>
              <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
              <button 
                v-if="authStore.currentUser?.username === comment.username"
                @click="deleteComment(comment.id)"
                class="comment-delete-btn"
              >
                삭제
              </button>
            </div>
            <p class="comment-content">{{ comment.content }}</p>
          </div>

          <!-- 댓글 작성 -->
          <div v-if="authStore.isLoggedIn" class="comment-form">
            <input 
              v-model="commentInput"
              @keyup.enter="submitComment"
              placeholder="댓글을 작성해주세요"
              class="comment-input"
            />
            <button @click="submitComment" class="comment-btn">등록</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Token ${token}` } : {}
}

const review = ref(null)
const commentInput = ref('')
const loading = ref(true)

// 수정 모드
const isEditing = ref(false)
const editRating = ref(0)
const editContent = ref('')

// 수정 시작
const startEdit = () => {
  isEditing.value = true
  editRating.value = review.value.rating
  editContent.value = review.value.content
}

// 수정 취소
const cancelEdit = () => {
  isEditing.value = false
  editRating.value = 0
  editContent.value = ''
}

// 수정 저장
const saveEdit = async () => {
  if (!editContent.value.trim()) {
    alert('리뷰 내용을 입력해주세요.')
    return
  }

  try {
    await axios.put(
      `${API_URL}/api/accounts/reviews/${review.value.id}/`,
      {
        rating: editRating.value,
        content: editContent.value,
        movie_id: review.value.movie_id,
        movie_title: review.value.movie_title
      },
      { headers: getAuthHeaders() }
    )
    alert('수정되었습니다.')
    isEditing.value = false
    await loadReview()
  } catch (error) {
    console.error('수정 실패:', error)
    alert('수정에 실패했습니다.')
  }
}

// 리뷰 불러오기
const loadReview = async () => {
  loading.value = true
  try {
    const headers = authStore.isLoggedIn ? getAuthHeaders() : {}
    const res = await axios.get(
      `${API_URL}/api/accounts/reviews/${route.params.id}/`,
      { headers }
    )
    review.value = res.data
  } catch (error) {
    console.error('리뷰 로딩 실패', error)
    alert('존재하지 않는 리뷰입니다.')
    router.push('/community')
  } finally {
    loading.value = false
  }
}

// 리뷰 삭제
const deleteReview = async () => {
  if (!confirm('리뷰를 삭제하시겠습니까?')) return

  try {
    await axios.delete(
      `${API_URL}/api/accounts/reviews/${review.value.id}/`,
      { headers: getAuthHeaders() }
    )
    alert('삭제되었습니다.')
    router.push('/community')
  } catch (error) {
    console.error(error)
    alert('삭제 실패')
  }
}

// 좋아요/싫어요
const toggleLike = async (isLike) => {
  if (!authStore.isLoggedIn) {
    alert('로그인이 필요합니다.')
    router.push('/login')
    return
  }

  try {
    await axios.post(
      `${API_URL}/api/accounts/reviews/${review.value.id}/like/`,
      { is_like: isLike },
      { headers: getAuthHeaders() }
    )
    await loadReview()
  } catch (error) {
    console.error(error)
  }
}

// 댓글 작성
const submitComment = async () => {
  if (!authStore.isLoggedIn) {
    alert('로그인이 필요합니다.')
    router.push('/login')
    return
  }

  if (!commentInput.value.trim()) {
    alert('댓글을 작성해주세요.')
    return
  }

  try {
    await axios.post(
      `${API_URL}/api/accounts/reviews/${review.value.id}/comments/`,
      { content: commentInput.value },
      { headers: getAuthHeaders() }
    )
    commentInput.value = ''
    await loadReview()
  } catch (error) {
    console.error(error)
    alert('댓글 작성 실패')
  }
}

// 댓글 삭제
const deleteComment = async (commentId) => {
  if (!confirm('댓글을 삭제하시겠습니까?')) return

  try {
    await axios.delete(
      `${API_URL}/api/accounts/comments/${commentId}/`,
      { headers: getAuthHeaders() }
    )
    await loadReview()
  } catch (error) {
    console.error(error)
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

onMounted(loadReview)
</script>

<style scoped>
.community-detail-page {
  padding: 102px 40px 40px;
  min-height: 100vh;
  background-color: #111;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
}

.back-btn {
  margin-bottom: 24px;
  padding: 10px 20px;
  background: rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.2);
  border-radius: 6px;
  color: #7dd3fc;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.loading {
  text-align: center;
  padding: 100px 20px;
  background: white;
  border-radius: 12px;
  color: #666;
}

/* 리뷰 카드 */
.review-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 16px;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.review-rating {
  display: flex;
  align-items: center;
  gap: 8px;
}

.review-rating .star {
  font-size: 20px;
  color: #ddd;
}

.review-rating .star.filled {
  color: #ffd700;
}

.rating-num {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.review-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  font-weight: 600;
  color: #333;
}

.date {
  font-size: 13px;
  color: #999;
}

.action-btns {
  display: flex;
  gap: 8px;
}

.edit-btn,
.delete-btn {
  padding: 4px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.2s;
}

.edit-btn {
  background-color: #4fa1f4;
  color: white;
}

.edit-btn:hover {
  background-color: #0052a3;
}

.delete-btn {
  background-color: #f44336;
  color: white;
}

.delete-btn:hover {
  background-color: #d32f2f;
}

/* 수정 모드 */
.edit-mode {
  margin-top: 16px;
}

.movie-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #333;
}

.edit-rating {
  margin-bottom: 20px;
}

.edit-rating label,
.edit-content label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.star-selector {
  display: flex;
  gap: 4px;
}

.star-btn {
  font-size: 28px;
  color: #ddd;
  cursor: pointer;
  transition: all 0.2s;
}

.star-btn:hover,
.star-btn.active {
  color: #ffd700;
  transform: scale(1.1);
}

.edit-content textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  line-height: 1.6;
  font-family: inherit;
  resize: vertical;
}

.edit-content textarea:focus {
  outline: none;
  border-color: #4fa1f4;
}

.edit-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-top: 16px;
}

.cancel-btn,
.save-btn {
  padding: 8px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}

.cancel-btn {
  background-color: #f5f5f5;
  color: #666;
}

.cancel-btn:hover {
  background-color: #e9e9e9;
}

.save-btn {
  background-color: #4fa1f4;
  color: white;
}

.save-btn:hover {
  background-color: #0052a3;
}

/* 읽기 모드 */
.review-content {
  margin-bottom: 16px;
}

.review-content p {
  line-height: 1.6;
  color: #666;
}

.review-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.like-btn,
.dislike-btn {
  padding: 8px 16px;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.like-btn:hover,
.dislike-btn:hover {
  background-color: #e9e9e9;
}

.like-btn.active {
  background-color: #e3f2fd;
  border-color: #2196f3;
  color: #2196f3;
}

.dislike-btn.active {
  background-color: #ffebee;
  border-color: #f44336;
  color: #f44336;
}

.comments-section {
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.comments-section h5 {
  font-size: 14px;
  margin-bottom: 12px;
  color: #666;
}

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

@media (max-width: 768px) {
  .community-detail-page {
    padding: 102px 20px 20px;
  }

  .review-meta {
    flex-wrap: wrap;
  }

  .action-btns {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
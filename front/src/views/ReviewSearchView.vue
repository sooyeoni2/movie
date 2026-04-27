<template>
  <div class="wrapper">
    
    <!-- 검색 영역 -->
    <div class="search-section">
      <h1 class="page-title">Search Review</h1>
      
      <!-- 영화 검색 제목 -->
      
      
      <!-- 검색창 -->
      <div class="search-container">
        <input
          v-model="query"
          @keyup.enter="searchReview"
          placeholder="리뷰가 궁금한 영화 제목을 입력하세요"
        />
        <button class="btn-primary" @click="searchReview">
          검색
        </button>
      </div>
    </div>

    <!-- 검색 결과 -->
    <div class="review-grid">
      <div
        v-for="item in results"
        :key="item.id.videoId"
        class="review-card"
        @click="openModal(item.id.videoId)"
      >
        <div class="thumbnail-wrapper">
          <img
            :src="item.snippet.thumbnails.medium.url"
            class="thumbnail"
          />
          <div class="play-overlay">▶</div>
        </div>

        <div class="review-info">
          <h3 class="review-title">
            {{ item.snippet.title }}
          </h3>
          <p class="channel-name">
            {{ item.snippet.channelTitle }}
          </p>
        </div>
      </div>
    </div>

    <!-- 모달 -->
    <div
      v-if="showModal"
      class="modal-overlay"
      @click.self="closeModal"
    >
      <div class="modal-content">
        <div class="video-container">
          <iframe
            :src="embedUrl"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
          ></iframe>
        </div>
        <button class="close-btn" @click="closeModal">
          닫기
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from "axios";
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

const query = ref("");
const results = ref([]);
const showModal = ref(false);
const embedUrl = ref("");

const youtubeKey = import.meta.env.VITE_YOUTUBE_API_KEY;

const searchReview = async () => {
  if (!query.value.trim()) return;

  const url = `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${query.value} 리뷰&maxResults=12&type=video&key=${youtubeKey}`;

  try {
    const { data } = await axios.get(url);
    results.value = data.items;
  } catch (err) {
    console.error("YouTube 검색 실패:", err);
  }
};

const openModal = (videoId) => {
  embedUrl.value = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  embedUrl.value = "";
};

/* 🔹 HomeView에서 넘어온 검색어 처리 */
onMounted(() => {
  const q = route.query.q;
  if (q) {
    query.value = q;
    searchReview();
  }
});
</script>

<style scoped>
/* ===== PAGE WRAPPER ===== */
.page {
  background: #111;
  min-height: 100vh;
}

.wrapper {
  padding: 102px 40px 40px;
  background: #111;
  min-height: 100vh;
  /* max-width: 1400px; */
}

/* ===== SEARCH SECTION ===== */
.search-section {
  margin-bottom: 50px;
  display: flex;
  justify-content: center;
  flex-direction: column;
  align-items: center;
}

.search-section h2 {
  font-size: 20px;
  margin-bottom: 16px;
  color: #fbfbfb;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 30px;
  color: #ffffff;
}

.search-container {
  display: flex;
  gap: 14px;
  width: 100%;
  max-width: 700px;

  padding: 18px 20px;
  border-radius: 18px;

  background: rgb(50, 50, 50);
  backdrop-filter: blur(12px);

  box-shadow: 0 16px 40px rgba(0,0,0,0.45);
}

/* INPUT */
.search-container input {
  flex: 1;
  padding: 12px 14px;
  font-size: 1rem;

  border-radius: 12px;
  border: none;
  outline: none;
}

.search-container input::placeholder {
  color: #8b8b8b;
}

.search-container input:focus {
  outline: 2px solid #7dd3fc;
}

/* BUTTON */
.btn-primary {
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

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(125, 211, 252, 0.45);
}

/* ===== REVIEW GRID ===== */
.review-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 32px;
}

/* CARD */
.review-card {
  background: rgba(22, 22, 22, 0.9);
  border-radius: 18px;
  overflow: hidden;
  cursor: pointer;

  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.45);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.review-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.65);
}

/* THUMBNAIL */
.thumbnail-wrapper {
  position: relative;
  width: 100%;
  padding-top: 56.25%;
}

.thumbnail {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* PLAY OVERLAY */
.play-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);

  width: 56px;
  height: 56px;
  border-radius: 50%;

  background: rgba(0, 0, 0, 0.65);
  color: #7dd3fc;

  display: flex;
  align-items: center;
  justify-content: center;

  font-size: 22px;
  opacity: 0;
  transition: opacity 0.3s;
}

.review-card:hover .play-overlay {
  opacity: 1;
}

/* INFO */
.review-info {
  padding: 16px 18px;
}

.review-title {
  font-size: 0.95rem;
  font-weight: 600;
  line-height: 1.45;
  margin-bottom: 10px;

  color: #f9fafb;

  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.channel-name {
  font-size: 0.85rem;
  color: #9ca3af;
}

/* ===== MODAL ===== */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);

  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  width: 90%;
  max-width: 1000px;
  position: relative;
}

.video-container {
  position: relative;
  padding-top: 56.25%;
}

.video-container iframe {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border-radius: 12px;
  border: none;
}

.close-btn {
  position: absolute;
  top: -46px;
  right: 0;

  background: rgba(0,0,0,0.6);
  border: 1px solid rgba(255,255,255,0.4);
  color: #fff;

  padding: 6px 16px;
  border-radius: 8px;
  cursor: pointer;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
  .wrapper {
    padding: 102px 20px 20px;
  }

  .search-container {
    flex-direction: column;
  }

  .btn-primary {
    width: 100%;
  }
}

</style>

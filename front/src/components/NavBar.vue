<template>
  <nav class="navbar">
    <!-- 왼쪽 메뉴 -->
    <div class="left">
      <!-- Home → 로고 -->
      <RouterLink to="/" class="logo-link">
        <img
          src="@/assets/logo.png"
          alt="Movie Archive"
          class="logo"
        />
      </RouterLink>
      
      <!-- 로그인 시에만 보이는 모든 메뉴 -->
      <template v-if="authStore.isLoggedIn">
        <span class="divider">|</span>
        <RouterLink to="/movies" exact-active-class="active">Movies</RouterLink>
        <span class="divider">|</span>
        <RouterLink to="/review-search" exact-active-class="active">Search Review</RouterLink>
        <span class="divider">|</span>
        <RouterLink to="/watchlist" exact-active-class="active">Watchlist</RouterLink>
        <span class="divider">|</span>
        <RouterLink to="/community" exact-active-class="active">Community</RouterLink>
      </template>
    </div>

    <!-- 오른쪽 로그인 영역 -->
    <div class="right">
      <template v-if="authStore.isLoggedIn">
        <span class="username">
          {{ authStore.currentUser?.username }}님
        </span>
        <span class="divider">|</span>
        <button class="logout-btn" @click="handleLogout">
          로그아웃
        </button>
      </template>

      <template v-else>
        <RouterLink to="/login">로그인</RouterLink>
        <span class="divider">|</span>
        <RouterLink to="/signup">회원가입</RouterLink>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const handleLogout = async () => {
  if (confirm('로그아웃 하시겠습니까?')) {
    await authStore.logout()
    router.push('/')
  }
}
</script>

<style scoped>
/* ===== NAVBAR ROOT ===== */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;

  display: flex;
  justify-content: space-between;
  align-items: center;

  padding: 14px 24px;

  /* ✅ 핵심: 초기 렌더 안정화 */
  background: rgba(0, 0, 0, 0.15);

  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);

  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

/* ===== LEFT / RIGHT WRAPPER ===== */
.left,
.right {
  display: flex;
  align-items: center;
}

/* ===== LOGO ===== */
.logo-link {
  display: flex;
  align-items: center;
}

.logo {
  height: 34px;
  object-fit: contain;

  /* 유리 느낌 */
  filter:
    drop-shadow(0 2px 6px rgba(120, 200, 255, 0.45))
    drop-shadow(0 0 12px rgba(120, 200, 255, 0.25));

  transition: transform 0.25s ease, filter 0.25s ease;
}

.logo-link:hover .logo {
  transform: scale(1.06);
  filter:
    drop-shadow(0 4px 12px rgba(150, 220, 255, 0.7))
    drop-shadow(0 0 18px rgba(180, 240, 255, 0.45));
}

/* ===== MENU LINKS ===== */
.left a,
.right a {
  margin: 0 10px;
  text-decoration: none;

  color: #f9fafb;
  font-weight: 500;

  /* 가독성 핵심 */
  text-shadow:
    0 1px 2px rgba(0, 0, 0, 0.85),
    0 0 6px rgba(0, 0, 0, 0.6);

  transition: color 0.2s ease;
}

.left a:hover,
.right a:hover {
  color: #7dd3fc;
}

/* ===== ACTIVE LINK ===== */
.active {
  font-weight: 700;
  color: #7dd3fc;

  text-shadow:
    0 1px 2px rgba(0, 0, 0, 0.9),
    0 0 10px rgba(125, 211, 252, 0.8);
}

/* ===== DIVIDER ===== */
.divider {
  margin: 0 10px;
  color: rgba(255, 255, 255, 0.35);
}

/* ===== USER INFO ===== */
.username {
  margin-right: 8px;
  font-weight: 500;
  color: #e5e7eb;

  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.85);
}

/* ===== LOGOUT BUTTON ===== */
.logout-btn {
  background: none;
  border: none;
  cursor: pointer;

  padding: 0 4px;
  font-size: 14px;

  color: #ff8a8a;

  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.75);
}

.logout-btn:hover {
  text-decoration: underline;
}

</style>

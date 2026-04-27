import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'
import MovieListView from '@/views/MovieListView.vue'
import MovieDetailView from '@/views/MovieDetailView.vue'
import ReviewSearchView from '@/views/ReviewSearchView.vue'
import SignupView from '@/views/SignupView.vue'
import LoginView from '@/views/LoginView.vue'
import WatchlistView from '@/views/WatchlistView.vue'

const routes = [
  { path: '/', component: HomeView },
  { path: '/movies', component: MovieListView },
  { path: '/movies/:movieId', component: MovieDetailView },
  { path: '/review-search', component: ReviewSearchView },
  { path: '/signup', component: SignupView },
  { path: '/login', component: LoginView },
  { path: '/watchlist', component: WatchlistView },
  { path: '/community', component: () => import('@/views/CommunityView.vue')},
  { path: '/community/:id', component: () => import('@/views/CommunityDetailView.vue')}
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
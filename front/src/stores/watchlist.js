// front/src/stores/watchlist.js

import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useWatchlistStore = defineStore('watchlist', () => {
  // LocalStorage에서 불러오기
  const loadWatchlist = () => {
    const saved = localStorage.getItem('watchlist')
    return saved ? JSON.parse(saved) : []
  }

  const watchlist = ref(loadWatchlist())

  // 총 개수
  const watchlistCount = computed(() => watchlist.value.length)

  // 영화가 이미 목록에 있는지 확인
  const isInWatchlist = (movieId) => {
    return watchlist.value.some(movie => movie.id === movieId)
  }

  // 영화 추가
  const addToWatchlist = (movie) => {
    if (!isInWatchlist(movie.id)) {
      watchlist.value.push({
        id: movie.id,
        title: movie.title,
        poster_path: movie.poster_path,
        vote_average: movie.vote_average,
        release_date: movie.release_date,
        addedAt: new Date().toISOString()
      })
      saveToLocalStorage()
      return true
    }
    return false
  }

  // 영화 제거
  const removeFromWatchlist = (movieId) => {
    const index = watchlist.value.findIndex(movie => movie.id === movieId)
    if (index !== -1) {
      watchlist.value.splice(index, 1)
      saveToLocalStorage()
      return true
    }
    return false
  }

  // 목록 전체 비우기
  const clearWatchlist = () => {
    watchlist.value = []
    saveToLocalStorage()
  }

  // LocalStorage에 저장
  const saveToLocalStorage = () => {
    localStorage.setItem('watchlist', JSON.stringify(watchlist.value))
  }

  return {
    watchlist,
    watchlistCount,
    isInWatchlist,
    addToWatchlist,
    removeFromWatchlist,
    clearWatchlist
  }
})

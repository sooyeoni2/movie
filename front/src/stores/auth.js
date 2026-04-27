import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const storedUser = localStorage.getItem('currentUser')
  const currentUser = ref(storedUser ? JSON.parse(storedUser) : null)
  
  const isLoggedIn = computed(() => token.value !== null)
  
  // Axios 기본 헤더 설정
  const setAuthHeader = () => {
    if (token.value) {
      axios.defaults.headers.common['Authorization'] = `Token ${token.value}`
    } else {
      delete axios.defaults.headers.common['Authorization']
    }
  }
  
  // 초기화 시 토큰 헤더 설정
  setAuthHeader()
  
  // 회원가입
  const signup = async (username, password, genres) => {
    try {
      const response = await axios.post(`${API_URL}/api/accounts/signup/`, {
        username,
        password,
        password2: password,
        genres
      })
      
      token.value = response.data.token
      currentUser.value = response.data.user
      localStorage.setItem('token', token.value)
      localStorage.setItem('currentUser', JSON.stringify(response.data.user))
      setAuthHeader()
      
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || '회원가입에 실패했습니다.')
    }
  }
  
  // 로그인
  const login = async (username, password) => {
    try {
      const response = await axios.post(`${API_URL}/api/accounts/login/`, {
        username,
        password
      })
      
      token.value = response.data.token
      currentUser.value = response.data.user
      localStorage.setItem('token', token.value)
      localStorage.setItem('currentUser', JSON.stringify(response.data.user))
      setAuthHeader()
      
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || '로그인에 실패했습니다.')
    }
  }
  
  // 로그아웃
  const logout = async () => {
    try {
      if (token.value) {
        await axios.post(`${API_URL}/api/accounts/logout/`)
      }
    } catch (error) {
      console.error('로그아웃 요청 실패:', error)
    } finally {
      token.value = null
      currentUser.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('currentUser')
      setAuthHeader()
    }
  }
  
  return {
    token,
    currentUser,
    isLoggedIn,
    signup,
    login,
    logout
  }
})
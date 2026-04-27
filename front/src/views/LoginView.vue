<template>
  <div class="login-page">
    <div class="container">
      <div class="page-header">
        <h2>로그인</h2>
      </div>
      
      <div class="login-box">
        <form @submit.prevent="handleLogin">
          <div class="form-group">
            <label for="username">아이디</label>
            <input 
              type="text" 
              id="username" 
              v-model="username" 
              required
              placeholder="아이디를 입력하세요"
            />
          </div>
          
          <div class="form-group">
            <label for="password">비밀번호</label>
            <input 
              type="password" 
              id="password" 
              v-model="password" 
              required
              placeholder="비밀번호를 입력하세요"
            />
          </div>
          
          <div v-if="error" class="error-message">
            {{ error }}
          </div>
          
          <div class="button-group">
            <button type="submit" class="btn btn-primary">로그인</button>
            <router-link to="/signup" class="btn btn-secondary">회원가입</router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'LoginView',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const username = ref('')
    const password = ref('')
    const error = ref('')
    
    const handleLogin = async () => {
      error.value = ''
      
      if (!username.value || !password.value) {
        error.value = '아이디와 비밀번호를 입력해주세요.'
        return
      }
      
      try {
        await authStore.login(username.value, password.value)
        router.push('/')
      } catch (err) {
        error.value = err.message
      }
    }
    
    return {
      username,
      password,
      error,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-page {
  padding: 102px 40px 40px;
  min-height: 100vh;
  background-color: #e8e8e8;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h2 {
  font-size: 24px;
  color: #333;
  font-weight: normal;
  border-bottom: 2px solid #ddd;
  padding-bottom: 10px;
}

.login-box {
  background-color: #fff;
  border: 1px solid #ddd;
  padding: 40px;
  max-width: 600px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 25px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
}

.form-group input[type="text"],
.form-group input[type="password"] {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid #ddd;
  font-size: 14px;
}

.form-group input:focus {
  outline: none;
  border-color: #0066cc;
}

.error-message {
  padding: 10px 15px;
  background-color: #fee;
  border: 1px solid #fcc;
  color: #c33;
  font-size: 14px;
  margin-bottom: 20px;
}

.button-group {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 12px 30px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  text-decoration: none;
  text-align: center;
  flex: 1;
}

.btn-primary {
  background-color: #0066cc;
  color: white;
}

.btn-primary:hover {
  background-color: #0052a3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

@media (max-width: 768px) {
  .login-box {
    padding: 20px;
  }
  
  .button-group {
    flex-direction: column;
  }
}
</style>
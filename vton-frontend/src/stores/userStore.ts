import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserAccount, UserBody } from '@/types/user'

export const useUserStore = defineStore('user', () => {
  // 登录状态和 token
  const isLoggedIn = ref(false)
  const token = ref<string | null>(null)
  
  // 用户账户信息
  const userAccount = ref<UserAccount | null>(null)
  
  // 用户身体信息
  const userBody = ref<UserBody | null>(null)
  
  // 计算属性
  const isAuthenticated = computed(() => isLoggedIn.value && !!token.value)
  
  // Actions
  function setLoginStatus(status: boolean, accessToken: string | null = null) {
    isLoggedIn.value = status
    token.value = accessToken
    
    if (status && accessToken) {
      localStorage.setItem('isLoggedIn', 'true')
      localStorage.setItem('token', accessToken)
    } else {
      localStorage.removeItem('isLoggedIn')
      localStorage.removeItem('token')
    }
  }
  
  function setUserAccount(account: UserAccount | null) {
    userAccount.value = account
  }
  
  function setUserBody(body: UserBody | null) {
    userBody.value = body
  }
  
  function logout() {
    setLoginStatus(false)
    setUserAccount(null)
    setUserBody(null)
  }
  
  function initializeFromStorage() {
    const storedLoggedIn = localStorage.getItem('isLoggedIn') === 'true'
    const storedToken = localStorage.getItem('token')
    
    if (storedLoggedIn && storedToken) {
      setLoginStatus(true, storedToken)
    }
  }
  
  return {
    // State
    isLoggedIn,
    token,
    userAccount,
    userBody,
    isAuthenticated,
    
    // Actions
    setLoginStatus,
    setUserAccount,
    setUserBody,
    logout,
    initializeFromStorage
  }
})
<template>
    <el-row class="container">
        <el-col>
            <h1>这是“用户中心”页面：{{ userStore.userAccount?.nickname }}</h1>
        </el-col>
    </el-row>
</template>

<script setup lang="ts">
import { usersAPI } from '@/api'
import { useUserStore } from '@/stores/userStore'
import { onMounted } from 'vue'

const userStore = useUserStore()

// 获取用户账户信息
onMounted(async () => {
  if (userStore.isAuthenticated && !userStore.userAccount) {
    try {
      // 调用 API 获取用户信息并存储到 store
      const accountInfo = await usersAPI.getCurrentUserInfo()
      userStore.setUserAccount(accountInfo)
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }
})
</script>

<style scoped>
.container {
    height: 100vh;
    display: flex;
    align-items: center;
}
</style>

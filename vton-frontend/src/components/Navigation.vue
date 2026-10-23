<template>
  <el-container>
    <el-header height="60px" class="header">
      <div class="logo">虚拟试衣间</div>
      <el-menu :default-active="activeIndex" class="el-menu-demo" mode="horizontal" @select="handleSelect">
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/garments">服装库</el-menu-item>
        
        <el-menu-item index="/magic-video">✨ 动态试穿</el-menu-item>

        <template v-if="!isLoggedIn">
          <el-menu-item index="/login">登录</el-menu-item>
          <el-menu-item index="/register">注册</el-menu-item>
        </template>
        <template v-else>
          <el-menu-item index="/usercenter">个人中心</el-menu-item>
          <el-menu-item index="logout" @click="handleLogout">退出登录</el-menu-item>
        </template>
      </el-menu>
    </el-header>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '@/stores/userStore';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

// 初始化登录状态
onMounted(() => {
  userStore.initializeFromStorage();
});

// 使用 store 中的状态
const isLoggedIn = computed(() => userStore.isLoggedIn);

// 计算当前激活的菜单
const activeIndex = computed(() => {
  return route.path;
});

// 菜单选择事件
const handleSelect = (key: string) => {
  if (key === 'logout') {
    handleLogout();
    return;
  }
  router.push(key);
};

// 退出登录
const handleLogout = () => {
  userStore.logout();
  router.push('/login');
};
</script>

<style scoped>
.header {
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: start;
  padding: 0 20px;
}

.logo {
  font-size: 24px;
  font-weight: bold;
  color: #67c23a;
  width: 8%;
}

.el-menu-demo {
  margin-left: 30px;
  border-bottom: none;
  width: 92%;
}
</style>
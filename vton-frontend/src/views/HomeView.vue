<template>
  <div class="boutique-home">
    <aside class="wardrobe-panel">
      <section class="garment-section">
        <header class="section-header">
          <h2 class="section-title">
            上装选配 <span class="count">({{ topGarmentPagination.total }} ITEMS)</span>
          </h2>
          <button class="ghost-btn" @click="changeTopGarments">
            <el-icon><RefreshRight /></el-icon> 换一批
          </button>
        </header>
        <div class="garment-grid">
          <div
            v-for="(top, index) in topGarments"
            :key="index"
            class="garment-card"
            :class="{ 'is-selected': selectedTopGarment === index }"
            @click="selectTopGarment(index)"
          >
            <div class="image-wrapper">
              <img :src="top.image" :alt="top.gtype" />
            </div>
            <p class="garment-name">{{ top.gtype }}</p>
            <div v-if="selectedTopGarment === index" class="selected-badge">
              <el-icon><Check /></el-icon>
            </div>
          </div>
        </div>
      </section>

      <section class="garment-section">
        <header class="section-header">
          <h2 class="section-title">
            下装选配 <span class="count">({{ bottomGarmentPagination.total }} ITEMS)</span>
          </h2>
          <button class="ghost-btn" @click="changeBottomGarments">
            <el-icon><RefreshRight /></el-icon> 换一批
          </button>
        </header>
        <div class="garment-grid">
          <div
            v-for="(bottom, index) in bottomGarments"
            :key="index"
            class="garment-card"
            :class="{ 'is-selected': selectedBottomGarment === index }"
            @click="selectBottomGarment(index)"
          >
            <div class="image-wrapper">
              <img :src="bottom.image" :alt="bottom.gtype" />
            </div>
            <p class="garment-name">{{ bottom.gtype }}</p>
            <div v-if="selectedBottomGarment === index" class="selected-badge">
              <el-icon><Check /></el-icon>
            </div>
          </div>
        </div>
      </section>
    </aside>

    <main class="fitting-room-panel">
      <div class="fitting-stage">
        <img :src="mote_url" class="model-image" alt="Model Try-on" />
        
        <div class="stage-action-bar">
          <button class="action-btn secondary-btn" @click="changeMote">
            <el-icon><User /></el-icon> 更换模特
          </button>
          <button class="action-btn primary-btn magic-try-btn" @click="tryonGarments">
            ✨ 一键试穿
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElLoading } from 'element-plus'
import type { PaginationInfo } from '../types/commons'
import type { Garment, TryOnRequest } from '../types/garment'
import { GarmentCategory } from '../types/garment'
import { garmentsAPI } from '../api/index'

// --- 状态定义 ---
const topGarments = ref<Garment[]>([])
const allTopGarments = ref<Garment[]>([])
const topGarmentPagination = ref<PaginationInfo>({ total: 0, page: 1, limit: 10, pages: 1 })

const bottomGarments = ref<Garment[]>([])
const allBottomGarments = ref<Garment[]>([])
const bottomGarmentPagination = ref<PaginationInfo>({ total: 0, page: 1, limit: 10, pages: 1 })

const pageSize = 3

const selectedTopGarment = ref(0)
const selectedBottomGarment = ref(0)

const mote_url = ref<string>(
  'https://help-static-aliyun-doc.aliyuncs.com/assets/img/zh-CN/1389646171/p801328.png',
)

// --- 方法定义 (逻辑保持不变) ---
const loadGarmentData = async (category: GarmentCategory) => {
  try {
    if (category == GarmentCategory.Top) {
      const data = await garmentsAPI.getGarments(category, '', topGarmentPagination.value.page, topGarmentPagination.value.limit)
      allTopGarments.value = data.items
      topGarmentPagination.value = { total: data.total, page: data.page, limit: data.limit, pages: data.pages }
    }
    if (category == GarmentCategory.Bottom) {
      const data = await garmentsAPI.getGarments(category, '', bottomGarmentPagination.value.page, bottomGarmentPagination.value.limit)
      allBottomGarments.value = data.items
      bottomGarmentPagination.value = { total: data.total, page: data.page, limit: data.limit, pages: data.pages }
    }
    showTopGarmentPage(1)
    showBottomGarmentPage(1)
  } catch (error) {
    ElMessage.error('加载服装数据失败')
  }
}

const selectTopGarment = (index: number) => { selectedTopGarment.value = index }
const selectBottomGarment = (index: number) => { selectedBottomGarment.value = index }

const showTopGarmentPage = (page: number) => {
  const start = (page - 1) * pageSize
  topGarments.value = allTopGarments.value.slice(start, start + pageSize)
  topGarmentPagination.value.page = page
  selectedTopGarment.value = 0 
}

const showBottomGarmentPage = (page: number) => {
  const start = (page - 1) * pageSize
  bottomGarments.value = allBottomGarments.value.slice(start, start + pageSize)
  bottomGarmentPagination.value.page = page
  selectedBottomGarment.value = 0 
}

const changeTopGarments = () => {
  const nextPage = topGarmentPagination.value.page * pageSize < allTopGarments.value.length ? topGarmentPagination.value.page + 1 : 1
  showTopGarmentPage(nextPage)
}

const changeBottomGarments = () => {
  const nextPage = bottomGarmentPagination.value.page * pageSize < allBottomGarments.value.length ? bottomGarmentPagination.value.page + 1 : 1
  showBottomGarmentPage(nextPage)
}

const changeMote = async () => {
  const mote_urls = [
    'https://help-static-aliyun-doc.aliyuncs.com/assets/img/zh-CN/1389646171/p801328.png', 
    'https://help-static-aliyun-doc.aliyuncs.com/assets/img/zh-CN/2389646171/p801337.png', 
    'https://help-static-aliyun-doc.aliyuncs.com/assets/img/zh-CN/2389646171/p801329.png', 
    'https://help-static-aliyun-doc.aliyuncs.com/assets/img/zh-CN/1389646171/p801321.png', 
  ]
  mote_url.value = mote_urls[Math.floor(Math.random() * mote_urls.length)] ?? mote_urls[0] 
}

const tryonGarments = async () => {
  const selectedTop = topGarments.value[selectedTopGarment.value]
  const selectedBottom = bottomGarments.value[selectedBottomGarment.value]

  if (!selectedTop && !selectedBottom) {
    ElMessage.warning('请至少选择一件上装或下装')
    return
  }

  const loading = ElLoading.service({
    lock: true,
    text: 'AI魔法换装中，大约需要1分钟，请耐心等待...',
    background: 'rgba(0, 0, 0, 0.7)',
  })

  try {
    const payload = {
      top_garment_id: selectedTop ? Number(selectedTop.id) : null,
      bottom_garment_id: selectedBottom ? Number(selectedBottom.id) : null,
      person_image_url: mote_url.value,
    } as TryOnRequest

    const result = await garmentsAPI.tryOnGarments(payload)
    ElMessage.success('试穿成功！')
    mote_url.value = result.image_url
  } catch (error) {
    console.error('试穿请求失败:', error)
    ElMessage.error('试穿失败或请求超时，请稍后重试')
  } finally {
    loading.close()
  }
}

onMounted(() => {
  loadGarmentData(GarmentCategory.Top)
  loadGarmentData(GarmentCategory.Bottom)
})
</script>

<style scoped>
/* 整体布局：限制最大宽度并居中，提供呼吸空间 */
.boutique-home {
  display: flex;
  height: calc(100vh - 60px); /* 减去顶部导航栏高度 */
  background-color: var(--vton-bg);
  padding: 24px;
  gap: 30px;
  max-width: 1600px;
  margin: 0 auto;
}

/* 左侧：衣橱面板 */
.wardrobe-panel {
  flex: 0 0 55%; /* 占据 55% 宽度 */
  display: flex;
  flex-direction: column;
  gap: 24px;
  overflow-y: auto;
  padding-right: 10px;
}

/* 隐藏滚动条，保持界面整洁 */
.wardrobe-panel::-webkit-scrollbar { width: 4px; }
.wardrobe-panel::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.1); border-radius: 4px; }

/* 每一个独立的服装区域 (上装/下装) */
.garment-section {
  background: var(--vton-surface);
  border-radius: var(--vton-radius-lg);
  padding: 24px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.02); /* 极轻微的阴影 */
  border: 1px solid var(--vton-border);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--vton-border);
  padding-bottom: 12px;
}

.section-title {
  font-family: var(--vton-font-title);
  font-size: 18px;
  font-weight: 600;
  color: var(--vton-text-main);
  margin: 0;
  letter-spacing: 0.5px;
}

.section-title .count {
  font-family: var(--vton-font-body);
  font-size: 12px;
  color: var(--vton-text-sub);
  font-weight: normal;
  margin-left: 8px;
}

/* 幽灵按钮 (换一批) */
.ghost-btn {
  background: transparent;
  border: none;
  color: var(--vton-text-sub);
  cursor: pointer;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: var(--vton-transition);
}
.ghost-btn:hover { color: var(--vton-accent-primary); }

/* 服装网格布局 */
.garment-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

/* 单个服装卡片 */
.garment-card {
  position: relative;
  background: var(--vton-surface-alt);
  border-radius: var(--vton-radius-sm);
  padding: 12px;
  cursor: pointer;
  transition: var(--vton-transition);
  border: 2px solid transparent;
}

.image-wrapper {
  background: #fff;
  border-radius: 6px;
  overflow: hidden;
  height: 180px; /* 固定高度，保证整齐 */
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: contain; /* 保证衣服不被裁剪变形 */
  transition: transform 0.4s ease;
}

.garment-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--vton-shadow-float);
}

.garment-card:hover .image-wrapper img {
  transform: scale(1.05); /* 悬浮微微放大图片 */
}

/* 选中状态 */
.garment-card.is-selected {
  border-color: var(--vton-accent-primary);
  background: var(--vton-surface);
}

.garment-name {
  text-align: center;
  margin: 12px 0 0;
  font-size: 13px;
  color: var(--vton-text-main);
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 选中时的对勾徽章 */
.selected-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: var(--vton-accent-primary);
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  z-index: 2;
}

/* 右侧：试衣展台 */
.fitting-room-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.fitting-stage {
  position: relative;
  flex: 1;
  background: linear-gradient(to bottom, #F9F9FB, #EAEAEA); /* 非常柔和的展台背景渐变 */
  border-radius: var(--vton-radius-lg);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 0 40px rgba(0,0,0,0.03); /* 内阴影增加空间感 */
  border: 1px solid var(--vton-border);
}

.model-image {
  max-width: 90%;
  max-height: 95%;
  object-fit: contain;
  filter: drop-shadow(0 15px 25px rgba(0,0,0,0.1)); /* 给人物本身加一点阴影，更有立体感 */
}

/* 底部操作面板 (毛玻璃悬浮效果) */
.stage-action-bar {
  position: absolute;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 16px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px); /* 毛玻璃 */
  -webkit-backdrop-filter: blur(12px);
  padding: 12px 24px;
  border-radius: 40px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.08);
  border: 1px solid rgba(255,255,255,0.5);
}

.action-btn {
  border: none;
  padding: 10px 24px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: var(--vton-transition);
  font-family: var(--vton-font-body);
}

.secondary-btn {
  background: transparent;
  color: var(--vton-text-main);
}
.secondary-btn:hover { background: rgba(0,0,0,0.05); }

.primary-btn {
  background: var(--vton-accent-primary);
  color: white;
  box-shadow: 0 4px 12px rgba(58, 71, 80, 0.2);
}
.primary-btn:hover {
  background: #2D3A42;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(58, 71, 80, 0.3);
}
</style>
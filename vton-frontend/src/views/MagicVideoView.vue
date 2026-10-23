<template>
  <div class="boutique-container">
    <div class="header-section">
      <h1 class="boutique-title">AI Fitting Studio</h1>
      <p class="boutique-subtitle">赋予服装生命力的数字工坊</p>
    </div>

    <div class="studio-layout">
      <aside class="gallery-wardrobe">
        <div class="upload-gallery">
          <div class="gallery-card" :class="{ 'has-file': avatarPreview }">
            <input type="file" @change="handleAvatarChange" accept="image/*" class="hidden-input" />
            <div v-if="!avatarPreview" class="empty-state">
              <span class="icon">01</span>
              <span class="label">AVATAR UPLOAD</span>
              <span class="sub-label">上传人物正面照</span>
            </div>
            <div v-else class="preview-state">
              <img :src="avatarPreview" />
              <div class="status-badge">已就绪</div>
            </div>
          </div>

          <div class="gallery-card" :class="{ 'has-file': garmentPreview }">
            <input type="file" @change="handleGarmentChange" accept="image/*" class="hidden-input" />
            <div v-if="!garmentPreview" class="empty-state">
              <span class="icon">02</span>
              <span class="label">GARMENT UPLOAD</span>
              <span class="sub-label">上传服装平铺图</span>
            </div>
            <div v-else class="preview-state">
              <img :src="garmentPreview" />
              <div class="status-badge">已就绪</div>
            </div>
          </div>

          <div class="gallery-card video-card" :class="{ 'has-file': videoFile }">
            <input type="file" @change="handleVideoChange" accept="video/*" class="hidden-input" />
            <div v-if="!videoFile" class="empty-state">
              <span class="icon">03</span>
              <span class="label">MOTION VIDEO</span>
              <span class="sub-label">上传动作参考视频</span>
            </div>
            <div v-else class="preview-state video-ready">
              <span class="video-icon">▶</span>
              <span class="video-name">{{ videoFile.name }}</span>
              <div class="status-badge">已就绪</div>
            </div>
          </div>
        </div>

        <div class="silk-action-bar">
          <button 
            class="action-btn" 
            :class="{ 'is-loading': isLoading }"
            @click="startMagic" 
            :disabled="isLoading || !avatarFile || !garmentFile || !videoFile"
          >
            <span v-if="!isLoading">生成数字试穿视频</span>
            <span v-else class="loading-text">
               <i></i> 丝线交织中... (预计2-5分钟)
            </span>
          </button>
          <div v-if="statusMessage" class="toast-message" :class="{ 'is-error': isError }">
            {{ statusMessage }}
          </div>
        </div>
      </aside>

      <main class="fitting-stage-wrapper">
        <div class="fitting-stage" :class="{ 'is-active': finalVideoUrl || isLoading }">
          <div v-if="!finalVideoUrl && !isLoading" class="stage-placeholder">
            <div class="placeholder-graphic"></div>
            <p>等待灵感注入...</p>
          </div>
          
          <div v-if="isLoading" class="stage-loading">
            <div class="breathing-skeleton"></div>
          </div>

          <video 
            v-if="finalVideoUrl" 
            :src="finalVideoUrl" 
            controls 
            autoplay 
            loop 
            class="stage-video"
          ></video>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
// 这里保留你之前完整的 <script setup> 里的 Typescript / API 逻辑
import { ref, onUnmounted } from 'vue';
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api/pipeline'; 

const avatarFile = ref<File | null>(null);
const garmentFile = ref<File | null>(null);
const videoFile = ref<File | null>(null);

const avatarPreview = ref('');
const garmentPreview = ref('');

const isLoading = ref(false);
const statusMessage = ref('');
const isError = ref(false);
const isSuccess = ref(false);
const finalVideoUrl = ref('');
let pollInterval: any = null;

const handleAvatarChange = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    avatarFile.value = target.files[0];
    avatarPreview.value = URL.createObjectURL(target.files[0]);
  }
};

const handleGarmentChange = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    garmentFile.value = target.files[0];
    garmentPreview.value = URL.createObjectURL(target.files[0]);
  }
};

const handleVideoChange = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    videoFile.value = target.files[0];
  }
};

const startMagic = async () => {
  if (!avatarFile.value || !garmentFile.value || !videoFile.value) return;

  isLoading.value = true;
  isError.value = false;
  isSuccess.value = false;
  finalVideoUrl.value = '';
  statusMessage.value = '正在上传素材...';

  const formData = new FormData();
  formData.append('avatar', avatarFile.value);
  formData.append('garment', garmentFile.value);
  formData.append('video', videoFile.value);

  try {
    const response = await axios.post(`${API_BASE_URL}/generate_magic_video`, formData);
    const taskId = response.data.task_id || response.data.id || response.data.data?.task_id;
    if (!taskId) throw new Error("无任务ID");

    statusMessage.value = 'AI 引擎已启动，请稍候...';
    startPolling(taskId);
  } catch (error: any) {
    isLoading.value = false;
    isError.value = true;
    statusMessage.value = '启动失败: ' + (error.response?.data?.detail || error.message);
  }
};

const startPolling = (taskId: string) => {
  pollInterval = setInterval(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/status/${taskId}`);
      const data = response.data;
      const status = data.output?.task_status || data.task_status || data.status || '';
      const videoUrl = data.output?.results?.video_url || data.video_url || data.url;

      if (videoUrl || status.toUpperCase() === 'SUCCEEDED' || status.toUpperCase() === 'SUCCESS') {
        clearInterval(pollInterval);
        if (videoUrl) {
            finalVideoUrl.value = videoUrl;
            isSuccess.value = true;
            statusMessage.value = '为您呈现。';
        } else {
            isError.value = true;
            statusMessage.value = '未能获取视频链接';
        }
        isLoading.value = false;
      } else if (status.toUpperCase() === 'FAILED' || status.toUpperCase() === 'ERROR') {
        clearInterval(pollInterval);
        isError.value = true;
        statusMessage.value = '生成中断。';
        isLoading.value = false;
      }
    } catch (e) {
      console.log('轮询中...', e);
    }
  }, 5000);
};

onUnmounted(() => { if (pollInterval) clearInterval(pollInterval); });
</script>

<style scoped>
/* 容器与排版 */
.boutique-container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
.header-section { margin-bottom: 40px; text-align: center; }
.boutique-title { font-family: var(--vton-font-title); font-size: 32px; color: var(--vton-accent-primary); letter-spacing: 1px; margin-bottom: 8px; }
.boutique-subtitle { color: var(--vton-text-sub); font-size: 14px; letter-spacing: 2px; text-transform: uppercase; }

/* 双栏布局 */
.studio-layout { display: flex; gap: 40px; align-items: stretch; }

/* 左侧：画廊卡片 (去线化，呼吸感) */
.gallery-wardrobe { flex: 0 0 320px; display: flex; flex-direction: column; gap: 30px; }
.upload-gallery { display: flex; flex-direction: column; gap: 16px; }

.gallery-card {
  position: relative; height: 130px; background: var(--vton-surface-alt);
  border-radius: var(--vton-radius-sm); cursor: pointer; overflow: hidden;
  transition: var(--vton-transition); display: flex; align-items: center; justify-content: center;
}
.gallery-card:hover { transform: translateY(-3px); box-shadow: var(--vton-shadow-float); background: #EAEAEA; }
.gallery-card.has-file { background: var(--vton-surface); box-shadow: 0 2px 12px rgba(0,0,0,0.03); }

.hidden-input { position: absolute; width: 100%; height: 100%; opacity: 0; cursor: pointer; z-index: 10; }

.empty-state { text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center;}
.empty-state .icon { font-family: var(--vton-font-title); font-size: 24px; color: #D0D0D0; margin-bottom: 4px; font-style: italic;}
.empty-state .label { font-size: 12px; font-weight: 600; letter-spacing: 1.5px; color: var(--vton-text-main); margin-bottom: 2px;}
.empty-state .sub-label { font-size: 11px; color: var(--vton-text-sub); }

.preview-state { width: 100%; height: 100%; position: relative; }
.preview-state img { width: 100%; height: 100%; object-fit: cover; opacity: 0.9; }
.video-ready { display: flex; flex-direction: column; align-items: center; justify-content: center; background: var(--vton-accent-primary); color: white; }
.video-icon { font-size: 24px; margin-bottom: 8px; }
.video-name { font-size: 12px; max-width: 80%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* 状态徽标 */
.status-badge { position: absolute; top: 10px; right: 10px; background: rgba(255,255,255,0.9); color: var(--vton-text-main); font-size: 10px; padding: 4px 8px; border-radius: 20px; font-weight: 600; letter-spacing: 1px;}

/* 魔法丝带操作区 */
.silk-action-bar { margin-top: auto; padding-top: 20px; position: relative; }
.action-btn { width: 100%; padding: 18px; border-radius: 30px; border: none; background: var(--vton-accent-primary); color: #fff; font-size: 14px; letter-spacing: 1px; cursor: pointer; transition: var(--vton-transition); font-weight: 500; }
.action-btn:hover:not(:disabled) { background: #263138; transform: translateY(-2px); box-shadow: 0 10px 20px rgba(58, 71, 80, 0.2); }
.action-btn:disabled { background: #E0E0E0; color: #999; cursor: not-allowed; }
.action-btn.is-loading { background: var(--vton-accent-gold); position: relative; overflow: hidden; }

/* 悬浮 Toast 消息 */
.toast-message { position: absolute; bottom: -35px; left: 0; right: 0; text-align: center; font-size: 12px; color: var(--vton-accent-primary); font-weight: 500; letter-spacing: 0.5px; animation: fadeIn 0.3s ease; }
.toast-message.is-error { color: #D9534F; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }

/* 右侧：沉浸式展台 */
.fitting-stage-wrapper { flex: 1; }
.fitting-stage {
  width: 100%; height: 100%; min-height: 500px; border-radius: var(--vton-radius-lg);
  background: linear-gradient(145deg, #1C1C1E, #2C2C2E); position: relative; display: flex; align-items: center; justify-content: center; overflow: hidden;
  transition: var(--vton-transition);
}

/* 环境光晕 */
.fitting-stage::before {
  content: ''; position: absolute; top: 10%; left: 10%; right: 10%; bottom: 10%;
  background: radial-gradient(circle at center, rgba(193, 154, 107, 0.15) 0%, transparent 60%); filter: blur(30px); z-index: 0; opacity: 0; transition: opacity 1s ease;
}
.fitting-stage.is-active::before { opacity: 1; }

.stage-placeholder, .stage-loading { z-index: 1; text-align: center; color: #777; font-size: 13px; letter-spacing: 1px; }
.placeholder-graphic { width: 60px; height: 1px; background: #555; margin: 0 auto 20px; }

/* 优雅的骨架屏动画 */
.breathing-skeleton { width: 120px; height: 160px; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; margin: 0 auto 20px; position: relative; overflow: hidden; }
.breathing-skeleton::after { content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent); animation: sweep 2s infinite ease-in-out; }
@keyframes sweep { 100% { left: 200%; } }

.stage-video { z-index: 2; max-width: 100%; max-height: 600px; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); object-fit: contain; }
</style>
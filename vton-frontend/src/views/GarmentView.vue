<template>
  <div class="garment-container">
    <!-- 筛选标签和新增按钮 -->
    <div class="filter-section">
      <el-tag
        :type="activeTag === '全部' ? 'primary' : 'info'"
        @click="filterByType('全部')"
        class="filter-tag"
        >全部</el-tag
      >
      <el-tag
        v-for="tag in garmentTypeList"
        :key="tag"
        :type="activeTag === tag.name ? 'primary' : 'info'"
        @click="filterByType(tag.name)"
        class="filter-tag"
      >
        {{ tag.name }}
      </el-tag>
      <el-button type="primary" class="add-btn" @click="handleAdd">新增</el-button>
    </div>

    <!-- 服装列表 -->
    <div class="garment-list">
      <el-card v-for="garment in filteredGarments" :key="garment.id" class="garment-card">
        <div class="garment-image">
          <img :src="garment.image" :alt="garment.gtype" />
        </div>
        <div class="garment-info">
          <span>款式：{{ garment.gtype }}</span>
          <span>分类：{{ garment.category }}</span>
        </div>
        <div class="garment-actions">
          <el-button type="primary" size="small" @click="handleEdit(garment)">修改</el-button>
          <el-button type="danger" size="small" @click="handleDelete(garment.id)">删除</el-button>
        </div>
      </el-card>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '修改服装' : '新增服装'" width="500px">
      <el-form :model="formData" label-width="80px">
        <el-form-item label="分类">
          <el-select v-model="formData.category" placeholder="请选择服装分类">
            <el-option label="Top" value="上装" />
            <el-option label="Bottom" value="下装" />
            <el-option label="Whole" value="全身装" />
          </el-select>
        </el-form-item>
        <el-form-item label="款式">
          <el-input v-model="formData.gtype" placeholder="请输入服装款式，如毛衣、外套、T恤等" />
        </el-form-item>
        <el-form-item label="图片">
          <el-upload
            class="avatar-uploader"
            :action="''"
            :show-file-list="false"
            :on-success="handleImageUpload"
            :before-upload="beforeImageUpload"
            :auto-upload="true"
          >
            <img v-if="formData.image" :src="formData.image" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon">
              <Plus />
            </el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog v-model="deleteDialogVisible" title="确认删除" width="300px">
      <span>确定要删除这件服装吗？</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="confirmDelete">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, type ComputedRef } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElLoading } from 'element-plus'
import type { PaginationInfo } from '../types/commons'
import type { GarmentType, Garment, GarmentCreateRequest } from '../types/garment'
import { GarmentCategory } from '../types/garment'
import { garmentsAPI } from '../api'

// 服装列表分页信息
const pagination = ref<PaginationInfo>({
  total: 0,
  page: 1,
  limit: 10,
  pages: 1,
})

// 服装款式列表
const garmentTypeList = ref<GarmentType[]>([])

// 服装列表
const garmentList = ref<Garment[]>([])

// 活动标签
const activeTag = ref('全部')

// 新增/编辑对话框
const dialogVisible = ref(false)
const isEdit = ref(false)
const formData = ref<GarmentCreateRequest>({
  category: GarmentCategory.Top,
  gtype: '',
  gender: '男性',
  sizes: '',
})

// 删除对话框
const deleteDialogVisible = ref(false)
const deleteId = ref(0)

// 筛选后的服装列表
const filteredGarments: ComputedRef<Garment[]> = computed(() => {
  if (activeTag.value === '全部') {
    return garmentList.value
  }
  return garmentList.value.filter((garment) => garment.gtype === activeTag.value)
})

// 按类型筛选
const filterByType = (tag: string) => {
  activeTag.value = tag
}

// 新增服装
const handleAdd = () => {
  isEdit.value = false
  formData.value = {
    name: '',
    category: GarmentCategory,
    type: '',
    imageUrl: '',
  }
  dialogVisible.value = true
}

// 编辑服装
const handleEdit = (garment: Garment) => {
  isEdit.value = true
  formData.value = { ...garment }
  dialogVisible.value = true
}

// 删除服装
const handleDelete = (id: number) => {
  deleteId.value = id
  deleteDialogVisible.value = true
}

// 确认删除
const confirmDelete = async () => {
  const loading = ElLoading.service({
    lock: true,
    text: '正在删除服装...',
    background: 'rgba(0, 0, 0, 0.7)',
  })

  try {
    // await garmentsAPI.deleteGarment(deleteId.value);
    const index = garmentList.value.findIndex((item) => item.id === deleteId.value)
    if (index !== -1) {
      garmentList.value.splice(index, 1)
    }
    ElMessage.success('服装删除成功')
    deleteDialogVisible.value = false
  } catch (error) {
    ElMessage.error('服装删除失败')
  } finally {
    loading.close()
  }
}

// 提交表单
const handleSubmit = async () => {
  const loading = ElLoading.service({
    lock: true,
    text: isEdit.value ? '正在修改服装...' : '正在添加服装...',
    background: 'rgba(0, 0, 0, 0.7)',
  })

  try {
    if (isEdit.value) {
      // 修改服装
      // const updatedGarment = await garmentsAPI.updateGarment(formData.value.id, formData.value);
      // const index = garmentList.value.findIndex(item => item.id === formData.value.id);
      // if (index !== -1) {
      //     garmentList.value[index] = updatedGarment;
      // }
      ElMessage.success('服装修改成功')
    } else {
      // // 新增服装
      // const newGarment = await garmentsAPI.createGarment(formData.value);
      // garmentList.value.push(newGarment);
      ElMessage.success('服装添加成功')
    }
    dialogVisible.value = false
  } catch (error) {
    ElMessage.error(isEdit.value ? '服装修改失败' : '服装添加失败')
  } finally {
    loading.close()
  }
}

// 图片上传前校验
const beforeImageUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('请上传图片文件！')
  }
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过2MB！')
  }
  return isImage && isLt2M
}

// 图片上传成功处理
const handleImageUpload = (response: any, file: any) => {
  // 模拟上传成功，实际项目中应该使用真实的上传接口
  // 在真实项目中，这里应该获取上传后的图片URL
  // formData.value.image = URL.createObjectURL(file.raw);
}

// 加载服装款式数据
const loadGarmentTypeData = async () => {
  const loading = ElLoading.service({
    lock: true,
    text: '正在加载服装款式数据...',
    background: 'rgba(0, 0, 0, 0.7)',
  })
  try {
    const data = await garmentsAPI.getGarmentTypes()
    garmentTypeList.value = data
  } catch (error) {
    ElMessage.error('加载服装款式数据失败')
  } finally {
    loading.close()
  }
}

// 加载服装数据
const loadGarmentData = async () => {
  const loading = ElLoading.service({
    lock: true,
    text: '正在加载服装数据...',
    background: 'rgba(0, 0, 0, 0.7)',
  })

  try {
    const data = await garmentsAPI.getGarments()
    garmentList.value = data.items
    pagination.value = data.pagination
  } catch (error) {
    ElMessage.error('加载服装数据失败')
  } finally {
    loading.close()
  }
}

// 页面初始化时加载数据
onMounted(() => {
  loadGarmentTypeData()
  loadGarmentData()
})
</script>

<style scoped>
/* --- 在 src/views/GarmentView.vue 的 <style scoped> 中添加/覆盖 --- */

.garment-container {
  width: 100%;
  padding: 20px 0;
}

/* 胶囊参数选择器 (替换原本 el-tag 样式) */
.filter-section {
  display: flex;
  align-items: center;
  margin-bottom: 30px; /* 增加呼吸感 */
  gap: 12px;
}

:deep(.filter-tag.el-tag) {
  border-radius: 20px; /* 胶囊形状 */
  padding: 8px 20px;
  height: auto;
  font-size: 14px;
  border: 1px solid var(--vton-border);
  background-color: transparent;
  color: var(--vton-text-sub);
  cursor: pointer;
  transition: var(--vton-transition);
}

:deep(.filter-tag.el-tag--primary) {
  background-color: var(--vton-accent-primary);
  color: white;
  border-color: var(--vton-accent-primary);
}

:deep(.filter-tag.el-tag:hover:not(.el-tag--primary)) {
  background-color: var(--vton-surface-alt);
  color: var(--vton-text-main);
}

/* 画廊式列表卡片 (去线化，悬浮感) */
.garment-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 30px; /* 拉大间距 */
}

/* 覆写 Element Plus 的 el-card 样式 */
:deep(.garment-card.el-card) {
  border: none !important;
  background-color: var(--vton-surface-alt); /* 极淡的灰底作为托盘 */
  border-radius: var(--vton-radius-sm);
  box-shadow: none !important;
  transition: var(--vton-transition);
  overflow: hidden;
}

:deep(.garment-card.el-card:hover) {
  transform: translateY(-5px);
  background-color: var(--vton-surface);
  box-shadow: var(--vton-shadow-float) !important;
}

:deep(.el-card__body) {
  padding: 15px !important;
}

.garment-image {
  height: 220px; /* 加高图片展示区 */
  overflow: hidden;
  margin-bottom: 15px;
  border-radius: 6px;
  background: #fff; /* 图片区纯白底 */
}

.garment-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: transform 0.5s ease;
}

.garment-image img:hover {
  transform: scale(1.03); /* 更微妙的缩放 */
}

.garment-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding: 0 5px;
}

.garment-info span {
  color: var(--vton-text-main);
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.5px;
}

/* 按钮精简 */
.garment-actions {
  display: flex;
  gap: 10px;
  padding: 0 5px;
}

:deep(.garment-actions .el-button) {
  flex: 1;
  border-radius: 15px; /* 圆角按钮 */
  font-weight: 500;
}
.filter-section {
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 16px 12px;
}

:deep(.filter-tag.el-tag) {
  flex: 0 0 auto;
}

.add-btn {
  margin-left: auto;
  border-radius: 999px;
  padding-inline: 20px;
}

@media (max-width: 768px) {
  .filter-section {
    align-items: stretch;
  }

  .add-btn {
    width: 100%;
    margin-left: 0;
  }
}
</style>

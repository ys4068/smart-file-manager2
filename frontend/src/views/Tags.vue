<template>
  <div class="tags-page">
    <div class="toolbar">
      <el-button type="primary" :icon="Plus" @click="showAddDialog">添加标签</el-button>
    </div>

    <el-card shadow="never" style="margin-top: 12px">
      <div class="tag-grid" v-if="tagList.length">
        <div v-for="tag in tagList" :key="tag.id" class="tag-card" :style="{ borderColor: tag.color }">
          <div class="tag-info">
            <el-tag :color="tag.color" effect="dark" size="large">{{ tag.name }}</el-tag>
            <span class="tag-time">创建于 {{ formatDate(tag.created_at) }}</span>
          </div>
          <div class="tag-actions">
            <el-button link type="primary" size="small" @click="editTag(tag)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-popconfirm title="确定删除此标签？关联的文件/书签不会删除" @confirm="deleteTag(tag)">
              <template #reference>
                <el-button link type="danger" size="small">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-popconfirm>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无标签" :image-size="80" />
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑标签' : '添加标签'" width="420px">
      <el-form :model="form" label-position="top">
        <el-form-item label="标签名称" required>
          <el-input v-model="form.name" placeholder="输入标签名" />
        </el-form-item>
        <el-form-item label="颜色">
          <div class="color-picker">
            <div v-for="c in colorOptions" :key="c" class="color-dot"
              :style="{ background: c }"
              :class="{ active: form.color === c }"
              @click="form.color = c" />
            <el-color-picker v-model="form.color" size="small" />
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { tagsAPI } from '@/api/modules'

const tagList = ref([])
const dialogVisible = ref(false)
const editingId = ref(null)

const colorOptions = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399',
  '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16', '#F97316']

const form = ref({ name: '', color: '#409EFF' })

async function fetchTags() {
  try { const res = await tagsAPI.list(); tagList.value = res.data } catch { /* */ }
}

function showAddDialog() {
  editingId.value = null
  form.value = { name: '', color: '#409EFF' }
  dialogVisible.value = true
}

function editTag(tag) {
  editingId.value = tag.id
  form.value = { name: tag.name, color: tag.color }
  dialogVisible.value = true
}

async function submitForm() {
  if (!form.value.name.trim()) {
    ElMessage.warning('标签名不能为空')
    return
  }
  try {
    if (editingId.value) {
      await tagsAPI.update(editingId.value, form.value)
      ElMessage.success('更新成功')
    } else {
      await tagsAPI.create(form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchTags()
  } catch { /* */ }
}

async function deleteTag(tag) {
  try {
    await tagsAPI.delete(tag.id)
    ElMessage.success('删除成功')
    fetchTags()
  } catch { /* */ }
}

function formatDate(date) {
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(fetchTags)
</script>

<style scoped>
.toolbar {
  background: #fff;
  padding: 12px 16px;
  border-radius: 6px;
}
.tag-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.tag-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border: 1px solid #e4e7ed;
  border-left: 4px solid;
  border-radius: 6px;
  background: #fff;
  min-width: 260px;
  gap: 16px;
}
.tag-info {
  display: flex;
  align-items: center;
  gap: 12px;
}
.tag-time {
  font-size: 12px;
  color: #c0c4cc;
}
.color-picker {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.color-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  border: 3px solid transparent;
  transition: border-color 0.2s;
}
.color-dot.active {
  border-color: #303133;
}
</style>

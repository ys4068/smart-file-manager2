<template>
  <div class="files-page">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-upload :show-file-list="false" :before-upload="handleUpload" accept="*">
          <el-button type="primary" :icon="Upload">上传文件</el-button>
        </el-upload>
        <el-input v-model="searchKeyword" placeholder="搜索文件名..." clearable
          :prefix-icon="Search" style="width: 240px; margin-left: 12px"
          @input="handleSearch" />
        <el-select v-model="filterType" placeholder="文件类型" clearable
          style="width: 140px; margin-left: 12px" @change="fetchFiles">
          <el-option v-for="t in fileTypes" :key="t" :label="t" :value="t" />
        </el-select>
      </div>
      <div class="toolbar-right">
        <el-select v-model="sortBy" style="width: 120px" @change="fetchFiles">
          <el-option label="最新上传" value="newest" />
          <el-option label="最早上传" value="oldest" />
          <el-option label="文件名" value="name" />
          <el-option label="文件大小" value="size" />
        </el-select>
      </div>
    </div>

    <!-- 文件表格 -->
    <el-card shadow="never" style="margin-top: 12px">
      <el-table :data="fileList" stripe v-loading="loading" @row-click="previewFile" style="cursor: pointer">
        <el-table-column prop="original_name" label="文件名" min-width="200">
          <template #default="{ row }">
            <span style="display: flex; align-items: center; gap: 8px">
              <el-icon :size="20"><component :is="fileIcon(row.file_type)" /></el-icon>
              <span>{{ row.original_name }}</span>
              <el-tag v-if="row.is_favorite" size="small" type="warning">⭐</el-tag>
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="file_size" label="大小" width="100">
          <template #default="{ row }">{{ formatBytes(row.file_size) }}</template>
        </el-table-column>
        <el-table-column prop="file_type" label="类型" width="80" />
        <el-table-column prop="view_count" label="浏览" width="70" />
        <el-table-column label="标签" min-width="160">
          <template #default="{ row }">
            <el-tag v-for="tag in row.tags" :key="tag.id" size="small"
              :color="tag.color" effect="dark" style="margin-right: 4px">
              {{ tag.name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="170">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="downloadFile(row)">
              <el-icon><Download /></el-icon> 下载
            </el-button>
            <el-button link type="warning" size="small" @click.stop="editFile(row)">
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-popconfirm title="确定删除此文件？" @confirm="deleteFile(row)">
              <template #reference>
                <el-button link type="danger" size="small" @click.stop>
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top: 16px; display: flex; justify-content: flex-end">
        <el-pagination v-model:current-page="page" v-model:page-size="pageSize"
          :total="total" :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next"
          @change="fetchFiles" />
      </div>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editVisible" title="编辑文件信息" width="500px">
      <el-form :model="editForm" label-position="top">
        <el-form-item label="描述">
          <div style="display:flex;gap:8px;width:100%">
            <el-input v-model="editForm.description" type="textarea" :rows="3" placeholder="添加文件描述..." style="flex:1" />
            <el-button :loading="editSuggesting" @click="handleEditSuggest" style="align-self:flex-end">
              🔍 智能分析
            </el-button>
          </div>
        </el-form-item>
        <!-- 智能建议结果 -->
        <el-form-item v-if="editSuggest" label="建议" class="file-suggest-box">
          <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">
            <span style="font-size:12px;color:#999">标签 →</span>
            <el-tag v-for="t in editSuggest.suggested_tags" :key="t" size="small" type="info">{{ t }}</el-tag>
            <el-button size="small" type="primary" link @click="applyEditSuggest">应用建议</el-button>
          </div>
        </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="editForm.tag_ids" multiple placeholder="选择标签" style="width: 100%">
            <el-option v-for="tag in allTags" :key="tag.id" :label="tag.name" :value="tag.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="editForm.is_favorite">收藏</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveFile">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { filesAPI, tagsAPI } from '@/api/modules'

const fileList = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchKeyword = ref('')
const filterType = ref('')
const sortBy = ref('newest')
const fileTypes = ref([])
const allTags = ref([])
const editVisible = ref(false)
const editForm = ref({})
const editSuggesting = ref(false)
const editSuggest = ref(null)
let searchTimer = null

async function fetchFiles() {
  loading.value = true
  try {
    const res = await filesAPI.list({
      page: page.value, per_page: pageSize.value,
      search: searchKeyword.value, file_type: filterType.value, sort: sortBy.value,
    })
    fileList.value = res.data.items
    total.value = res.data.total
  } catch { /* */ }
  finally { loading.value = false }
}

async function fetchFileTypes() {
  try { const res = await filesAPI.types(); fileTypes.value = res.data } catch { /* */ }
}

async function fetchTags() {
  try { const res = await tagsAPI.list(); allTags.value = res.data } catch { /* */ }
}

function handleSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 1; fetchFiles() }, 300)
}

async function handleUpload(file) {
  const formData = new FormData()
  formData.append('file', file)
  try {
    await filesAPI.upload(formData)
    ElMessage.success('上传成功')
    fetchFiles()
    fetchFileTypes()
  } catch { /* */ }
  return false // 阻止默认上传
}

function previewFile(row) {
  ElMessage.info(`文件: ${row.original_name} (${formatBytes(row.file_size)})`)
}

function downloadFile(row) {
  const token = localStorage.getItem('access_token')
  const url = `${filesAPI.downloadUrl(row.id)}?token=${token}`
  window.open(url, '_blank')
}

function editFile(row) {
  editForm.value = {
    id: row.id,
    description: row.description,
    tag_ids: row.tags.map(t => t.id),
    is_favorite: row.is_favorite,
  }
  editSuggest.value = null
  editVisible.value = true
}

async function handleEditSuggest() {
  const text = editForm.value.description || ''
  if (!text.trim()) {
    ElMessage.warning('请先填写描述内容')
    return
  }
  editSuggesting.value = true
  try {
    const res = await filesAPI.suggest({ text })
    editSuggest.value = res.data
  } catch { /* */ }
  finally { editSuggesting.value = false }
}

function applyEditSuggest() {
  if (!editSuggest.value) return
  const suggestedTags = editSuggest.value.suggested_tags || []
  if (suggestedTags.length) {
    // 将建议的标签名匹配到已有标签 ID
    const suggestedIds = []
    for (const name of suggestedTags) {
      const match = allTags.value.find(t => t.name.toLowerCase() === name.toLowerCase())
      if (match) suggestedIds.push(match.id)
    }
    if (suggestedIds.length) {
      const existing = editForm.value.tag_ids || []
      editForm.value.tag_ids = [...new Set([...existing, ...suggestedIds])]
      ElMessage.success('已应用智能建议')
    } else {
      ElMessage.info('建议的标签尚未创建，请先创建对应标签')
    }
  }
}

async function saveFile() {
  try {
    await filesAPI.update(editForm.value.id, {
      description: editForm.value.description,
      is_favorite: editForm.value.is_favorite,
    })
    await filesAPI.updateTags(editForm.value.id, editForm.value.tag_ids)
    ElMessage.success('更新成功')
    editVisible.value = false
    fetchFiles()
  } catch { /* */ }
}

async function deleteFile(row) {
  try {
    await filesAPI.delete(row.id)
    ElMessage.success('删除成功')
    fetchFiles()
  } catch { /* */ }
}

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0, size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return `${size.toFixed(1)} ${units[i]}`
}

function formatDate(date) {
  return new Date(date).toLocaleString('zh-CN')
}

function fileIcon(type) {
  const map = { pdf: 'Document', doc: 'Document', docx: 'Document', xls: 'Grid', xlsx: 'Grid',
    ppt: 'DataAnalysis', pptx: 'DataAnalysis', png: 'Picture', jpg: 'Picture', jpeg: 'Picture',
    gif: 'PictureFilled', zip: 'Box', rar: 'Box', 7z: 'Box', txt: 'Tickets', md: 'Tickets',
    py: 'Monitor', js: 'Monitor', html: 'Monitor', css: 'Monitor', json: 'Monitor' }
  return map[type] || 'Folder'
}

onMounted(() => {
  fetchFiles()
  fetchFileTypes()
  fetchTags()
})
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  padding: 12px 16px;
  border-radius: 6px;
}
.toolbar-left { display: flex; align-items: center; }
.toolbar-right { display: flex; align-items: center; }
.file-suggest-box :deep(.el-form-item__content) {
  background: #f0f9ff;
  border: 1px dashed #91d5ff;
  border-radius: 6px;
  padding: 8px 12px;
}
</style>

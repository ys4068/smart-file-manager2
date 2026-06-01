<template>
  <div class="bookmarks-page">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" :icon="Plus" @click="showAddDialog">添加书签</el-button>
        <el-upload :show-file-list="false" :before-upload="handleImport" accept=".html">
          <el-button :icon="Upload">导入书签</el-button>
        </el-upload>
        <el-input v-model="searchKeyword" placeholder="搜索书签..." clearable
          :prefix-icon="Search" style="width: 240px; margin-left: 12px"
          @input="handleSearch" />
        <el-select v-model="filterCategory" placeholder="分类" clearable
          style="width: 140px; margin-left: 12px" @change="fetchBookmarks">
          <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
        </el-select>
        <el-select v-model="filterTag" placeholder="标签筛选" clearable
          style="width: 140px; margin-left: 12px" @change="fetchBookmarks">
          <el-option v-for="t in allTags" :key="t.id" :label="t.name" :value="t.id" />
        </el-select>
      </div>
      <div class="toolbar-right">
        <el-select v-model="sortBy" style="width: 120px" @change="fetchBookmarks">
          <el-option label="最新添加" value="newest" />
          <el-option label="最早添加" value="oldest" />
          <el-option label="标题排序" value="title" />
          <el-option label="访问最多" value="visits" />
        </el-select>
      </div>
    </div>

    <!-- 书签表格 -->
    <el-card shadow="never" style="margin-top: 12px">
      <el-table :data="bookmarkList" stripe v-loading="loading">
        <el-table-column label="标题" min-width="240">
          <template #default="{ row }">
            <div style="display: flex; align-items: center; gap: 8px">
              <img v-if="row.favicon" :src="row.favicon" width="16" height="16"
                style="flex-shrink: 0" @error="$event.target.style.display='none'" />
              <a :href="row.url" target="_blank" @click.stop>{{ row.title }}</a>
              <el-tag v-if="row.is_favorite" size="small" type="warning">⭐</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="url" label="URL" min-width="200" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="标签" min-width="140">
          <template #default="{ row }">
            <el-tag v-for="tag in row.tags" :key="tag.id" size="small"
              :color="tag.color" effect="dark" style="margin-right: 3px">
              {{ tag.name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="visit_count" label="访问" width="70" />
        <el-table-column prop="created_at" label="添加时间" width="170">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="window.open(row.url, '_blank')">
              <el-icon><Link /></el-icon> 访问
            </el-button>
            <el-button link type="warning" size="small" @click.stop="editBookmark(row)">
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-popconfirm title="确定删除？" @confirm="deleteBookmark(row)">
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
          @change="fetchBookmarks" />
      </div>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="520px">
      <el-form :model="form" label-position="top">
        <el-form-item label="标题" required>
          <el-input v-model="form.title" placeholder="书签标题" />
        </el-form-item>
        <el-form-item label="URL" required>
          <el-input v-model="form.url" placeholder="https://..." />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="描述..." />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" placeholder="选择分类" style="width: 100%" allow-create filterable>
            <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="form.tag_ids" multiple placeholder="选择标签" style="width: 100%">
            <el-option v-for="tag in allTags" :key="tag.id" :label="tag.name" :value="tag.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="form.is_favorite">收藏</el-checkbox>
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
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { bookmarksAPI, tagsAPI } from '@/api/modules'

const bookmarkList = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchKeyword = ref('')
const filterCategory = ref('')
const filterTag = ref('')
const sortBy = ref('newest')
const categories = ref([])
const allTags = ref([])
const dialogVisible = ref(false)
const editingId = ref(null)
let searchTimer = null

const dialogTitle = computed(() => editingId.value ? '编辑书签' : '添加书签')

const form = ref({
  title: '', url: '', description: '', category: '未分类',
  tag_ids: [], is_favorite: false,
})

async function fetchBookmarks() {
  loading.value = true
  try {
    const res = await bookmarksAPI.list({
      page: page.value, per_page: pageSize.value,
      search: searchKeyword.value, category: filterCategory.value,
      tag_id: filterTag.value || undefined, sort: sortBy.value,
    })
    bookmarkList.value = res.data.items
    total.value = res.data.total
  } catch { /* */ }
  finally { loading.value = false }
}

async function fetchCategories() {
  try { const res = await bookmarksAPI.categories(); categories.value = res.data } catch { /* */ }
}

async function fetchTags() {
  try { const res = await tagsAPI.list(); allTags.value = res.data } catch { /* */ }
}

function handleSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 1; fetchBookmarks() }, 300)
}

function showAddDialog() {
  editingId.value = null
  form.value = { title: '', url: '', description: '', category: '未分类', tag_ids: [], is_favorite: false }
  dialogVisible.value = true
}

function editBookmark(row) {
  editingId.value = row.id
  form.value = {
    title: row.title, url: row.url, description: row.description,
    category: row.category, tag_ids: row.tags.map(t => t.id), is_favorite: row.is_favorite,
  }
  dialogVisible.value = true
}

async function submitForm() {
  if (!form.value.title || !form.value.url) {
    ElMessage.warning('标题和URL不能为空')
    return
  }
  try {
    if (editingId.value) {
      await bookmarksAPI.update(editingId.value, form.value)
      await bookmarksAPI.updateTags(editingId.value, form.value.tag_ids)
      ElMessage.success('更新成功')
    } else {
      await bookmarksAPI.create(form.value)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    fetchBookmarks()
    fetchCategories()
  } catch { /* */ }
}

async function deleteBookmark(row) {
  try {
    await bookmarksAPI.delete(row.id)
    ElMessage.success('删除成功')
    fetchBookmarks()
  } catch { /* */ }
}

async function handleImport(file) {
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await bookmarksAPI.import(formData)
    ElMessage.success(res.msg || '导入成功')
    fetchBookmarks()
    fetchCategories()
  } catch { /* */ }
  return false
}

function formatDate(date) {
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchBookmarks()
  fetchCategories()
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
.toolbar-left { display: flex; align-items: center; gap: 8px; }
.toolbar-right { display: flex; align-items: center; }
</style>

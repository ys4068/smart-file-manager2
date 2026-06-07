<template>
  <div class="bookmarks-page">
    <div class="page-header">
      <h2>🔖 书签管理</h2>
      <el-button type="primary" @click="showAdd = true">
        <el-icon><Plus /></el-icon> 添加书签
      </el-button>
    </div>

    <!-- Filters -->
    <el-card class="filter-bar">
      <el-row :gutter="16" align="middle">
        <el-col :span="6">
          <el-input v-model="search" placeholder="搜索书签..." clearable @clear="fetchBookmarks" @keyup.enter="fetchBookmarks">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="category" placeholder="分类筛选" clearable @change="fetchBookmarks">
            <el-option v-for="c in categories" :key="c.name" :label="`${c.name} (${c.count})`" :value="c.name" />
          </el-select>
        </el-col>
        <el-col :span="2">
          <el-checkbox v-model="readLater" @change="fetchBookmarks" border>待读</el-checkbox>
        </el-col>
        <el-col :span="2">
          <el-button @click="fetchBookmarks">搜索</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- Bookmark Cards -->
    <el-row :gutter="16" style="margin-top: 16px">
      <el-col v-for="b in bookmarks" :key="b.id" :span="8" style="margin-bottom: 16px">
        <el-card shadow="hover" class="bookmark-card">
          <div class="bookmark-header">
            <h4 class="bookmark-title">
              <a :href="b.url" target="_blank" @click="handleVisit(b)">{{ b.title }}</a>
            </h4>
            <div class="bookmark-actions">
              <el-button size="small" link @click="openEdit(b)">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button
                size="small"
                link
                :type="b.is_favorite ? 'warning' : ''"
                @click="toggleFavorite(b)"
              >
                <el-icon><Star /></el-icon>
              </el-button>
              <el-popconfirm title="确定删除？" @confirm="handleDelete(b)">
                <template #reference>
                  <el-button size="small" type="danger" link>
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </template>
              </el-popconfirm>
            </div>
          </div>
          <p class="bookmark-desc" v-if="b.description">{{ b.description }}</p>
          <el-tag size="small" type="success" style="margin-right: 4px">{{ b.category }}</el-tag>
          <el-tag v-if="b.is_read_later" size="small" type="warning">待读</el-tag>
          <div class="bookmark-tags" v-if="b.tags.length">
            <el-tag v-for="t in b.tags" :key="t" size="small" type="info" style="margin: 2px">{{ t }}</el-tag>
          </div>
          <div class="bookmark-footer">
            <span class="visit-count">访问 {{ b.visit_count }} 次</span>
            <span class="bookmark-time">{{ formatTime(b.created_at) }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-empty v-if="!loading && !bookmarks.length" description="暂无书签" />

    <div style="margin-top: 16px; text-align: right" v-if="total > perPage">
      <el-pagination
        v-model:current-page="page"
        :page-size="perPage"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="fetchBookmarks"
      />
    </div>

    <!-- Add Dialog -->
    <el-dialog v-model="showAdd" title="添加书签" width="500px">
      <el-form :model="addForm" :rules="addRules" ref="addFormRef" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="addForm.title" placeholder="书签标题" />
        </el-form-item>
        <el-form-item label="URL" prop="url">
          <el-input v-model="addForm.url" placeholder="https://..." @blur="handleUrlBlur">
            <template #append>
              <el-button :loading="urlSuggesting" @click="handleUrlSuggest">
                🔍 智能分析
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        <!-- URL 智能建议结果 -->
        <el-form-item v-if="urlSuggest" label="建议" class="url-suggest-box">
          <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">
            <span style="font-size:13px;color:#999">分类 →</span>
            <el-tag type="success" size="small">{{ urlSuggest.suggested_category }}</el-tag>
            <el-button size="small" type="primary" link @click="applyUrlSuggest">应用建议</el-button>
          </div>
          <div style="margin-top:4px;display:flex;align-items:center;gap:4px;flex-wrap:wrap">
            <span style="font-size:12px;color:#999">标签 →</span>
            <el-tag v-for="t in urlSuggest.suggested_tags" :key="t" size="small" type="info">{{ t }}</el-tag>
          </div>
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="addForm.category" placeholder="如：技术博客" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="addForm.tags" placeholder="逗号分隔" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="addForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="addForm.is_read_later">加入待读列表</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdd = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleAdd">添加</el-button>
      </template>
    </el-dialog>

    <!-- Edit Dialog -->
    <el-dialog v-model="showEdit" title="编辑书签" width="500px">
      <el-form label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="editForm.title" />
        </el-form-item>
        <el-form-item label="URL">
          <el-input v-model="editForm.url" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="editForm.category" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="editForm.tags" placeholder="逗号分隔" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="editForm.is_read_later">待读</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEdit = false">取消</el-button>
        <el-button type="primary" @click="handleEditSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import api from "@/api";

const bookmarks = ref([]);
const categories = ref([]);
const loading = ref(false);
const search = ref("");
const category = ref("");
const readLater = ref(false);
const page = ref(1);
const perPage = ref(9);
const total = ref(0);
const saving = ref(false);
const urlSuggesting = ref(false);
const urlSuggest = ref(null);

const showAdd = ref(false);
const addFormRef = ref(null);
const addForm = ref({
  title: "",
  url: "",
  category: "",
  tags: "",
  description: "",
  is_read_later: false,
});

const addRules = {
  title: [{ required: true, message: "请输入标题", trigger: "blur" }],
  url: [{ required: true, message: "请输入URL", trigger: "blur" }],
};

const showEdit = ref(false);
const editBookmarkId = ref(null);
const editForm = ref({
  title: "",
  url: "",
  category: "",
  tags: "",
  description: "",
  is_read_later: false,
});

function formatTime(t) {
  if (!t) return "";
  return new Date(t).toLocaleString("zh-CN");
}

async function fetchBookmarks() {
  loading.value = true;
  try {
    const res = await api.get("/bookmarks", {
      params: {
        page: page.value,
        per_page: perPage.value,
        search: search.value || undefined,
        category: category.value || undefined,
        read_later: readLater.value ? "1" : undefined,
      },
    });
    bookmarks.value = res.bookmarks;
    total.value = res.total;
  } finally {
    loading.value = false;
  }
}

async function fetchCategories() {
  try {
    const res = await api.get("/bookmarks/categories");
    categories.value = res.categories;
  } catch {}
}

async function handleAdd() {
  const valid = await addFormRef.value.validate().catch(() => false);
  if (!valid) return;

  saving.value = true;
  try {
    const data = {
      title: addForm.value.title,
      url: addForm.value.url,
      category: addForm.value.category || "未分类",
      tags: addForm.value.tags.split(",").map((t) => t.trim()).filter(Boolean),
      description: addForm.value.description,
      is_read_later: addForm.value.is_read_later,
    };
    await api.post("/bookmarks", data);
    ElMessage.success("添加成功");
    showAdd.value = false;
    addForm.value = { title: "", url: "", category: "", tags: "", description: "", is_read_later: false };
    urlSuggest.value = null;
    fetchBookmarks();
    fetchCategories();
  } finally {
    saving.value = false;
  }
}

async function handleUrlSuggest() {
  if (!addForm.value.url.trim()) return;
  urlSuggesting.value = true;
  try {
    const res = await api.post("/search/suggest-url", { url: addForm.value.url });
    urlSuggest.value = res;
  } catch {
    // handled by interceptor
  } finally {
    urlSuggesting.value = false;
  }
}

function handleUrlBlur() {
  if (addForm.value.url.trim() && (!addForm.value.category || addForm.value.category === "未分类")) {
    handleUrlSuggest();
  }
}

function applyUrlSuggest() {
  if (!urlSuggest.value) return;
  if (urlSuggest.value.suggested_category && urlSuggest.value.suggested_category !== "未分类") {
    addForm.value.category = urlSuggest.value.suggested_category;
  }
  if (urlSuggest.value.suggested_tags && urlSuggest.value.suggested_tags.length) {
    const existing = addForm.value.tags.split(",").map(t => t.trim()).filter(Boolean);
    const merged = [...new Set([...existing, ...urlSuggest.value.suggested_tags])];
    addForm.value.tags = merged.join(", ");
  }
  ElMessage.success("已应用智能建议");
}

function openEdit(row) {
  editBookmarkId.value = row.id;
  editForm.value = {
    title: row.title,
    url: row.url,
    category: row.category,
    tags: Array.isArray(row.tags) ? row.tags.join(",") : row.tags,
    description: row.description,
    is_read_later: row.is_read_later,
  };
  showEdit.value = true;
}

async function handleEditSave() {
  try {
    await api.put(`/bookmarks/${editBookmarkId.value}`, {
      title: editForm.value.title,
      url: editForm.value.url,
      category: editForm.value.category,
      tags: editForm.value.tags.split(",").map((t) => t.trim()).filter(Boolean),
      description: editForm.value.description,
      is_read_later: editForm.value.is_read_later,
    });
    ElMessage.success("更新成功");
    showEdit.value = false;
    fetchBookmarks();
    fetchCategories();
  } catch {}
}

async function toggleFavorite(row) {
  try {
    await api.put(`/bookmarks/${row.id}`, { is_favorite: !row.is_favorite });
    row.is_favorite = !row.is_favorite;
  } catch {}
}

async function handleVisit(row) {
  try {
    await api.post(`/bookmarks/${row.id}/visit`);
    row.visit_count++;
  } catch {}
}

async function handleDelete(row) {
  try {
    await api.delete(`/bookmarks/${row.id}`);
    ElMessage.success("删除成功");
    fetchBookmarks();
    fetchCategories();
  } catch {}
}

onMounted(() => {
  fetchBookmarks();
  fetchCategories();
});
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.page-header h2 {
  margin: 0;
}
.bookmark-card {
  height: 100%;
}
.bookmark-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.bookmark-title {
  margin: 0;
  flex: 1;
}
.bookmark-title a {
  color: #333;
  text-decoration: none;
}
.bookmark-title a:hover {
  color: #409eff;
}
.bookmark-desc {
  color: #666;
  font-size: 13px;
  margin: 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.bookmark-tags {
  margin-top: 8px;
}
.bookmark-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  font-size: 12px;
  color: #999;
}
.bookmark-actions {
  display: flex;
  flex-shrink: 0;
}
.url-suggest-box :deep(.el-form-item__content) {
  background: #f0f9ff;
  border: 1px dashed #91d5ff;
  border-radius: 6px;
  padding: 8px 12px;
}
</style>

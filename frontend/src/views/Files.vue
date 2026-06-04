<template>
  <div class="files-page">
    <div class="page-header">
      <h2>📁 文件管理</h2>
      <el-button type="primary" @click="showUpload = true">
        <el-icon><Upload /></el-icon> 上传文件
      </el-button>
    </div>

    <!-- Filters -->
    <el-card class="filter-bar">
      <el-row :gutter="16" align="middle">
        <el-col :span="6">
          <el-input v-model="search" placeholder="搜索文件..." clearable @clear="fetchFiles" @keyup.enter="fetchFiles">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="category" placeholder="分类筛选" clearable @change="fetchFiles">
            <el-option v-for="c in categories" :key="c.name" :label="`${c.name} (${c.count})`" :value="c.name" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="fileType" placeholder="文件类型" clearable @change="fetchFiles">
            <el-option label="文档" value="document" />
            <el-option label="图片" value="image" />
            <el-option label="视频" value="video" />
            <el-option label="音频" value="audio" />
            <el-option label="压缩包" value="archive" />
          </el-select>
        </el-col>
        <el-col :span="2">
          <el-button @click="fetchFiles">搜索</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- File Table -->
    <el-card style="margin-top: 16px">
      <el-table :data="files" stripe v-loading="loading" @sort-change="handleSortChange">
        <el-table-column prop="original_name" label="文件名" min-width="200">
          <template #default="{ row }">
            <div class="file-name-cell">
              <el-icon :size="20"><Document /></el-icon>
              <span>{{ row.original_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="file_size" label="大小" width="100" sortable="custom">
          <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
        </el-table-column>
        <el-table-column prop="file_type" label="类型" width="90">
          <template #default="{ row }">
            <el-tag size="small">{{ typeLabel(row.file_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="100">
          <template #default="{ row }">
            <el-tag size="small" type="success">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tags" label="标签" width="150">
          <template #default="{ row }">
            <el-tag v-for="t in row.tags" :key="t" size="small" type="info" style="margin: 2px">{{ t }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="170" sortable="custom">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="handleDownload(row)">
              <el-icon><Download /></el-icon>
            </el-button>
            <el-button size="small" link @click="openEdit(row)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button
              size="small"
              link
              :type="row.is_favorite ? 'warning' : ''"
              @click="toggleFavorite(row)"
            >
              <el-icon><Star /></el-icon>
            </el-button>
            <el-popconfirm title="确定删除此文件？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button size="small" type="danger" link>
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 16px; text-align: right">
        <el-pagination
          v-model:current-page="page"
          :page-size="perPage"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="fetchFiles"
        />
      </div>
    </el-card>

    <!-- Upload Dialog -->
    <el-dialog v-model="showUpload" title="上传文件" width="500px">
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        drag
      >
        <el-icon :size="48"><UploadFilled /></el-icon>
        <div>将文件拖到此处或<em>点击上传</em></div>
      </el-upload>
      <el-form style="margin-top: 16px" label-width="80px">
        <el-form-item label="分类">
          <el-input v-model="uploadForm.category" placeholder="如：技术文档" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="uploadForm.tags" placeholder="逗号分隔，如：python,教程" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="uploadForm.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUpload = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">上传</el-button>
      </template>
    </el-dialog>

    <!-- Edit Dialog -->
    <el-dialog v-model="showEdit" title="编辑文件信息" width="500px">
      <el-form label-width="80px">
        <el-form-item label="分类">
          <el-input v-model="editForm.category" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="editForm.tags" placeholder="逗号分隔" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
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

const files = ref([]);
const categories = ref([]);
const loading = ref(false);
const search = ref("");
const category = ref("");
const fileType = ref("");
const page = ref(1);
const perPage = ref(10);
const total = ref(0);
const sortField = ref("updated_at");
const sortOrder = ref("desc");

const showUpload = ref(false);
const uploading = ref(false);
const uploadRef = ref(null);
const uploadFile = ref(null);
const uploadForm = ref({ category: "", tags: "", description: "" });

const showEdit = ref(false);
const editFileId = ref(null);
const editForm = ref({ category: "", tags: "", description: "" });

const typeLabels = {
  document: "文档",
  image: "图片",
  video: "视频",
  audio: "音频",
  archive: "压缩包",
  other: "其他",
};

function typeLabel(type) {
  return typeLabels[type] || type;
}

function formatSize(bytes) {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let i = 0;
  let size = bytes;
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024;
    i++;
  }
  return size.toFixed(1) + " " + units[i];
}

function formatTime(t) {
  if (!t) return "";
  return new Date(t).toLocaleString("zh-CN");
}

async function fetchFiles() {
  loading.value = true;
  try {
    const res = await api.get("/files", {
      params: {
        page: page.value,
        per_page: perPage.value,
        search: search.value || undefined,
        category: category.value || undefined,
        file_type: fileType.value || undefined,
        sort_field: sortField.value,
        sort_order: sortOrder.value,
      },
    });
    files.value = res.files;
    total.value = res.total;
  } finally {
    loading.value = false;
  }
}

async function fetchCategories() {
  try {
    const res = await api.get("/files/categories");
    categories.value = res.categories;
  } catch {}
}

function handleSortChange({ prop, order }) {
  sortField.value = prop || "updated_at";
  sortOrder.value = order === "ascending" ? "asc" : "desc";
  fetchFiles();
}

function handleFileChange(file) {
  uploadFile.value = file.raw;
}

async function handleUpload() {
  if (!uploadFile.value) {
    ElMessage.warning("请先选择文件");
    return;
  }
  uploading.value = true;
  try {
    const formData = new FormData();
    formData.append("file", uploadFile.value);
    formData.append("category", uploadForm.value.category || "未分类");
    formData.append("tags", uploadForm.value.tags);
    formData.append("description", uploadForm.value.description);
    await api.post("/files/upload", formData);
    ElMessage.success("上传成功");
    showUpload.value = false;
    uploadForm.value = { category: "", tags: "", description: "" };
    uploadFile.value = null;
    fetchFiles();
    fetchCategories();
  } finally {
    uploading.value = false;
  }
}

function handleDownload(row) {
  window.open(`/api/files/${row.id}/download?token=${localStorage.getItem("token")}`);
}

function openEdit(row) {
  editFileId.value = row.id;
  editForm.value = {
    category: row.category,
    tags: Array.isArray(row.tags) ? row.tags.join(",") : row.tags,
    description: row.description,
  };
  showEdit.value = true;
}

async function handleEditSave() {
  try {
    await api.put(`/files/${editFileId.value}`, {
      category: editForm.value.category,
      tags: editForm.value.tags.split(",").map((t) => t.trim()).filter(Boolean),
      description: editForm.value.description,
    });
    ElMessage.success("更新成功");
    showEdit.value = false;
    fetchFiles();
    fetchCategories();
  } catch {}
}

async function toggleFavorite(row) {
  try {
    await api.put(`/files/${row.id}`, { is_favorite: !row.is_favorite });
    row.is_favorite = !row.is_favorite;
  } catch {}
}

async function handleDelete(row) {
  try {
    await api.delete(`/files/${row.id}`);
    ElMessage.success("删除成功");
    fetchFiles();
    fetchCategories();
  } catch {}
}

onMounted(() => {
  fetchFiles();
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
.file-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>

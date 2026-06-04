<template>
  <div class="files-page">
    <div class="page-header">
      <h2>📁 文件管理</h2>
      <div class="header-actions">
        <el-button @click="showFolderCreate = true">
          <el-icon><FolderAdd /></el-icon> 新建文件夹
        </el-button>
        <el-button type="primary" @click="showUpload = true">
          <el-icon><Upload /></el-icon> 上传文件
        </el-button>
      </div>
    </div>

    <div class="files-body">
      <!-- 文件夹侧边栏 -->
      <div class="folder-sidebar">
        <el-card class="folder-card">
          <template #header>
            <span style="font-weight: bold">📂 目录结构</span>
          </template>
          <el-tree
            :data="folderTree"
            :props="{ label: 'name', children: 'children' }"
            node-key="id"
            highlight-current
            :expand-on-click-node="true"
            :default-expanded-keys="[]"
            @node-click="handleFolderClick"
          >
            <template #default="{ node, data }">
              <div class="folder-node">
                <el-icon color="#e6a23c"><Folder /></el-icon>
                <span class="folder-name">{{ data.name }}</span>
                <span class="folder-count">({{ data.file_count || 0 }})</span>
                <span class="folder-actions" @click.stop>
                  <el-button size="small" link @click="renameFolder(data)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-popconfirm title="删除文件夹会将文件移回根目录，确定？" @confirm="deleteFolder(data)">
                    <template #reference>
                      <el-button size="small" link type="danger">
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </template>
                  </el-popconfirm>
                </span>
              </div>
            </template>
          </el-tree>
          <div v-if="currentFolder" style="margin-top: 8px; padding: 8px; background: #f5f7fa; border-radius: 4px">
            当前位置：
            <template v-if="currentFolder.label === '全部'">📁 全部文件</template>
            <template v-else>📂 {{ currentFolder.name }}</template>
            <el-button size="small" link @click="resetFolder">← 返回根目录</el-button>
          </div>
        </el-card>
      </div>

      <!-- 主内容区 -->
      <div class="files-main">
        <!-- 筛选 -->
        <el-card class="filter-bar">
          <el-row :gutter="12" align="middle">
            <el-col :span="6">
              <el-input v-model="search" placeholder="搜索文件..." clearable @clear="fetchFiles" @keyup.enter="fetchFiles" size="default">
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>
            </el-col>
            <el-col :span="4">
              <el-select v-model="category" placeholder="分类" clearable @change="fetchFiles" size="default">
                <el-option v-for="c in categories" :key="c.name" :label="`${c.name} (${c.count})`" :value="c.name" />
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-select v-model="fileType" placeholder="类型" clearable @change="fetchFiles" size="default">
                <el-option label="文档" value="document" />
                <el-option label="图片" value="image" />
                <el-option label="视频" value="video" />
                <el-option label="音频" value="audio" />
                <el-option label="压缩包" value="archive" />
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-select v-model="selectedFolderId" placeholder="文件夹" clearable @change="fetchFiles" size="default">
                <el-option label="全部文件" :value="null" />
                <el-option v-for="f in folderFlat" :key="f.id" :label="f.prefix + f.name" :value="f.id" />
              </el-select>
            </el-col>
            <el-col :span="3">
              <el-button @click="fetchFiles" size="default">搜索</el-button>
            </el-col>
          </el-row>
        </el-card>

        <!-- 文件表格 -->
        <el-card style="margin-top: 12px">
          <el-table :data="files" stripe v-loading="loading">
            <el-table-column prop="original_name" label="文件名" min-width="220">
              <template #default="{ row }">
                <div class="file-name-cell">
                  <el-icon :size="18"><Document /></el-icon>
                  <span>{{ row.original_name }}</span>
                  <el-tag v-if="row.access_level === 'public'" size="small" type="success" effect="dark">公开</el-tag>
                  <el-tag v-if="row.share_token" size="small" type="warning" effect="dark">已分享</el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="file_size" label="大小" width="100" sortable="custom">
              <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
            </el-table-column>
            <el-table-column prop="file_type" label="类型" width="80">
              <template #default="{ row }">
                <el-tag size="small">{{ typeLabel(row.file_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="category" label="分类" width="100">
              <template #default="{ row }">
                <el-tag size="small" type="success">{{ row.category }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="folder_name" label="所在目录" width="120">
              <template #default="{ row }">
                <span v-if="row.folder_name" style="color: #e6a23c">📂 {{ row.folder_name }}</span>
                <span v-else style="color: #ccc">根目录</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="时间" width="160" sortable="custom">
              <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="260" fixed="right">
              <template #default="{ row }">
                <el-button size="small" link @click="handleDownload(row)" title="下载">
                  <el-icon><Download /></el-icon>
                </el-button>
                <el-button size="small" link @click="openEdit(row)" title="编辑">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button size="small" link @click="openMove(row)" title="移动">
                  <el-icon><FolderOpened /></el-icon>
                </el-button>
                <el-button size="small" link :type="row.share_token ? 'warning' : ''" @click="handleShare(row)" title="分享">
                  <el-icon><Share /></el-icon>
                </el-button>
                <el-button size="small" link :type="row.is_favorite ? 'warning' : ''" @click="toggleFavorite(row)" title="收藏">
                  <el-icon><Star /></el-icon>
                </el-button>
                <el-popconfirm title="确定删除？" @confirm="handleDelete(row)">
                  <template #reference>
                    <el-button size="small" link type="danger" title="删除">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>

          <div style="margin-top: 12px; text-align: right">
            <el-pagination
              v-model:current-page="page"
              :page-size="perPage"
              :total="total"
              layout="total, prev, pager, next"
              @current-change="fetchFiles"
              small
            />
          </div>
        </el-card>
      </div>
    </div>

    <!-- ========== 弹窗 ========== -->

    <!-- 上传 -->
    <el-dialog v-model="showUpload" title="上传文件" width="500px">
      <el-upload ref="uploadRef" :auto-upload="false" :on-change="handleFileChange" :limit="1" drag>
        <el-icon :size="48"><UploadFilled /></el-icon>
        <div>将文件拖到此处或<em>点击上传</em></div>
      </el-upload>
      <el-form style="margin-top: 12px" label-width="60px" size="small">
        <el-form-item label="目录">
          <el-tree-select
            v-model="uploadForm.folder_id"
            :data="folderTree"
            :props="{ label: 'name', children: 'children', value: 'id' }"
            placeholder="根目录"
            clearable
            check-strictly
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="uploadForm.category" placeholder="如：技术文档" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="uploadForm.tags" placeholder="逗号分隔" />
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

    <!-- 编辑 -->
    <el-dialog v-model="showEdit" title="编辑文件" width="500px">
      <el-form label-width="60px">
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

    <!-- 移动 -->
    <el-dialog v-model="showMove" title="移动文件" width="400px">
      <p>将「{{ moveFile?.original_name }}」移动到：</p>
      <el-tree-select
        v-model="moveTargetId"
        :data="folderTree"
        :props="{ label: 'name', children: 'children', value: 'id' }"
        placeholder="根目录"
        clearable
        check-strictly
        style="width: 100%; margin-top: 12px"
      />
      <template #footer>
        <el-button @click="showMove = false">取消</el-button>
        <el-button type="primary" @click="handleMove">确定移动</el-button>
      </template>
    </el-dialog>

    <!-- 创建文件夹 -->
    <el-dialog v-model="showFolderCreate" title="新建文件夹" width="400px">
      <el-form label-width="80px">
        <el-form-item label="文件夹名">
          <el-input v-model="newFolderName" placeholder="输入文件夹名称" @keyup.enter="createFolder" />
        </el-form-item>
        <el-form-item label="父目录">
          <el-tree-select
            v-model="newFolderParentId"
            :data="folderTree"
            :props="{ label: 'name', children: 'children', value: 'id' }"
            placeholder="根目录（可选）"
            clearable
            check-strictly
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showFolderCreate = false">取消</el-button>
        <el-button type="primary" @click="createFolder">创建</el-button>
      </template>
    </el-dialog>

    <!-- 重命名文件夹 -->
    <el-dialog v-model="showFolderRename" title="重命名文件夹" width="400px">
      <el-input v-model="renameFolderName" placeholder="新名称" @keyup.enter="confirmRename" />
      <template #footer>
        <el-button @click="showFolderRename = false">取消</el-button>
        <el-button type="primary" @click="confirmRename">确定</el-button>
      </template>
    </el-dialog>

    <!-- 分享链接 -->
    <el-dialog v-model="showShare" title="文件分享" width="450px">
      <template v-if="shareToken">
        <p>📎 分享链接已生成：</p>
        <el-input v-model="shareUrl" readonly style="margin-top: 8px">
          <template #append>
            <el-button @click="copyShareUrl">复制</el-button>
          </template>
        </el-input>
        <p style="margin-top: 12px; font-size: 12px; color: #999">
          知道此链接的人都可以查看和下载该文件
        </p>
        <el-button type="danger" size="small" @click="revokeShare(shareFile)">撤销分享</el-button>
      </template>
      <template v-else>
        <p>生成公开分享链接？</p>
        <el-button type="primary" @click="handleShare(shareFile, true)">生成链接</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { ElMessage } from "element-plus";
import api from "@/api";

// ---- state ----
const files = ref([]);
const categories = ref([]);
const folderTree = ref([]);
const folderFlat = ref([]);
const loading = ref(false);
const search = ref("");
const category = ref("");
const fileType = ref("");
const selectedFolderId = ref(null);
const currentFolder = ref(null);
const page = ref(1);
const perPage = ref(10);
const total = ref(0);

const showUpload = ref(false);
const uploading = ref(false);
const uploadRef = ref(null);
const uploadFile = ref(null);
const uploadForm = ref({ folder_id: null, category: "", tags: "", description: "" });

const showEdit = ref(false);
const editFileId = ref(null);
const editForm = ref({ category: "", tags: "", description: "" });

const showMove = ref(false);
const moveFile = ref(null);
const moveTargetId = ref(null);

const showFolderCreate = ref(false);
const newFolderName = ref("");
const newFolderParentId = ref(null);

const showFolderRename = ref(false);
const renameFolderId = ref(null);
const renameFolderName = ref("");

const showShare = ref(false);
const shareFile = ref(null);
const shareToken = ref("");
const shareUrl = computed(() => shareToken.value ? `${window.location.origin}/api/files/share/${shareToken.value}` : "");

const typeLabels = {
  document: "文档", image: "图片", video: "视频", audio: "音频", archive: "压缩包", other: "其他",
};

function typeLabel(type) { return typeLabels[type] || type; }

function formatSize(bytes) {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let i = 0, size = bytes;
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++; }
  return size.toFixed(1) + " " + units[i];
}

function formatTime(t) { return t ? new Date(t).toLocaleString("zh-CN") : ""; }

// ---- API ----

async function fetchFiles() {
  loading.value = true;
  try {
    const params = {
      page: page.value,
      per_page: perPage.value,
      search: search.value || undefined,
      category: category.value || undefined,
      file_type: fileType.value || undefined,
      folder_id: selectedFolderId.value,
    };
    const res = await api.get("/files", { params });
    files.value = res.files;
    total.value = res.total;
  } finally {
    loading.value = false;
  }
}

async function fetchFolders() {
  try {
    const res = await api.get("/folders");
    folderTree.value = res.folders || [];
    const flat = await api.get("/folders/flat");
    folderFlat.value = flat.folders || [];
  } catch {}
}

async function fetchCategories() {
  try {
    const res = await api.get("/files/categories");
    categories.value = res.categories;
  } catch {}
}

// ---- 文件夹操作 ----

function handleFolderClick(data) {
  currentFolder.value = data;
  selectedFolderId.value = data.id;
  page.value = 1;
  fetchFiles();
}

function resetFolder() {
  currentFolder.value = null;
  selectedFolderId.value = null;
  page.value = 1;
  fetchFiles();
}

async function createFolder() {
  if (!newFolderName.value.trim()) {
    ElMessage.warning("请输入文件夹名称");
    return;
  }
  try {
    await api.post("/folders", { name: newFolderName.value, parent_id: newFolderParentId.value || null });
    ElMessage.success("文件夹创建成功");
    showFolderCreate.value = false;
    newFolderName.value = "";
    newFolderParentId.value = null;
    fetchFolders();
  } catch {}
}

function renameFolder(data) {
  renameFolderId.value = data.id;
  renameFolderName.value = data.name;
  showFolderRename.value = true;
}

async function confirmRename() {
  if (!renameFolderName.value.trim()) return;
  try {
    await api.put(`/folders/${renameFolderId.value}`, { name: renameFolderName.value });
    ElMessage.success("重命名成功");
    showFolderRename.value = false;
    fetchFolders();
  } catch {}
}

async function deleteFolder(data) {
  try {
    await api.delete(`/folders/${data.id}`);
    ElMessage.success("删除成功");
    if (selectedFolderId.value === data.id) resetFolder();
    fetchFolders();
    fetchFiles();
  } catch {}
}

// ---- 文件操作 ----

function handleFileChange(file) { uploadFile.value = file.raw; }

async function handleUpload() {
  if (!uploadFile.value) { ElMessage.warning("请先选择文件"); return; }
  uploading.value = true;
  try {
    const fd = new FormData();
    fd.append("file", uploadFile.value);
    fd.append("category", uploadForm.value.category || "未分类");
    fd.append("tags", uploadForm.value.tags);
    fd.append("description", uploadForm.value.description);
    if (uploadForm.value.folder_id) fd.append("folder_id", uploadForm.value.folder_id);
    await api.post("/files/upload", fd);
    ElMessage.success("上传成功");
    showUpload.value = false;
    uploadForm.value = { folder_id: null, category: "", tags: "", description: "" };
    uploadFile.value = null;
    fetchFiles();
    fetchFolders();
    fetchCategories();
  } finally { uploading.value = false; }
}

function handleDownload(row) {
  window.open(`/api/files/${row.id}/download?token=${localStorage.getItem("token")}`);
}

function openEdit(row) {
  editFileId.value = row.id;
  editForm.value = { category: row.category, tags: Array.isArray(row.tags) ? row.tags.join(",") : row.tags, description: row.description };
  showEdit.value = true;
}

async function handleEditSave() {
  try {
    await api.put(`/files/${editFileId.value}`, {
      category: editForm.value.category,
      tags: editForm.value.tags.split(",").map(t => t.trim()).filter(Boolean),
      description: editForm.value.description,
    });
    ElMessage.success("更新成功");
    showEdit.value = false;
    fetchFiles();
    fetchCategories();
  } catch {}
}

function openMove(row) {
  moveFile.value = row;
  moveTargetId.value = row.folder_id;
  showMove.value = true;
}

async function handleMove() {
  try {
    await api.post(`/files/${moveFile.value.id}/move`, { folder_id: moveTargetId.value });
    ElMessage.success("移动成功");
    showMove.value = false;
    fetchFiles();
    fetchFolders();
  } catch {}
}

async function handleShare(row, forceRefresh) {
  shareFile.value = row;
  if (row.share_token && !forceRefresh) {
    shareToken.value = row.share_token;
  } else {
    try {
      const res = await api.post(`/files/${row.id}/share`);
      row.share_token = res.share_token;
      shareToken.value = res.share_token;
    } catch { return; }
  }
  showShare.value = true;
}

async function revokeShare(row) {
  try {
    await api.delete(`/files/${row.id}/share`);
    row.share_token = null;
    row.access_level = "private";
    shareToken.value = "";
    ElMessage.success("分享已撤销");
  } catch {}
}

function copyShareUrl() {
  navigator.clipboard.writeText(shareUrl.value);
  ElMessage.success("链接已复制");
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
    fetchFolders();
    fetchCategories();
  } catch {}
}

onMounted(() => {
  fetchFiles();
  fetchFolders();
  fetchCategories();
});
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.page-header h2 { margin: 0; }
.header-actions { display: flex; gap: 8px; }
.files-body { display: flex; gap: 12px; }
.folder-sidebar { width: 260px; flex-shrink: 0; }
.folder-card { height: 100%; }
.folder-card :deep(.el-card__body) { padding: 8px; }
.folder-node { display: flex; align-items: center; gap: 4px; width: 100%; }
.folder-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 13px; }
.folder-count { font-size: 11px; color: #999; }
.folder-actions { display: none; }
.folder-node:hover .folder-actions { display: flex; }
.files-main { flex: 1; min-width: 0; }
.file-name-cell { display: flex; align-items: center; gap: 6px; }
</style>

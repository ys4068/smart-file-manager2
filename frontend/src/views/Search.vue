<template>
  <div class="search-page">
    <h2>🔍 智能搜索</h2>

    <el-card class="search-bar">
      <el-input
        v-model="keyword"
        size="large"
        placeholder="输入关键词搜索文件和书签..."
        @keyup.enter="handleSearch"
        clearable
      >
        <template #prefix><el-icon><Search /></el-icon></template>
        <template #append>
          <el-button type="primary" :loading="searching" @click="handleSearch">全局搜索</el-button>
        </template>
      </el-input>
    </el-card>

    <!-- Smart Suggest -->
    <el-card v-if="suggestResult" class="suggest-card" style="margin-top: 16px">
      <template #header>💡 智能建议</template>
      <div class="suggest-content">
        <div class="suggest-item">
          <span class="suggest-label">推荐分类：</span>
          <el-tag type="success" size="large">{{ suggestResult.suggested_category }}</el-tag>
        </div>
        <div class="suggest-item">
          <span class="suggest-label">推荐标签：</span>
          <el-tag v-for="t in suggestResult.suggested_tags" :key="t" size="small" style="margin: 2px">{{ t }}</el-tag>
          <el-button size="small" type="primary" link @click="keyword = suggestResult.suggested_tags.join(' ')">使用这些标签</el-button>
        </div>
        <div class="suggest-item">
          <span class="suggest-label">关键词：</span>
          <el-tag v-for="k in suggestResult.keywords" :key="k" size="small" type="info" style="margin: 2px">{{ k }}</el-tag>
        </div>
      </div>
    </el-card>

    <!-- Results -->
    <div v-if="searched" style="margin-top: 16px">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="全部结果" name="all">
          <el-empty v-if="!resultFiles.length && !resultBookmarks.length" description="未找到相关结果" />
        </el-tab-pane>
        <el-tab-pane :label="`文件 (${resultFiles.length})`" name="files">
          <el-table :data="resultFiles" stripe>
            <el-table-column prop="original_name" label="文件名" min-width="200" />
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
            <el-table-column label="标签" width="180">
              <template #default="{ row }">
                <el-tag v-for="t in row.tags" :key="t" size="small" type="info" style="margin: 2px">{{ t }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button size="small" type="primary" link @click="handleDownload(row)">下载</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane :label="`书签 (${resultBookmarks.length})`" name="bookmarks">
          <el-table :data="resultBookmarks" stripe>
            <el-table-column prop="title" label="标题" min-width="200">
              <template #default="{ row }">
                <a :href="row.url" target="_blank">{{ row.title }}</a>
              </template>
            </el-table-column>
            <el-table-column prop="url" label="URL" min-width="200">
              <template #default="{ row }">
                <a :href="row.url" target="_blank" style="color: #999; font-size: 12px">{{ row.url }}</a>
              </template>
            </el-table-column>
            <el-table-column prop="category" label="分类" width="100">
              <template #default="{ row }">
                <el-tag size="small" type="success">{{ row.category }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- Quick suggest input -->
    <el-card v-else style="margin-top: 16px">
      <template #header>💡 智能分类推荐</template>
      <div style="display: flex; gap: 12px; align-items: center">
        <el-input v-model="suggestText" placeholder="输入文件名或标题，获取分类和标签建议..." style="flex: 1" />
        <el-button type="primary" :loading="suggesting" @click="handleSuggest">分析</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from "vue";
import api from "@/api";

const keyword = ref("");
const searching = ref(false);
const searched = ref(false);
const activeTab = ref("all");
const resultFiles = ref([]);
const resultBookmarks = ref([]);

const suggestText = ref("");
const suggesting = ref(false);
const suggestResult = ref(null);

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

async function handleSearch() {
  if (!keyword.value.trim()) return;
  searching.value = true;
  searched.value = true;
  try {
    const res = await api.get("/search", { params: { q: keyword.value } });
    resultFiles.value = res.files;
    resultBookmarks.value = res.bookmarks;

    // Also get suggest
    const suggestRes = await api.post("/search/suggest", { text: keyword.value });
    suggestResult.value = suggestRes;
  } finally {
    searching.value = false;
  }
}

async function handleSuggest() {
  if (!suggestText.value.trim()) return;
  suggesting.value = true;
  try {
    const res = await api.post("/search/suggest", { text: suggestText.value });
    suggestResult.value = res;
  } finally {
    suggesting.value = false;
  }
}

function handleDownload(row) {
  window.open(`/api/files/${row.id}/download?token=${localStorage.getItem("token")}`);
}
</script>

<style scoped>
.search-page h2 {
  margin-bottom: 16px;
}
.suggest-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.suggest-item {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.suggest-label {
  font-weight: bold;
  font-size: 14px;
  color: #666;
}
</style>

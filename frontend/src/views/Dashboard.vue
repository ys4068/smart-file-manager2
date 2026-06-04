<template>
  <div class="dashboard">
    <h2>📊 仪表盘</h2>
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #e6f7ff">
            <el-icon :size="32" color="#1890ff"><Folder /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ stats.total_files }}</div>
            <div class="stat-label">文件总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #fff7e6">
            <el-icon :size="32" color="#fa8c16"><Collection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ stats.total_bookmarks }}</div>
            <div class="stat-label">书签总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #f6ffed">
            <el-icon :size="32" color="#52c41a"><Star /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ stats.favorite_files }}</div>
            <div class="stat-label">收藏文件</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #fff0f6">
            <el-icon :size="32" color="#eb2f96"><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ stats.read_later_bookmarks }}</div>
            <div class="stat-label">待读书签</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>📁 文件类型分布</template>
          <div v-if="fileTypes.length" class="type-list">
            <div v-for="ft in fileTypes" :key="ft.type" class="type-item">
              <span>{{ typeLabel(ft.type) }}</span>
              <el-progress
                :percentage="Math.round((ft.count / totalFiles) * 100) || 0"
                :stroke-width="12"
                style="flex: 1; margin: 0 12px"
              />
              <span>{{ ft.count }}</span>
            </div>
          </div>
          <el-empty v-else description="暂无数据" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>📝 最近文件</template>
          <div v-if="recentFiles.length">
            <div v-for="f in recentFiles" :key="f.id" class="recent-item">
              <el-icon><Document /></el-icon>
              <span class="recent-name">{{ f.original_name }}</span>
              <span class="recent-time">{{ formatTime(f.created_at) }}</span>
            </div>
          </div>
          <el-empty v-else description="暂无文件" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "@/api";

const stats = ref({});
const fileTypes = ref([]);
const recentFiles = ref([]);
const totalFiles = ref(0);

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

function formatTime(t) {
  if (!t) return "";
  return new Date(t).toLocaleString("zh-CN");
}

onMounted(async () => {
  try {
    const res = await api.get("/dashboard");
    stats.value = res.stats;
    fileTypes.value = res.file_types;
    recentFiles.value = res.recent_files;
    totalFiles.value = res.stats.total_files;
  } catch {
    // handled by interceptor
  }
});
</script>

<style scoped>
.dashboard h2 {
  margin-bottom: 20px;
}
.stat-card {
  display: flex;
  align-items: center;
}
.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
}
.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}
.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 4px;
}
.type-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.type-item {
  display: flex;
  align-items: center;
}
.recent-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}
.recent-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.recent-time {
  font-size: 12px;
  color: #999;
}
</style>

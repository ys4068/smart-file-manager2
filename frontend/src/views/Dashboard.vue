<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20">
      <el-col :span="6" v-for="card in statCards" :key="card.key">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-left">
              <div class="stat-value">{{ card.value }}</div>
              <div class="stat-label">{{ card.label }}</div>
            </div>
            <div class="stat-icon" :style="{ background: card.color }">
              <el-icon :size="28"><component :is="card.icon" /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>📊 文件类型分布</template>
          <div v-if="stats.file_type_distribution && Object.keys(stats.file_type_distribution).length" class="chart-placeholder">
            <el-tag v-for="(count, type) in stats.file_type_distribution" :key="type"
              :type="tagType(type)" style="margin: 4px">
              {{ type }}: {{ count }}
            </el-tag>
          </div>
          <el-empty v-else description="暂无数据" :image-size="80" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>🏷️ 热门标签</template>
          <div v-if="stats.top_tags && stats.top_tags.length" class="chart-placeholder">
            <el-tag v-for="tag in stats.top_tags" :key="tag.name"
              :color="tag.color" effect="dark" style="margin: 4px">
              {{ tag.name }} ({{ tag.count }})
            </el-tag>
          </div>
          <el-empty v-else description="暂无数据" :image-size="80" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近活动 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>📅 最近7天</template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="新增文件">{{ stats.recent_files || 0 }}</el-descriptions-item>
            <el-descriptions-item label="新增书签">{{ stats.recent_bookmarks || 0 }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { statsAPI } from '@/api/modules'

const stats = ref({})

const statCards = reactive([
  { key: 'files', label: '文件总数', value: 0, icon: 'FolderOpened', color: '#409EFF' },
  { key: 'bookmarks', label: '书签总数', value: 0, icon: 'Collection', color: '#67C23A' },
  { key: 'tags', label: '标签总数', value: 0, icon: 'PriceTag', color: '#E6A23C' },
  { key: 'storage', label: '存储空间', value: '0 B', icon: 'Coin', color: '#F56C6C' },
])

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return `${size.toFixed(1)} ${units[i]}`
}

function tagType(type) {
  const map = { pdf: 'danger', doc: 'primary', docx: 'primary', xls: 'success', xlsx: 'success',
    ppt: 'warning', pptx: 'warning', png: '', jpg: '', jpeg: '', gif: '', zip: 'info', rar: 'info' }
  return map[type] || ''
}

onMounted(async () => {
  try {
    const res = await statsAPI.dashboard()
    stats.value = res.data
    statCards[0].value = res.data.total_files
    statCards[1].value = res.data.total_bookmarks
    statCards[2].value = res.data.total_tags
    statCards[3].value = formatBytes(res.data.total_storage_bytes)
  } catch { /* empty */ }
})
</script>

<style scoped>
.stat-card :deep(.el-card__body) { padding: 20px; }
.stat-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}
.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}
.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}
.chart-placeholder {
  min-height: 120px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}
</style>

import api from './index'

// ========== 认证 ==========
export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  getProfile: () => api.get('/auth/profile'),
  updateProfile: (data) => api.put('/auth/profile', data),
  logout: () => api.post('/auth/logout'),
  refreshToken: (token) => api.post('/auth/refresh', { refresh_token: token }),
}

// ========== 文件 ==========
export const filesAPI = {
  list: (params) => api.get('/files', { params }),
  upload: (formData) =>
    api.post('/files/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  get: (id) => api.get(`/files/${id}`),
  update: (id, data) => api.put(`/files/${id}`, data),
  delete: (id) => api.delete(`/files/${id}`),
  updateTags: (id, tagIds) => api.put(`/files/${id}/tags`, { tag_ids: tagIds }),
  suggest: (data) => api.post('/files/suggest', data),
  types: () => api.get('/files/types'),
  downloadUrl: (id) => `/api/files/${id}/download`,
}

// ========== 书签 ==========
export const bookmarksAPI = {
  list: (params) => api.get('/bookmarks', { params }),
  create: (data) => api.post('/bookmarks', data),
  import: (file) =>
    api.post('/bookmarks/import', file, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  get: (id) => api.get(`/bookmarks/${id}`),
  update: (id, data) => api.put(`/bookmarks/${id}`, data),
  delete: (id) => api.delete(`/bookmarks/${id}`),
  updateTags: (id, tagIds) => api.put(`/bookmarks/${id}/tags`, { tag_ids: tagIds }),
  categories: () => api.get('/bookmarks/categories'),
}

// ========== 标签 ==========
export const tagsAPI = {
  list: () => api.get('/tags'),
  create: (data) => api.post('/tags', data),
  update: (id, data) => api.put(`/tags/${id}`, data),
  delete: (id) => api.delete(`/tags/${id}`),
}

// ========== 统计 ==========
export const statsAPI = {
  dashboard: () => api.get('/stats/dashboard'),
}

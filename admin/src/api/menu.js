import apiClient from './client';

export const fetchMenuTree = async () => {
  const response = await apiClient.get('/admin/menu/tree');
  return response.data;
};

export const createCategory = async (payload) => {
  const response = await apiClient.post('/admin/menu/categories', payload);
  return response.data;
};

export const updateCategory = async (id, payload) => {
  const response = await apiClient.patch(`/admin/menu/categories/${id}`, payload);
  return response.data;
};

export const deleteCategory = async (id) => apiClient.delete(`/admin/menu/categories/${id}`);

export const createService = async (payload) => {
  const response = await apiClient.post('/admin/menu/services', payload);
  return response.data;
};

export const updateService = async (id, payload) => {
  const response = await apiClient.patch(`/admin/menu/services/${id}`, payload);
  return response.data;
};

export const deleteService = async (id) => apiClient.delete(`/admin/menu/services/${id}`);

export const uploadMenuImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await apiClient.post('/admin/menu/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const reorderCategories = async (parentId, items) => {
  await apiClient.post('/admin/menu/categories/reorder', {
    parent_id: parentId,
    items,
  });
};

export const reorderServices = async (categoryId, items) => {
  await apiClient.post('/admin/menu/services/reorder', {
    category_id: categoryId,
    items,
  });
};

export const bulkUpdateServices = async (payload) => {
  await apiClient.post('/admin/menu/services/bulk', payload);
};



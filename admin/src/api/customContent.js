import apiClient from './client';

export const fetchCustomContentBlocks = async () => {
  const response = await apiClient.get('/admin/custom-content');
  return response.data;
};

export const fetchCustomContentBlock = async (id) => {
  const response = await apiClient.get(`/admin/custom-content/${id}`);
  return response.data;
};

export const createCustomContentBlock = async (data) => {
  const response = await apiClient.post('/admin/custom-content', data);
  return response.data;
};

export const updateCustomContentBlock = async (id, data) => {
  const response = await apiClient.patch(`/admin/custom-content/${id}`, data);
  return response.data;
};

export const deleteCustomContentBlock = async (id) => {
  await apiClient.delete(`/admin/custom-content/${id}`);
};


import apiClient from './client';

export const fetchLoyaltyLevels = async () => {
  const response = await apiClient.get('/admin/loyalty/levels');
  return response.data;
};

export const createLoyaltyLevel = async (payload) => {
  const response = await apiClient.post('/admin/loyalty/levels', payload);
  return response.data;
};

export const updateLoyaltyLevel = async (levelId, payload) => {
  const response = await apiClient.patch(`/admin/loyalty/levels/${levelId}`, payload);
  return response.data;
};

export const deleteLoyaltyLevel = async (levelId) => {
  const response = await apiClient.delete(`/admin/loyalty/levels/${levelId}`);
  return response.data;
};

export const fetchLoyaltyBonuses = async () => {
  const response = await apiClient.get('/admin/loyalty/bonuses');
  return response.data;
};

export const createLoyaltyBonus = async (payload) => {
  const response = await apiClient.post('/admin/loyalty/bonuses', payload);
  return response.data;
};

export const updateLoyaltyBonus = async (bonusId, payload) => {
  const response = await apiClient.patch(`/admin/loyalty/bonuses/${bonusId}`, payload);
  return response.data;
};

export const deleteLoyaltyBonus = async (bonusId) => {
  const response = await apiClient.delete(`/admin/loyalty/bonuses/${bonusId}`);
  return response.data;
};

export const adjustUserLoyalty = async (userId, payload) => {
  const response = await apiClient.post(`/admin/loyalty/users/${userId}/adjust`, payload);
  return response.data;
};

export const fetchLoyaltySettings = async () => {
  const response = await apiClient.get('/admin/loyalty/settings');
  return response.data;
};

export const updateLoyaltySettings = async (payload) => {
  const response = await apiClient.patch('/admin/loyalty/settings', payload);
  return response.data;
};

export const getUserByCode = async (uniqueCode) => {
  const response = await apiClient.get(`/admin/loyalty/users/by-code/${uniqueCode}`);
  return response.data;
};
import apiClient, { setAuthToken } from './client';

export const fetchInvites = async () => {
  const response = await apiClient.get('/admin/auth/invites');
  return response.data.invites ?? [];
};

export const createInvite = async (payload) => {
  const response = await apiClient.post('/admin/auth/invite', payload);
  return response.data;
};

export const getInviteByToken = async (token) => {
  const response = await apiClient.get(`/admin/auth/invite/${token}`);
  return response.data;
};

export const acceptInvite = async (token, password) => {
  const response = await apiClient.post('/admin/auth/accept', { token, password });
  const { access_token: accessToken } = response.data;
  if (accessToken) {
    setAuthToken(accessToken);
  }
  return response.data;
};



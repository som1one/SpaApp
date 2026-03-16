import apiClient, { setAuthToken } from './client';

export const login = async (email, password) => {
  const response = await apiClient.post('/admin/auth/login', {
    email,
    password,
  }, {
    timeout: 15000, // 15 секунд для логина
  });
  const token = response.data?.access_token;
  if (token) {
    setAuthToken(token);
    apiClient.defaults.headers.Authorization = `Bearer ${token}`;
  }
  return token;
};

export const logout = () => {
  setAuthToken(null);
};

export const fetchCurrentUser = async () => {
  const response = await apiClient.get('/admin/auth/me', {
    timeout: 10000, // 10 секунд для получения профиля
  });
  return response.data;
};



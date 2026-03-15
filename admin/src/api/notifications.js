import apiClient from './client';

export const fetchNotifications = async ({
  status,
  page = 1,
  pageSize = 20,
} = {}) => {
  const response = await apiClient.get('/admin/notifications', {
    params: {
      status_filter: status,
      limit: pageSize,
      offset: (page - 1) * pageSize,
    },
  });
  return response.data;
};

export const createNotification = async (payload) => {
  const response = await apiClient.post('/admin/notifications', payload);
  return response.data;
};

export const updateNotificationStatus = async (id, status) => {
  const response = await apiClient.patch(`/admin/notifications/${id}`, null, {
    params: { new_status: status },
  });
  return response.data;
};


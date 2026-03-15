import apiClient from './client';

export const fetchAudit = async ({
  action,
  adminId,
  page = 1,
  pageSize = 30,
} = {}) => {
  const response = await apiClient.get('/admin/audit', {
    params: {
      action,
      admin_id: adminId,
      limit: pageSize,
      offset: (page - 1) * pageSize,
    },
  });
  return response.data;
};


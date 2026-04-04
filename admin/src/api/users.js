import apiClient from './client';

export const fetchUsers = async ({
  search,
  isActive,
  isVerified,
  minLoyalty,
  sortBy,
  sortDir,
  page = 1,
  pageSize = 20,
} = {}) => {
  const response = await apiClient.get('/admin/users', {
    params: {
      search,
      is_active: isActive,
      is_verified: isVerified,
      min_loyalty: minLoyalty,
      sort_by: sortBy,
      sort_dir: sortDir,
      limit: pageSize,
      offset: (page - 1) * pageSize,
    },
  });
  return response.data;
};

export const exportUsersExcel = async ({
  search,
  isActive,
  isVerified,
  minLoyalty,
  sortBy,
  sortDir,
} = {}) => {
  const response = await apiClient.get('/admin/users/export', {
    params: {
      search,
      is_active: isActive,
      is_verified: isVerified,
      min_loyalty: minLoyalty,
      sort_by: sortBy,
      sort_dir: sortDir,
    },
    responseType: 'blob',
  });
  return response.data;
};

export const fetchUserYclientsSnapshot = async (userId) => {
  const response = await apiClient.get(`/admin/users/${userId}/yclients`);
  return response.data;
};

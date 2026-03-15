import axios from './client';

export const fetchStaff = async () => {
  const response = await axios.get('/admin/staff');
  return response.data;
};

export const fetchStaffById = async (id) => {
  const response = await axios.get(`/admin/staff/${id}`);
  return response.data;
};

export const createStaff = async (data) => {
  const response = await axios.post('/admin/staff', data);
  return response.data;
};

export const updateStaff = async (id, data) => {
  const response = await axios.patch(`/admin/staff/${id}`, data);
  return response.data;
};

export const deleteStaff = async (id) => {
  await axios.delete(`/admin/staff/${id}`);
};

export const fetchStaffSchedules = async (staffId) => {
  const response = await axios.get(`/admin/staff/${staffId}/schedules`);
  return response.data;
};

export const createStaffSchedule = async (data) => {
  const response = await axios.post('/admin/staff/schedules', data);
  return response.data;
};

export const updateStaffSchedule = async (scheduleId, data) => {
  const response = await axios.patch(`/admin/staff/schedules/${scheduleId}`, data);
  return response.data;
};

export const deleteStaffSchedule = async (scheduleId) => {
  await axios.delete(`/admin/staff/schedules/${scheduleId}`);
};

export const createStaffService = async (data) => {
  const response = await axios.post('/admin/staff/services', data);
  return response.data;
};

export const deleteStaffService = async (staffServiceId) => {
  await axios.delete(`/admin/staff/services/${staffServiceId}`);
};


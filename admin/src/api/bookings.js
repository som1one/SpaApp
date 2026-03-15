import apiClient from './client';

export const fetchBookings = async ({
  status,
  search,
  userId,
  dateFrom,
  dateTo,
  page = 1,
  pageSize = 20,
} = {}) => {
  const response = await apiClient.get('/admin/bookings', {
    params: {
      status,
      search,
      user_id: userId,
      date_from: dateFrom,
      date_to: dateTo,
      limit: pageSize,
      offset: (page - 1) * pageSize,
    },
  });
  return response.data;
};

export const updateBookingStatus = async (bookingId, payload) => {
  const response = await apiClient.patch(`/admin/bookings/${bookingId}`, payload);
  return response.data;
};

export const confirmBookingPayment = async (bookingId, payload) => {
  const response = await apiClient.post(`/admin/bookings/${bookingId}/confirm-payment`, payload);
  return response.data;
};


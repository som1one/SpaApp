import axios from './client';

export const fetchServices = async () => {
  const response = await axios.get('/services');
  return response.data;
};


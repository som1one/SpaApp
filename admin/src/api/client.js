import axios from 'axios';

// Базовый URL API бэкенда.
// В production/на сервере укажи VITE_API_BASE_URL в .env / docker-compose, например:
//   VITE_API_BASE_URL=https://api.priroda-spa.ru/api/v1
// По умолчанию (если переменная не задана) подключаемся к прод-серверу:
//   http://194.87.187.146:9003/api/v1
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://194.87.187.146:9003/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000, 
});

export const setAuthToken = (token) => {
  if (token) {
    localStorage.setItem('admin_token', token);
  } else {
    localStorage.removeItem('admin_token');
  }
};

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      error.message = 'Превышено время ожидания. Проверьте подключение к интернету.';
    } else if (error.response) {
      const status = error.response.status;
      if (status === 401) {
        error.message = 'Сессия истекла. Пожалуйста, войдите снова.';
        localStorage.removeItem('admin_token');
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      } else if (status === 403) {
        error.message = 'Недостаточно прав для выполнения этого действия.';
      } else if (status === 422) {
        // Детальная обработка ошибок валидации
        const detail = error.response.data?.detail;
        if (Array.isArray(detail)) {
          // Форматируем ошибки валидации Pydantic
          const messages = detail.map((err) => {
            const field = err.loc?.join('.') || 'неизвестное поле';
            const msg = err.msg || 'неизвестная ошибка';
            const type = err.type || '';
            return `${field}: ${msg}${type ? ` (${type})` : ''}`;
          });
          error.message = `Ошибка валидации:\n${messages.join('\n')}`;
          // Сохраняем детали для более детального отображения
          error.validationErrors = detail;
        } else if (typeof detail === 'string') {
          error.message = detail;
        } else {
          error.message = error.response.data?.message || `Ошибка валидации (422)`;
        }
        // Логируем детали для отладки
        console.error('422 Validation Error:', {
          url: error.config?.url,
          method: error.config?.method,
          data: error.config?.data,
          response: error.response.data,
        });
      } else if (status >= 500) {
        error.message = 'Ошибка сервера. Попробуйте позже.';
      } else {
        error.message = error.response.data?.detail || error.response.data?.message || `Ошибка ${status}`;
      }
    } else if (error.request) {
      error.message = 'Не удалось подключиться к серверу. Проверьте подключение к интернету и убедитесь, что сервер запущен.';
    }
    return Promise.reject(error);
  }
);

export default apiClient;



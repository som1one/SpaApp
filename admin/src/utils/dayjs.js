import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';

// Подключаем плагины
dayjs.extend(utc);
dayjs.extend(timezone);

// Функция для форматирования времени в московском часовом поясе
export const formatMoscowTime = (date, format = 'DD MMM HH:mm') => {
  if (!date) return '—';
  // Если дата уже в UTC или с timezone, конвертируем в Москву
  // Если без timezone, предполагаем что это уже московское время
  const dt = dayjs(date);
  if (dt.isValid()) {
    // Если есть информация о timezone, конвертируем
    if (dt.format('Z') !== '+00:00' || dt.isUTC()) {
      return dt.tz('Europe/Moscow').format(format);
    }
    // Иначе просто форматируем (предполагаем что уже московское)
    return dt.format(format);
  }
  return '—';
};

// Функция для получения текущего времени в Москве
export const moscowNow = () => {
  return dayjs().tz('Europe/Moscow');
};

// Экспортируем настроенный dayjs
export default dayjs;


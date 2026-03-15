FROM node:20-alpine

WORKDIR /app

# Устанавливаем зависимости
COPY admin/package.json admin/package-lock.json* ./ 
RUN npm install --legacy-peer-deps

# Копируем исходники админки
COPY admin ./admin
WORKDIR /app/admin

# Экспонируем порт dev-сервера Vite
EXPOSE 3001

# Запускаем Vite в dev-режиме, доступен снаружи
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3001"]



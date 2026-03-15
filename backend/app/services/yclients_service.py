"""
Сервис для интеграции с YClients API
"""
import logging
import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from app.core.config import settings

logger = logging.getLogger(__name__)


class YClientsService:
    """Сервис для работы с YClients API"""
    
    BASE_URL = "https://api.yclients.com/api/v1"
    
    def __init__(self):
        self.company_id: Optional[int] = None
        self.api_token: Optional[str] = None
        self.user_token: Optional[str] = None
        
    def configure(self, company_id: int, api_token: str, user_token: str):
        """Настройка параметров YClients"""
        if not company_id:
            raise ValueError("YClients company_id is required")
        if not api_token or not api_token.strip():
            raise ValueError("YClients api_token is required and cannot be empty")
        if not user_token or not user_token.strip():
            raise ValueError("YClients user_token is required and cannot be empty")
        
        self.company_id = company_id
        self.api_token = api_token.strip()
        self.user_token = user_token.strip()
        
        logger.debug(
            "YClients настроен: company_id=%s, api_token_length=%s, user_token_length=%s",
            self.company_id,
            len(self.api_token),
            len(self.user_token)
        )
    
    def _get_headers(self, include_user_token_in_header: bool = True) -> Dict[str, str]:
        """Получить заголовки для запросов
        
        Args:
            include_user_token_in_header: Если True, добавляет User-Token в заголовки.
                                         Если False, User-Token нужно передавать в URL параметрах.
        """
        if not self.api_token:
            raise ValueError("YClients api_token not configured. Call configure() first.")
        
        if include_user_token_in_header and not self.user_token:
            raise ValueError("YClients user_token not configured. Call configure() first.")

        # Очищаем токены от пробелов в начале и конце
        api_token_str = str(self.api_token).strip()
        user_token_str = str(self.user_token).strip() if self.user_token else ""

        # Проверяем, что токены не пустые
        if not api_token_str:
            logger.error(
                "API токен YClients пустой. Проверьте настройку YCLIENTS_API_TOKEN."
            )
            raise ValueError("YClients API token is empty. Check configuration.")
        
        if include_user_token_in_header and not user_token_str:
            logger.error(
                "User токен YClients пустой. Проверьте настройку YCLIENTS_USER_TOKEN."
            )
            raise ValueError("YClients user token is empty. Check configuration.")

        # Формируем заголовки согласно документации YClients
        # Authorization: Bearer {api_token}
        # User-Token: {user_token} (отдельный заголовок) - ИЛИ в URL параметрах
        auth_header = f"Bearer {api_token_str}"

        # Жёстко валидируем, что заголовок можно закодировать в ASCII (требование HTTP)
        try:
            auth_header.encode("ascii")
            if user_token_str:
                user_token_str.encode("ascii")
        except UnicodeEncodeError as e:
            # Находим проблемные символы для наглядной диагностики
            bad_chars = []
            try:
                auth_header.encode("ascii")
            except UnicodeEncodeError:
                bad_chars.extend([
                    f"api_token pos {idx}: {repr(ch)} (U+{ord(ch):04X})"
                    for idx, ch in enumerate(api_token_str)
                    if ord(ch) > 127
                ])
            if user_token_str:
                try:
                    user_token_str.encode("ascii")
                except UnicodeEncodeError:
                    bad_chars.extend([
                        f"user_token pos {idx}: {repr(ch)} (U+{ord(ch):04X})"
                        for idx, ch in enumerate(user_token_str)
                        if ord(ch) > 127
                    ])
            logger.error(
                "YClients токены содержат недопустимые (non-ASCII) символы: %s. "
                "Проверьте, что переменные окружения YCLIENTS_API_TOKEN и YCLIENTS_USER_TOKEN "
                "скопированы из кабинета YClients без кавычек и лишних символов.",
                "; ".join(bad_chars) or "unknown chars",
            )
            # Поднимаем осмысленную ошибку конфигурации вместо UnicodeEncodeError внутри httpx
            raise ValueError(
                "YClients tokens contain non-ASCII characters. "
                "Fix YCLIENTS_API_TOKEN / YCLIENTS_USER_TOKEN in .env"
            ) from e

        headers = {
            "Authorization": auth_header,
            "Accept": "application/vnd.api.v2+json",  # Используем формат из документации YClients
            "Content-Type": "application/json",
        }
        
        # User-Token может быть в заголовках ИЛИ в URL параметрах
        if include_user_token_in_header and user_token_str:
            headers["User-Token"] = user_token_str
        
        # Логируем заголовки для отладки (без токенов)
        logger.debug(
            f"YClients headers: Authorization=Bearer ***, "
            f"User-Token in header={include_user_token_in_header}, "
            f"User-Token length={len(user_token_str) if user_token_str else 0}, "
            f"Accept={headers['Accept']}"
        )
        
        return headers
    
    def _get_url_params_with_token(self, existing_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Получить параметры URL с User Token
        
        Args:
            existing_params: Существующие параметры URL
            
        Returns:
            Словарь параметров с добавленным user_token
        """
        if not self.user_token:
            raise ValueError("YClients user_token not configured. Call configure() first.")
        
        params = existing_params.copy() if existing_params else {}
        params["user_token"] = str(self.user_token).strip()
        return params
    
    async def get_available_dates(
        self,
        service_id: int,
        staff_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Получить доступные даты для записи
        
        Args:
            service_id: ID услуги в YClients
            staff_id: ID мастера (опционально)
            date_from: Начальная дата (по умолчанию сегодня)
            date_to: Конечная дата (по умолчанию +30 дней)
        
        Returns:
            Список доступных дат со слотами времени
        """
        if not self.company_id or not self.api_token or not self.user_token:
            logger.warning("YClients не настроен")
            return []
        
        try:
            # YClients API для получения доступных дат
            # Формат может отличаться, используем общий подход
            url = f"{self.BASE_URL}/book_dates/{self.company_id}"
            
            # Формируем параметры запроса
            params = {}
            
            # YClients может требовать service_ids как массив
            if service_id:
                params["service_ids[]"] = str(service_id)
            
            if staff_id:
                params["staff_id"] = str(staff_id)
            
            if date_from:
                params["date_from"] = date_from.isoformat()
            else:
                params["date_from"] = date.today().isoformat()
            
            if date_to:
                params["date_to"] = date_to.isoformat()
            else:
                from datetime import timedelta
                params["date_to"] = (date.today() + timedelta(days=30)).isoformat()
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    url,
                    headers=self._get_headers(),
                    params=params,
                )
                response.raise_for_status()
                data = response.json()
                
                # YClients может возвращать данные в разных форматах
                # Пытаемся обработать оба варианта
                result = []
                
                if "data" in data:
                    dates_data = data["data"]
                    if isinstance(dates_data, dict):
                        # Формат: {"2024-01-15": {"times": ["10:00", ...]}, ...}
                        for date_str, slots in dates_data.items():
                            if isinstance(slots, dict):
                                times = slots.get("times", [])
                            elif isinstance(slots, list):
                                times = slots
                            else:
                                times = []
                            
                            result.append({
                                "date": date_str,
                                "times": times if isinstance(times, list) else [],
                            })
                    elif isinstance(dates_data, list):
                        # Формат: [{"date": "2024-01-15", "times": [...]}, ...]
                        for item in dates_data:
                            if isinstance(item, dict):
                                result.append({
                                    "date": item.get("date", ""),
                                    "times": item.get("times", []),
                                })
                
                return result
                
        except Exception as e:
            logger.error(f"Ошибка получения доступных дат из YClients: {e}", exc_info=True)
            return []
    
    async def create_booking(
        self,
        service_id: int,
        datetime_str: str,
        client_name: str,
        client_phone: str,
        client_email: Optional[str] = None,
        staff_id: Optional[int] = None,
        comment: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Создать запись в YClients
        
        Args:
            service_id: ID услуги в YClients
            datetime_str: Дата и время в формате "YYYY-MM-DD HH:MM"
            client_name: Имя клиента
            client_phone: Телефон клиента
            client_email: Email клиента (опционально)
            staff_id: ID мастера (опционально)
            comment: Комментарий (опционально)
        
        Returns:
            Данные созданной записи или None при ошибке
        """
        if not self.company_id or not self.api_token or not self.user_token:
            logger.warning("YClients не настроен")
            return None
        
        try:
            url = f"{self.BASE_URL}/book_record/{self.company_id}"
            
            # Парсим дату и время
            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
            
            payload = {
                "company_id": self.company_id,
                "services": [{"id": service_id}],
                "date": dt.strftime("%Y-%m-%d"),
                "time": dt.strftime("%H:%M"),
                "client": {
                    "name": client_name,
                    "phone": client_phone,
                },
            }
            
            if client_email:
                payload["client"]["email"] = client_email
            
            if staff_id:
                payload["staff_id"] = staff_id
            
            if comment:
                payload["comment"] = comment
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    headers=self._get_headers(),
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                
                if "data" in data:
                    logger.info(f"Запись создана в YClients: {data['data']}")
                    return data["data"]
                
                return None
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP ошибка при создании записи в YClients: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Ошибка создания записи в YClients: {e}", exc_info=True)
            return None
    
    async def get_services(self) -> List[Dict[str, Any]]:
        """
        Получить список услуг из YClients
        
        Returns:
            Список услуг
        """
        if not self.company_id or not self.api_token or not self.user_token:
            logger.warning("YClients не настроен")
            return []
        
        try:
            # Пробуем сначала без lang=ru (как в рабочем примере test_yclients_auth.py)
            url = f"{self.BASE_URL}/company/{self.company_id}/services"
            logger.info(f"YClients get_services: URL = {url}")
            
            # Пробуем разные варианты: сначала с User-Token в заголовках, потом в URL
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Вариант 1: User-Token в заголовках
                headers = self._get_headers(include_user_token_in_header=True)
                logger.debug(f"YClients get_services: Headers = {list(headers.keys())}")
                response = await client.get(url, headers=headers)
                
                # Логируем детали ошибки для диагностики
                if response.status_code != 200:
                    logger.warning(
                        f"Ошибка получения услуг (User-Token в заголовках): {response.status_code}. "
                        f"URL: {url}, Response: {response.text[:500]}"
                    )
                    
                    # Вариант 2: User-Token в URL параметрах
                    if response.status_code == 401:
                        logger.info("Пробуем передать user_token в URL параметрах...")
                        params = self._get_url_params_with_token()
                        headers_url = self._get_headers(include_user_token_in_header=False)
                        response = await client.get(url, headers=headers_url, params=params)
                        if response.status_code == 200:
                            logger.info("✅ User-Token в URL параметрах сработал!")
                        else:
                            logger.warning(f"User-Token в URL тоже не сработал: {response.status_code}")
                    
                    # Вариант 3: С lang=ru параметром
                    if response.status_code in [400, 401]:
                        logger.info("Пробуем с параметром lang=ru...")
                        params = {"lang": "ru"}
                        if response.status_code == 401:
                            # Если была 401, пробуем user_token в URL + lang=ru
                            params = self._get_url_params_with_token(params)
                            headers_lang = self._get_headers(include_user_token_in_header=False)
                        else:
                            headers_lang = headers
                        url_with_lang = f"{url}?lang=ru"
                        response_alt = await client.get(url_with_lang, headers=headers_lang, params=params if params else None)
                        if response_alt.status_code == 200:
                            logger.info("✅ Запрос с lang=ru успешен!")
                            response = response_alt
                        else:
                            logger.warning(f"Запрос с lang=ru тоже не сработал: {response_alt.status_code}")
                
                response.raise_for_status()
                data = response.json()
                
                if "data" in data:
                    return data["data"]
                
                return []
                
        except Exception as e:
            logger.error(f"Ошибка получения услуг из YClients: {e}", exc_info=True)
            return []
    
    async def get_staff(self) -> List[Dict[str, Any]]:
        """
        Получить список мастеров из YClients
        
        Returns:
            Список мастеров
        """
        if not self.company_id or not self.api_token or not self.user_token:
            logger.warning("YClients не настроен")
            return []
        
        try:
            # Согласно документации, нужен слэш в конце и параметр lang=ru
            url = f"{self.BASE_URL}/company/{self.company_id}/staff/?lang=ru"
            headers = self._get_headers()
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    url,
                    headers=headers,
                )
                
                # Логируем детали ошибки для диагностики
                if response.status_code != 200:
                    logger.error(
                        f"Ошибка получения мастеров: {response.status_code}. "
                        f"URL: {url}, Response: {response.text[:500]}"
                    )
                
                response.raise_for_status()
                data = response.json()
                
                # YClients может вернуть массив напрямую или в поле "data"
                if isinstance(data, list):
                    return data
                elif "data" in data:
                    return data["data"]
                
                return []
                
        except Exception as e:
            logger.error(f"Ошибка получения мастеров из YClients: {e}", exc_info=True)
            return []
    
    async def get_bookings(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        client_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Получить записи из YClients
        
        Args:
            date_from: Начальная дата (по умолчанию сегодня)
            date_to: Конечная дата (по умолчанию +30 дней)
            client_id: ID клиента в YClients (опционально)
        
        Returns:
            Список записей
        """
        if not self.company_id or not self.api_token or not self.user_token:
            logger.warning("YClients не настроен")
            return []
        
        try:
            url = f"{self.BASE_URL}/records/{self.company_id}"
            
            params = {}
            if date_from:
                params["date_from"] = date_from.isoformat()
            else:
                from datetime import timedelta
                params["date_from"] = date.today().isoformat()
            
            if date_to:
                params["date_to"] = date_to.isoformat()
            else:
                from datetime import timedelta
                params["date_to"] = (date.today() + timedelta(days=30)).isoformat()
            
            if client_id:
                params["client_id"] = str(client_id)
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    url,
                    headers=self._get_headers(),
                    params=params,
                )
                response.raise_for_status()
                data = response.json()
                
                if "data" in data:
                    return data["data"] if isinstance(data["data"], list) else []
                
                return []
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP ошибка при получении записей из YClients: {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"Ошибка получения записей из YClients: {e}", exc_info=True)
            return []
    
    async def get_booking_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить конкретную запись по ID из YClients
        
        Args:
            record_id: ID записи в YClients
        
        Returns:
            Данные записи или None
        """
        if not self.company_id or not self.api_token or not self.user_token:
            logger.warning("YClients не настроен")
            return None
        
        try:
            url = f"{self.BASE_URL}/records/{self.company_id}/{record_id}"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    url,
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                data = response.json()
                
                if "data" in data:
                    return data["data"]
                
                return None
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP ошибка при получении записи {record_id} из YClients: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Ошибка получения записи {record_id} из YClients: {e}", exc_info=True)
            return None
    
    async def cancel_booking(self, record_id: int, reason: Optional[str] = None) -> bool:
        """
        Отменить запись в YClients
        
        Args:
            record_id: ID записи в YClients
            reason: Причина отмены (опционально)
        
        Returns:
            True если успешно, False при ошибке
        """
        if not self.company_id or not self.api_token or not self.user_token:
            logger.warning("YClients не настроен")
            return False
        
        try:
            # YClients API для отмены записи: DELETE /api/v1/records/{company_id}/{record_id}
            url = f"{self.BASE_URL}/records/{self.company_id}/{record_id}"
            
            payload = {}
            if reason:
                payload["comment"] = reason
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.delete(
                    url,
                    headers=self._get_headers(),
                    json=payload if payload else None,
                )
                
                if response.status_code == 404:
                    logger.warning(f"Запись {record_id} не найдена в YClients (404)")
                    return False
                
                response.raise_for_status()
                logger.info(f"Запись {record_id} успешно отменена в YClients")
                return True
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP ошибка при отмене записи {record_id} в YClients: {e.response.status_code} - {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Ошибка отмены записи {record_id} в YClients: {e}", exc_info=True)
            return False
    
    async def get_staff_with_schedule(self) -> Dict[int, Dict[str, Any]]:
        """
        Получить мастеров с их расписанием из YClients.
        Возвращает только тех мастеров, у которых есть расписание.
        Использует альтернативные методы если прямой доступ к /staff недоступен.
        
        Returns:
            Словарь {staff_id: {staff_info, schedule: [...]}}
        """
        if not self.company_id or not self.api_token or not self.user_token:
            logger.warning("YClients не настроен")
            return {}
        
        result = {}
        
        # Метод 1: Пытаемся получить список мастеров (может вернуть 403)
        try:
            staff_list = await self.get_staff()
            logger.info(f"Получен список из {len(staff_list)} мастеров через /staff")
            for staff_member in staff_list:
                staff_id = staff_member.get("id")
                if not staff_id:
                    continue
                
                # Пробуем получить расписание для этого мастера
                schedule = await self._get_staff_schedule_from_seances(staff_id)
                if schedule:
                    result[staff_id] = {
                        "staff_info": staff_member,
                        "schedule": schedule,
                    }
        except Exception as e:
            logger.debug(f"Метод 1: Не удалось получить список мастеров напрямую: {e}")
        
        # Метод 2: Извлекаем мастеров из доступных слотов (через book_dates)
        # Этот метод работает даже если /staff недоступен
        logger.info("Пробуем извлечь мастеров через доступные слоты...")
        try:
            staff_from_slots = await self._extract_staff_from_available_slots()
            for staff_id, staff_data in staff_from_slots.items():
                if staff_id not in result:
                    result[staff_id] = staff_data
            if staff_from_slots:
                logger.info(f"Найдено {len(staff_from_slots)} мастеров через доступные слоты")
            else:
                logger.warning("Метод 2: Не найдено мастеров через доступные слоты")
        except Exception as e:
            logger.warning(f"Метод 2: Не удалось извлечь мастеров из слотов: {e}", exc_info=True)
        
        # Метод 3: Извлекаем мастеров из услуг и проверяем их расписание
        logger.info("Пробуем извлечь мастеров из услуг...")
        try:
            services = await self.get_services()
            staff_from_services = {}
            staff_ids_found = set()
            
            # Собираем все уникальные ID мастеров из услуг
            for service in services:
                # Услуги могут иметь массив мастеров
                service_staff = service.get("staff", [])
                if isinstance(service_staff, list):
                    for staff_item in service_staff:
                        staff_id = staff_item.get("id") if isinstance(staff_item, dict) else staff_item
                        if staff_id:
                            staff_ids_found.add(staff_id)
                
                # Также может быть поле staff_id напрямую
                service_staff_id = service.get("staff_id")
                if service_staff_id:
                    staff_ids_found.add(service_staff_id)
            
            logger.info(f"Найдено {len(staff_ids_found)} уникальных ID мастеров из услуг")
            
            # Для каждого мастера пытаемся получить расписание
            for staff_id in staff_ids_found:
                if staff_id in result:
                    # Уже есть в результате из предыдущих методов
                    continue
                
                try:
                    # Сначала пробуем официальный эндпоинт /schedule
                    schedule = await self._get_staff_schedule_from_seances(staff_id)
                    
                    # Если не получилось, пробуем через доступные слоты (fallback)
                    if not schedule:
                        schedule = await self._extract_schedule_from_available_slots(staff_id)
                    
                    # Добавляем мастера даже если расписание не найдено (но хотя бы попытались получить)
                    # Если /book_dates вернул 200 OK, значит мастер есть и работает, просто расписание не распарсилось
                    staff_from_services[staff_id] = {
                        "staff_info": {"id": staff_id},
                        "schedule": schedule if schedule else [],  # Пустой список, если расписание не найдено
                    }
                    
                    if schedule:
                        logger.info(f"✓ Найдено расписание для мастера {staff_id}: {len(schedule)} дней")
                    else:
                        logger.debug(f"Мастер {staff_id} найден, но расписание не извлечено (возможно, формат ответа неожиданный)")
                except Exception as e:
                    logger.debug(f"Ошибка получения расписания для мастера {staff_id}: {e}")
                    continue
            
            # Добавляем найденных мастеров в результат
            for staff_id, staff_data in staff_from_services.items():
                if staff_id not in result:
                    result[staff_id] = staff_data
            
            if staff_from_services:
                logger.info(f"Успешно извлечено {len(staff_from_services)} мастеров с расписанием через услуги")
            else:
                logger.warning(f"Метод 3: Найдено {len(staff_ids_found)} мастеров в услугах, но ни у одного нет расписания")
        except Exception as e:
            logger.warning(f"Метод 3: Не удалось извлечь мастеров из услуг: {e}", exc_info=True)
        
        if not result:
            logger.warning("Не удалось получить мастеров ни одним из методов. Проверьте права доступа API токенов.")
        
        return result
    
    async def _get_staff_schedule_from_seances(self, staff_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Получить расписание мастера через официальный эндпоинт /schedule/{company_id}/{staff_id}.
        
        Args:
            staff_id: ID мастера в YClients
        
        Returns:
            Список расписаний по дням недели или None
        """
        if not self.company_id or not self.api_token or not self.user_token:
            return None
        
        from datetime import timedelta
        
        # Получаем расписание на ближайшие 2 недели
        today = date.today()
        end_date = today + timedelta(days=14)
        
        try:
            # Согласно документации YClients: GET /api/v1/schedule/{company_id}/{staff_id}
            url = f"{self.BASE_URL}/schedule/{self.company_id}/{staff_id}"
            params = {
                "start_date": today.isoformat(),
                "end_date": end_date.isoformat(),
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    url,
                    headers=self._get_headers(),
                    params=params,
                )
                
                if response.status_code == 404:
                    logger.debug(f"Расписание для мастера {staff_id} не найдено (404)")
                    return None
                
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"Получено расписание для мастера {staff_id}: keys={list(data.keys())[:5] if isinstance(data, dict) else 'not dict'}")
                
                # Обрабатываем ответ согласно документации
                # Формат: {"timetable": [...], "appointments": [...]}
                timetable = data.get("timetable", [])
                
                if not timetable:
                    logger.debug(f"Нет расписания (timetable) для мастера {staff_id}")
                    return None
                
                # Конвертируем расписание в наш формат
                schedule_items = self._parse_timetable_to_schedule(timetable, staff_id)
                
                if schedule_items:
                    logger.info(f"✓ Найдено расписание для мастера {staff_id}: {len(schedule_items)} дней")
                    return schedule_items
                else:
                    logger.warning(f"Не удалось распарсить расписание для мастера {staff_id}")
                    return None
                    
        except httpx.HTTPStatusError as e:
            logger.debug(f"HTTP ошибка при получении расписания для мастера {staff_id}: {e.response.status_code}")
            if e.response.status_code == 403:
                logger.warning(f"Нет прав на получение расписания для мастера {staff_id} (403). Проверьте User-Token.")
            return None
        except Exception as e:
            logger.debug(f"Ошибка при получении расписания для мастера {staff_id}: {e}")
            return None
    
    def _parse_timetable_to_schedule(self, timetable: List[Dict[str, Any]], staff_id: int) -> List[Dict[str, Any]]:
        """
        Конвертирует данные timetable из YClients в формат расписания по дням недели.
        
        Согласно документации, формат:
        {
          "timetable": [
            {
              "date": "2025-11-20",
              "start": "10:00",
              "end": "18:00",
              "breaks": []
            }
          ]
        }
        
        Args:
            timetable: Список записей расписания из YClients
            staff_id: ID мастера
        
        Returns:
            Список расписаний по дням недели
        """
        from datetime import datetime
        
        # Группируем по дням недели
        schedule_by_day = {}
        
        for entry in timetable:
            date_str = entry.get("date")
            start_time = entry.get("start", "09:00")
            end_time = entry.get("end", "18:00")
            breaks = entry.get("breaks", [])
            
            if not date_str:
                continue
            
            # Парсим дату для определения дня недели
            try:
                if isinstance(date_str, str):
                    dt = datetime.strptime(date_str, "%Y-%m-%d").date()
                else:
                    dt = date_str
                
                day_of_week = dt.weekday()  # 0 = Monday, 6 = Sunday
                
                # Обрабатываем перерывы
                break_start = None
                break_end = None
                if breaks and isinstance(breaks, list) and len(breaks) > 0:
                    # Берем первый перерыв (обычно один обеденный)
                    first_break = breaks[0]
                    if isinstance(first_break, dict):
                        break_start = first_break.get("start") or first_break.get("start_time")
                        break_end = first_break.get("end") or first_break.get("end_time")
                
                # Создаём или обновляем расписание для этого дня
                if day_of_week not in schedule_by_day:
                    schedule_by_day[day_of_week] = {
                        "day_of_week": day_of_week,
                        "start_time": start_time,
                        "end_time": end_time,
                        "break_start": break_start,
                        "break_end": break_end,
                    }
                else:
                    # Обновляем время начала/окончания (берём самое раннее/позднее)
                    existing = schedule_by_day[day_of_week]
                    if start_time < existing["start_time"]:
                        existing["start_time"] = start_time
                    if end_time > existing["end_time"]:
                        existing["end_time"] = end_time
                    # Обновляем перерывы если их нет
                    if not existing["break_start"] and break_start:
                        existing["break_start"] = break_start
                        existing["break_end"] = break_end
            except Exception as e:
                logger.debug(f"Ошибка парсинга даты {date_str} для мастера {staff_id}: {e}")
                continue
        
        result = list(schedule_by_day.values()) if schedule_by_day else []
        logger.debug(f"Сконвертировано {len(result)} дней расписания для мастера {staff_id}")
        return result
    
    async def _extract_schedule_from_available_slots(self, staff_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Извлекает расписание мастера на основе доступных слотов за 2 недели.
        Анализирует доступные даты и определяет рабочие часы.
        
        Args:
            staff_id: ID мастера в YClients
        
        Returns:
            Список расписаний по дням недели или None
        """
        from datetime import timedelta
        
        # Получаем доступные слоты на ближайшие 2 недели (для более точного расписания)
        today = date.today()
        week_end = today + timedelta(days=14)
        
        # Пробуем получить слоты для мастера
        try:
            url = f"{self.BASE_URL}/book_dates/{self.company_id}"
            params = {
                "staff_id": str(staff_id),
                "date_from": today.isoformat(),
                "date_to": week_end.isoformat(),
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    url,
                    headers=self._get_headers(),
                    params=params,
                )
                
                if response.status_code == 404:
                    # Мастер не найден или нет расписания
                    logger.debug(f"Мастер {staff_id} не найден или нет доступных слотов (404)")
                    return None
                
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"Ответ /book_dates для мастера {staff_id}: status=200, data keys: {list(data.keys())[:5] if isinstance(data, dict) else 'not dict'}")
                
                # Анализируем доступные слоты и определяем рабочее время
                if "data" in data:
                    dates_data = data["data"]
                    logger.info(f"Данные расписания для мастера {staff_id}: type={type(dates_data).__name__}, len={len(dates_data) if isinstance(dates_data, (dict, list)) else 'N/A'}")
                    
                    # Если ответ пустой, возвращаем None
                    if not dates_data or (isinstance(dates_data, dict) and len(dates_data) == 0):
                        logger.warning(f"Нет доступных слотов для мастера {staff_id} (пустой ответ)")
                        return None
                    
                    # Показываем первые несколько дат для диагностики
                    if isinstance(dates_data, dict):
                        sample_dates = list(dates_data.keys())[:3]
                        logger.info(f"Примеры дат для мастера {staff_id}: {sample_dates}")
                        if sample_dates:
                            first_date = sample_dates[0]
                            first_data = dates_data[first_date]
                            logger.info(f"Формат данных для {first_date}: type={type(first_data).__name__}, content preview: {str(first_data)[:200]}")
                    
                    schedule_by_day = {}  # {day_of_week: {start_times: [...], end_times: [...]}}
                    
                    if isinstance(dates_data, dict):
                        for date_str, slots_info in dates_data.items():
                            times = []
                            
                            # Обрабатываем разные форматы ответа
                            if isinstance(slots_info, dict):
                                # Может быть {"times": [...]} или прямо список времени
                                times = slots_info.get("times", [])
                                # Или может быть другой формат - проверяем все ключи
                                if not times and "times" not in slots_info:
                                    # Возможно, это вложенная структура
                                    for key, val in slots_info.items():
                                        if isinstance(val, list):
                                            times = val
                                            break
                            elif isinstance(slots_info, list):
                                # Может быть список строк времени или список объектов
                                for item in slots_info:
                                    if isinstance(item, str) and ":" in item:
                                        times.append(item)
                                    elif isinstance(item, dict):
                                        time_val = item.get("time") or item.get("start_time") or item.get("time_start")
                                        if time_val:
                                            times.append(time_val)
                            elif isinstance(slots_info, str) and ":" in slots_info:
                                # Единичное время
                                times = [slots_info]
                            
                            if not times:
                                logger.debug(f"Нет слотов для мастера {staff_id} на дату {date_str}")
                                continue
                            
                            logger.debug(f"Найдено {len(times)} слотов для мастера {staff_id} на {date_str}: {times[:3]}...")
                            
                            # Определяем день недели
                            try:
                                dt = datetime.strptime(date_str, "%Y-%m-%d").date()
                                day_of_week = dt.weekday()
                                
                                # Определяем рабочее время (первый и последний слот)
                                times_sorted = sorted([t for t in times if isinstance(t, str) and ":" in t])
                                if times_sorted:
                                    logger.debug(f"Обрабатываем слоты для мастера {staff_id}, день {day_of_week}, первый: {times_sorted[0]}, последний: {times_sorted[-1]}")
                                    start_time = times_sorted[0]
                                    last_slot = times_sorted[-1]
                                    
                                    # Парсим последний слот и добавляем примерную длительность услуги (60-90 минут)
                                    time_parts = last_slot.split(":")
                                    if len(time_parts) == 2:
                                        hour = int(time_parts[0])
                                        minute = int(time_parts[1])
                                        # Добавляем 90 минут к последнему слоту для определения конца рабочего дня
                                        end_dt = datetime.combine(date.today(), datetime.min.time().replace(hour=hour, minute=minute)) + timedelta(minutes=90)
                                        end_time = end_dt.strftime("%H:%M")
                                    else:
                                        end_time = last_slot
                                    
                                    # Группируем по дням недели (если несколько дней с одинаковым расписанием)
                                    if day_of_week not in schedule_by_day:
                                        schedule_by_day[day_of_week] = {
                                            "start_times": [],
                                            "end_times": [],
                                        }
                                    
                                    schedule_by_day[day_of_week]["start_times"].append(start_time)
                                    schedule_by_day[day_of_week]["end_times"].append(end_time)
                            except Exception as e:
                                logger.debug(f"Ошибка обработки даты {date_str} для мастера {staff_id}: {e}")
                                continue
                    
                    # Формируем итоговое расписание (берем самое раннее начало и самое позднее окончание для каждого дня)
                    result = []
                    for day_of_week, day_data in schedule_by_day.items():
                        if day_data["start_times"] and day_data["end_times"]:
                            # Берем самое раннее время начала и самое позднее время окончания
                            start_time = min(day_data["start_times"])
                            end_time = max(day_data["end_times"])
                            
                            result.append({
                                "day_of_week": day_of_week,
                                "start_time": start_time,
                                "end_time": end_time,
                                "break_start": None,
                                "break_end": None,
                            })
                    
                    if result:
                        logger.info(f"Извлечено расписание для мастера {staff_id}: {len(result)} дней")
                        return result
                    
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.debug(f"Мастер {staff_id} не найден или нет доступных слотов")
            else:
                logger.debug(f"HTTP ошибка при получении слотов для мастера {staff_id}: {e.response.status_code}")
            return None
        except Exception as e:
            logger.debug(f"Не удалось извлечь расписание из слотов для мастера {staff_id}: {e}")
        
        return None
    
    async def _extract_staff_from_available_slots(self) -> Dict[int, Dict[str, Any]]:
        """
        Извлекает мастеров с расписанием из доступных слотов через book_dates.
        Анализирует доступные слоты для разных услуг и извлекает информацию о мастерах.
        
        Returns:
            Словарь {staff_id: {staff_info, schedule: [...]}}
        """
        from datetime import timedelta
        
        result = {}
        
        try:
            # Получаем список услуг, чтобы попробовать разные комбинации
            services = await self.get_services()
            if not services:
                logger.warning("Нет услуг для анализа слотов")
                return {}
            
            # Пробуем получить слоты для первой услуги (или несколько услуг)
            test_service_ids = [s.get("id") for s in services[:5] if s.get("id")]  # Берем первые 5 услуг
            
            today = date.today()
            week_end = today + timedelta(days=14)  # Анализируем 2 недели
            
            staff_schedules = {}  # {staff_id: {day_of_week: {start, end, slots}}}
            
            for service_id in test_service_ids:
                try:
                    url = f"{self.BASE_URL}/book_dates/{self.company_id}"
                    params = {
                        "service_ids[]": str(service_id),
                        "date_from": today.isoformat(),
                        "date_to": week_end.isoformat(),
                    }
                    
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        response = await client.get(
                            url,
                            headers=self._get_headers(),
                            params=params,
                        )
                        response.raise_for_status()
                        data = response.json()
                        
                        # Обрабатываем ответ
                        if "data" in data:
                            dates_data = data["data"]
                            logger.debug(f"Получены данные для услуги {service_id}: {type(dates_data)}")
                            
                            # YClients может вернуть расписание по датам и мастерам
                            if isinstance(dates_data, dict):
                                # Формат может быть:
                                # 1. {"date": {"times": [...]}} - без мастера
                                # 2. {"date": {"staff_id": {"times": [...]}}} - с мастерами
                                # 3. {"date": [{"staff_id": ..., "times": [...]}]} - список мастеров
                                for date_str, date_info in dates_data.items():
                                    if not isinstance(date_info, dict):
                                        continue
                                    
                                    # Проверяем, есть ли информация о мастерах
                                    # Вариант 1: {"date": {"staff_id": {...}}}
                                    for key, value in date_info.items():
                                        try:
                                            # Проверяем, является ли ключ staff_id (число)
                                            if str(key).isdigit():
                                                staff_id = int(key)
                                                # Получаем слоты для этого мастера
                                                times = value.get("times", []) if isinstance(value, dict) else (value if isinstance(value, list) else [])
                                                
                                                if times and isinstance(times, list):
                                                    # Определяем день недели
                                                    try:
                                                        dt = datetime.strptime(date_str, "%Y-%m-%d").date()
                                                        day_of_week = dt.weekday()
                                                        
                                                        if staff_id not in staff_schedules:
                                                            staff_schedules[staff_id] = {}
                                                        
                                                        if day_of_week not in staff_schedules[staff_id]:
                                                            staff_schedules[staff_id][day_of_week] = {"times": []}
                                                        
                                                        staff_schedules[staff_id][day_of_week]["times"].extend(times)
                                                        logger.debug(f"Найден мастер {staff_id} на {date_str} с {len(times)} слотами")
                                                    except Exception as e:
                                                        logger.debug(f"Ошибка обработки даты {date_str}: {e}")
                                            # Вариант 2: прямо в date_info могут быть временные слоты без указания мастера
                                            elif key == "times" and isinstance(value, list):
                                                # Это слоты без указания мастера, пропускаем
                                                logger.debug(f"Найдены слоты без мастера на {date_str}")
                                                pass
                                        except (ValueError, TypeError) as e:
                                            logger.debug(f"Ошибка обработки ключа {key}: {e}")
                                            continue
                                    
                                    # Вариант 3: список мастеров в date_info
                                    if isinstance(date_info, list):
                                        for item in date_info:
                                            if isinstance(item, dict):
                                                item_staff_id = item.get("staff_id") or item.get("staff", {}).get("id") if isinstance(item.get("staff"), dict) else None
                                                if item_staff_id:
                                                    times = item.get("times", [])
                                                    if times:
                                                        try:
                                                            dt = datetime.strptime(date_str, "%Y-%m-%d").date()
                                                            day_of_week = dt.weekday()
                                                            
                                                            if item_staff_id not in staff_schedules:
                                                                staff_schedules[item_staff_id] = {}
                                                            
                                                            if day_of_week not in staff_schedules[item_staff_id]:
                                                                staff_schedules[item_staff_id][day_of_week] = {"times": []}
                                                            
                                                            staff_schedules[item_staff_id][day_of_week]["times"].extend(times)
                                                        except Exception as e:
                                                            logger.debug(f"Ошибка обработки мастера {item_staff_id} на {date_str}: {e}")
                            elif isinstance(dates_data, list):
                                # Формат: [{"date": "...", "staff_id": ..., "times": [...]}]
                                for item in dates_data:
                                    if isinstance(item, dict):
                                        date_str = item.get("date")
                                        item_staff_id = item.get("staff_id") or item.get("staff", {}).get("id") if isinstance(item.get("staff"), dict) else None
                                        times = item.get("times", [])
                                        
                                        if date_str and item_staff_id and times:
                                            try:
                                                dt = datetime.strptime(date_str, "%Y-%m-%d").date()
                                                day_of_week = dt.weekday()
                                                
                                                if item_staff_id not in staff_schedules:
                                                    staff_schedules[item_staff_id] = {}
                                                
                                                if day_of_week not in staff_schedules[item_staff_id]:
                                                    staff_schedules[item_staff_id][day_of_week] = {"times": []}
                                                
                                                staff_schedules[item_staff_id][day_of_week]["times"].extend(times)
                                            except Exception as e:
                                                logger.debug(f"Ошибка обработки записи: {e}")
                            
                            logger.info(f"Обработана услуга {service_id}, найдено {len(staff_schedules)} мастеров")
                except httpx.HTTPStatusError as e:
                    logger.debug(f"Не удалось получить слоты для услуги {service_id}: {e.response.status_code}")
                    continue
                except Exception as e:
                    logger.debug(f"Ошибка при запросе слотов для услуги {service_id}: {e}")
                    continue
            
            # Конвертируем найденные слоты в расписание
            for staff_id, schedule_by_day in staff_schedules.items():
                schedule_list = []
                
                for day_of_week, day_data in schedule_by_day.items():
                    times = day_data.get("times", [])
                    if not times:
                        continue
                    
                    # Определяем рабочее время (первый и последний слот)
                    times_sorted = sorted([t for t in times if isinstance(t, str) and ":" in t])
                    if times_sorted:
                        start_time = times_sorted[0]
                        # Берем последний слот и добавляем длительность (примерно 60 минут)
                        end_time = times_sorted[-1]
                        end_parts = end_time.split(":")
                        if len(end_parts) == 2:
                            hour = int(end_parts[0])
                            minute = int(end_parts[1])
                            # Добавляем час для определения конца рабочего дня
                            end_dt = datetime.combine(date.today(), datetime.min.time().replace(hour=hour, minute=minute)) + timedelta(hours=1)
                            end_time_formatted = end_dt.strftime("%H:%M")
                        else:
                            end_time_formatted = end_time
                        
                        schedule_list.append({
                            "day_of_week": day_of_week,
                            "start_time": start_time,
                            "end_time": end_time_formatted,
                            "break_start": None,
                            "break_end": None,
                        })
                
                if schedule_list:
                    result[staff_id] = {
                        "staff_info": {"id": staff_id},
                        "schedule": schedule_list,
                    }
        
        except Exception as e:
            logger.error(f"Ошибка при извлечении мастеров из слотов: {e}", exc_info=True)
        
        return result


# Глобальный экземпляр сервиса
yclients_service = YClientsService()


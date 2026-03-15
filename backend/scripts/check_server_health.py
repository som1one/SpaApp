#!/usr/bin/env python3
"""
Скрипт для проверки работоспособности сервера

Проверяет:
- Доступность сервера
- Подключение к базе данных
- Основные endpoints
- Конфигурацию

Использование:
    python scripts/check_server_health.py [--url http://localhost:8000]
"""

import sys
import argparse
import requests
from pathlib import Path
from typing import Dict, List, Tuple

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from app.core.config import settings
    from app.core.database import SessionLocal, engine
    from sqlalchemy import text
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь, что вы находитесь в папке backend и зависимости установлены")
    sys.exit(1)

# Цвета для вывода
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message: str):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def print_header(message: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{message}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")

def check_configuration() -> Tuple[bool, List[str]]:
    """Проверка конфигурации"""
    print_header("Проверка конфигурации")
    
    issues = []
    
    # Проверка SECRET_KEY
    if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 32:
        issues.append("SECRET_KEY не установлен или слишком короткий (минимум 32 символа)")
        print_error("SECRET_KEY не установлен или слишком короткий")
    else:
        print_success(f"SECRET_KEY установлен (длина: {len(settings.SECRET_KEY)})")
    
    # Проверка DATABASE_URL
    if not settings.DATABASE_URL:
        issues.append("DATABASE_URL не установлен")
        print_error("DATABASE_URL не установлен")
    else:
        # Скрываем пароль в выводе
        db_url_display = settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL
        print_success(f"DATABASE_URL установлен: ...@{db_url_display}")
    
    # Проверка окружения
    print_info(f"Окружение: {settings.ENVIRONMENT}")
    print_info(f"Debug режим: {settings.debug_mode}")
    
    # Проверка опциональных настроек
    if not settings.EMAIL_USER:
        print_warning("EMAIL_USER не установлен (email функциональность может не работать)")
    
    if not settings.GOOGLE_CLIENT_ID:
        print_warning("GOOGLE_CLIENT_ID не установлен (Google OAuth не будет работать)")
    
    if not settings.VK_APP_ID:
        print_warning("VK_APP_ID не установлен (VK OAuth не будет работать)")
    
    return len(issues) == 0, issues

def check_database() -> Tuple[bool, str]:
    """Проверка подключения к базе данных"""
    print_header("Проверка базы данных")
    
    try:
        # Пытаемся подключиться к БД
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print_success("Подключение к базе данных успешно")
        return True, ""
    except Exception as e:
        error_msg = f"Не удалось подключиться к базе данных: {str(e)}"
        print_error(error_msg)
        print_info("Убедитесь, что:")
        print_info("  1. PostgreSQL запущен")
        print_info("  2. DATABASE_URL правильный в .env файле")
        print_info("  3. База данных создана")
        return False, error_msg

def check_server_endpoints(base_url: str) -> Tuple[bool, List[str]]:
    """Проверка endpoints сервера"""
    print_header("Проверка endpoints сервера")
    
    issues = []
    endpoints = [
        ("/", "GET", "Проверка доступности"),
        ("/health", "GET", "Health check"),
        ("/docs", "GET", "Swagger документация"),
    ]
    
    for endpoint, method, description in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print_success(f"{method} {endpoint} - {description} (200 OK)")
            elif response.status_code == 404 and endpoint == "/docs":
                print_warning(f"{method} {endpoint} - {description} (404 - возможно, документация отключена)")
            else:
                issues.append(f"{endpoint} вернул статус {response.status_code}")
                print_error(f"{method} {endpoint} - {description} ({response.status_code})")
        except requests.exceptions.ConnectionError:
            issues.append(f"Не удалось подключиться к {base_url}")
            print_error(f"{method} {endpoint} - Сервер недоступен")
            return False, issues
        except requests.exceptions.Timeout:
            issues.append(f"Таймаут при подключении к {endpoint}")
            print_error(f"{method} {endpoint} - Таймаут")
        except Exception as e:
            issues.append(f"Ошибка при проверке {endpoint}: {str(e)}")
            print_error(f"{method} {endpoint} - Ошибка: {str(e)}")
    
    return len(issues) == 0, issues

def check_api_endpoints(base_url: str) -> Tuple[bool, List[str]]:
    """Проверка API endpoints"""
    print_header("Проверка API endpoints")
    
    issues = []
    api_base = f"{base_url}{settings.API_V1_PREFIX}"
    
    endpoints = [
        ("/auth/me", "GET", "Профиль пользователя (требует авторизации)"),
    ]
    
    for endpoint, method, description in endpoints:
        try:
            url = f"{api_base}{endpoint}"
            response = requests.get(url, timeout=5)
            
            # 401 - нормально для защищенных endpoints без токена
            if response.status_code in [200, 401, 403]:
                print_success(f"{method} {api_base}{endpoint} - {description} ({response.status_code})")
            else:
                issues.append(f"{endpoint} вернул неожиданный статус {response.status_code}")
                print_warning(f"{method} {api_base}{endpoint} - {description} ({response.status_code})")
        except Exception as e:
            issues.append(f"Ошибка при проверке {endpoint}: {str(e)}")
            print_error(f"{method} {api_base}{endpoint} - Ошибка: {str(e)}")
    
    return len(issues) == 0, issues

def main():
    parser = argparse.ArgumentParser(description="Проверка работоспособности сервера")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="URL сервера (по умолчанию: http://localhost:8000)"
    )
    args = parser.parse_args()
    
    base_url = args.url.rstrip('/')
    
    print_header("Проверка работоспособности сервера")
    print_info(f"Проверяю сервер: {base_url}")
    print_info(f"Рабочая директория: {project_root}\n")
    
    all_checks_passed = True
    all_issues = []
    
    # 1. Проверка конфигурации
    config_ok, config_issues = check_configuration()
    all_checks_passed = all_checks_passed and config_ok
    all_issues.extend(config_issues)
    
    # 2. Проверка базы данных
    db_ok, db_error = check_database()
    all_checks_passed = all_checks_passed and db_ok
    if db_error:
        all_issues.append(db_error)
    
    # 3. Проверка endpoints сервера
    endpoints_ok, endpoints_issues = check_server_endpoints(base_url)
    all_checks_passed = all_checks_passed and endpoints_ok
    all_issues.extend(endpoints_issues)
    
    # 4. Проверка API endpoints
    api_ok, api_issues = check_api_endpoints(base_url)
    # API endpoints могут требовать авторизации, поэтому не критично
    all_issues.extend(api_issues)
    
    # Итоговый результат
    print_header("Результаты проверки")
    
    if all_checks_passed and len(all_issues) == 0:
        print_success("Все проверки пройдены успешно! ✅")
        print_info("Сервер готов к работе")
        return 0
    else:
        if all_issues:
            print_error("Обнаружены проблемы:")
            for issue in all_issues:
                print(f"  • {issue}")
        
        print_warning("\nРекомендации:")
        print_info("1. Убедитесь, что сервер запущен: uvicorn app.main:app --reload")
        print_info("2. Проверьте .env файл в папке backend")
        print_info("3. Убедитесь, что PostgreSQL запущен: docker-compose up -d")
        print_info("4. Примените миграции: alembic upgrade head")
        
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
        sys.exit(1)
    except Exception as e:
        print_error(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


import asyncio
import os
import sys

import httpx

BASE_URL = "https://api.yclients.com/api/v1"

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from app.core.config import settings  # noqa: E402


def build_headers():
    missing = []
    if not settings.YCLIENTS_API_TOKEN:
        missing.append("YCLIENTS_API_TOKEN")
    if not settings.YCLIENTS_USER_TOKEN:
        missing.append("YCLIENTS_USER_TOKEN")
    if not settings.YCLIENTS_COMPANY_ID:
        missing.append("YCLIENTS_COMPANY_ID")

    if missing:
        raise RuntimeError(f"В .env не заполнены переменные: {', '.join(missing)}")

    return {
        "Content-Type": "application/json",
        "Accept": "application/vnd.api.v2+json",
        # Актуальный формат авторизации YClients:
        # Authorization: Bearer {partner_token}, User {user_token}
        "Authorization": f"Bearer {settings.YCLIENTS_API_TOKEN}, User {settings.YCLIENTS_USER_TOKEN}",
        # Дублируем для обратной совместимости.
        "User-Token": settings.YCLIENTS_USER_TOKEN,
    }


async def call(endpoint: str):
    url = f"{BASE_URL}{endpoint}"
    headers = build_headers()
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, headers=headers)
        print(f"[{endpoint}] status={response.status_code}")
        if response.status_code != 200:
            print(response.text[:500])
            response.raise_for_status()
        return response.json()


async def main():
    print("=" * 60)
    print("🔐 Тест авторизации YClients (env-based)")
    print("=" * 60)
    print(f"Компания: {settings.YCLIENTS_COMPANY_ID}")

    services = await call(f"/company/{settings.YCLIENTS_COMPANY_ID}/services")
    print(f"Услуг получено: {len(services.get('data', []))}")

    staff = await call(f"/company/{settings.YCLIENTS_COMPANY_ID}/staff")
    print(f"Сотрудников получено: {len(staff.get('data', []))}")

    print("\n✅ Авторизация успешно проверена")


if __name__ == "__main__":
    asyncio.run(main())

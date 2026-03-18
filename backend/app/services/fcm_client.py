import asyncio
import json
import logging
import os
from typing import Iterable, List, Mapping

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# FCM HTTP v1
FCM_V1_SCOPE = "https://www.googleapis.com/auth/firebase.messaging"


def _get_v1_access_token() -> str | None:
    """Получить OAuth2 access token для FCM v1 (синхронно, вызывать в executor)."""
    try:
        from google.oauth2 import service_account
    except ImportError:
        logger.warning("google-auth not installed; install with: pip install google-auth")
        return None

    project_id = (getattr(settings, "FCM_PROJECT_ID", None) or "").strip()
    if not project_id:
        return None

    credentials = None
    creds_path = (getattr(settings, "GOOGLE_APPLICATION_CREDENTIALS", None) or "").strip()
    creds_json = (getattr(settings, "FCM_CREDENTIALS_JSON", None) or "").strip()

    if creds_path and os.path.isfile(creds_path):
        try:
            credentials = service_account.Credentials.from_service_account_file(
                creds_path, scopes=[FCM_V1_SCOPE]
            )
        except Exception as e:
            logger.warning("Failed to load FCM credentials from file: %s", e)
    elif creds_json:
        try:
            info = json.loads(creds_json)
            credentials = service_account.Credentials.from_service_account_info(
                info, scopes=[FCM_V1_SCOPE]
            )
        except Exception as e:
            logger.warning("Failed to parse FCM_CREDENTIALS_JSON: %s", e)

    if not credentials:
        return None

    try:
        from google.auth.transport.requests import Request as AuthRequest
        credentials.refresh(AuthRequest())
    except Exception as e:
        logger.warning("Failed to refresh FCM v1 token: %s", e)
        return None

    return credentials.token


def _is_v1_configured() -> bool:
    """Проверка: настроен ли FCM v1 (project_id + credentials)."""
    project_id = (getattr(settings, "FCM_PROJECT_ID", None) or "").strip()
    if not project_id:
        return False
    creds_path = (getattr(settings, "GOOGLE_APPLICATION_CREDENTIALS", None) or "").strip()
    creds_json = (getattr(settings, "FCM_CREDENTIALS_JSON", None) or "").strip()
    return bool((creds_path and os.path.isfile(creds_path)) or creds_json)


def _is_legacy_configured() -> bool:
    """Проверка: задан ли Legacy Server Key."""
    key = (getattr(settings, "FCM_SERVER_KEY", None) or "").strip()
    return bool(key)


async def _send_v1(
    *,
    title: str,
    body: str,
    tokens: List[str],
    data: Mapping[str, str] | None,
) -> tuple[int, int]:
    """Отправка через FCM HTTP v1 API (один запрос на токен)."""
    project_id = (getattr(settings, "FCM_PROJECT_ID", None) or "").strip()
    if not project_id:
        raise RuntimeError("FCM is not configured (missing FCM_PROJECT_ID)")

    token = await asyncio.get_event_loop().run_in_executor(None, _get_v1_access_token)
    if not token:
        raise RuntimeError(
            "FCM v1: не удалось получить access token. "
            "Проверьте GOOGLE_APPLICATION_CREDENTIALS или FCM_CREDENTIALS_JSON (см. backend/ENV_SETUP.md)."
        )

    url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    data_clean = {k: str(v) for k, v in (data or {}).items()}

    success = 0
    failure = 0

    async with httpx.AsyncClient(timeout=15) as client:
        for fcm_token in tokens:
            body_msg = {
                "message": {
                    "token": fcm_token,
                    "notification": {"title": title, "body": body},
                    "data": data_clean,
                }
            }
            try:
                resp = await client.post(url, json=body_msg, headers=headers)
                if resp.status_code == 200:
                    success += 1
                else:
                    failure += 1
                    logger.warning(
                        "FCM v1 delivery failed",
                        extra={
                            "status_code": resp.status_code,
                            "response": resp.text[:300],
                        },
                    )
            except Exception as e:
                logger.exception("FCM v1 request failed for token", extra={"error": str(e)})
                failure += 1

    return success, failure


async def _send_legacy(
    *,
    title: str,
    body: str,
    tokens_list: List[str],
    data: Mapping[str, str] | None,
) -> tuple[int, int]:
    """Отправка через Legacy FCM API (batch)."""
    server_key = (getattr(settings, "FCM_SERVER_KEY", None) or "").strip()
    if not server_key:
        raise RuntimeError("FCM is not configured (missing FCM_SERVER_KEY)")

    success = 0
    failure = 0
    chunk_size = 1000
    headers = {
        "Authorization": f"key={server_key}",
        "Content-Type": "application/json",
    }
    api_url = getattr(settings, "FCM_API_URL", "https://fcm.googleapis.com/fcm/send")

    async with httpx.AsyncClient(timeout=10) as client:
        for i in range(0, len(tokens_list), chunk_size):
            chunk = tokens_list[i : i + chunk_size]
            payload = {
                "registration_ids": chunk,
                "notification": {"title": title, "body": body},
                "data": dict(data) if data else {},
            }
            try:
                resp = await client.post(api_url, json=payload, headers=headers)
                resp.raise_for_status()
                result = resp.json()
                results = result.get("results", [])
                if results:
                    for idx, item in enumerate(results):
                        if item.get("error"):
                            failure += 1
                            logger.warning(
                                "FCM legacy delivery failed",
                                extra={"token_index": idx, "error": item.get("error")},
                            )
                        else:
                            success += 1
                else:
                    success += int(result.get("success", 0))
                    failure += int(result.get("failure", 0))
            except httpx.HTTPStatusError as e:
                logger.error(
                    "FCM legacy HTTP error",
                    extra={
                        "status_code": e.response.status_code,
                        "response": (e.response.text or "")[:500],
                    },
                )
                failure += len(chunk)
            except Exception as e:
                logger.exception("FCM legacy request failed", extra={"error": str(e)})
                failure += len(chunk)

    return success, failure


class FcmClient:
    """Отправка push-уведомлений через FCM (v1 API или Legacy)."""

    @staticmethod
    async def send_to_tokens(
        *,
        title: str,
        body: str,
        tokens: Iterable[str],
        data: Mapping[str, str] | None = None,
    ) -> tuple[int, int]:
        """Отправка пушей на список токенов.

        Используется FCM HTTP v1 (если заданы FCM_PROJECT_ID и credentials),
        иначе Legacy API (если задан FCM_SERVER_KEY). Если ничего не настроено — RuntimeError.
        """
        tokens_list = [t for t in tokens if t]
        if not tokens_list:
            return 0, 0

        if _is_v1_configured():
            return await _send_v1(
                title=title, body=body, tokens=tokens_list, data=data
            )
        if _is_legacy_configured():
            return await _send_legacy(
                title=title, body=body, tokens_list=tokens_list, data=data
            )

        logger.error(
            "FCM not configured. Set FCM_PROJECT_ID + GOOGLE_APPLICATION_CREDENTIALS (or FCM_CREDENTIALS_JSON), "
            "or FCM_SERVER_KEY for Legacy. See backend/ENV_SETUP.md and spa/docs/FIREBASE_SETUP.md."
        )
        raise RuntimeError(
            "FCM is not configured. Add FCM v1 credentials or FCM_SERVER_KEY (see backend/ENV_SETUP.md)."
        )


def is_fcm_configured() -> bool:
    """Есть ли хотя бы одна рабочая конфигурация FCM (v1 или Legacy)."""
    return _is_v1_configured() or _is_legacy_configured()

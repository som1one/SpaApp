import logging
from typing import Iterable, List, Mapping

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class FcmClient:
    @staticmethod
    async def send_to_tokens(
        *,
        title: str,
        body: str,
        tokens: Iterable[str],
        data: Mapping[str, str] | None = None,
    ) -> tuple[int, int]:
        """Отправка пушей на список токенов (legacy HTTP API, batched)."""
        server_key = settings.FCM_SERVER_KEY
        if not server_key:
            logger.warning("FCM_SERVER_KEY not configured, skipping push")
            return 0, 0

        tokens_list: List[str] = [t for t in tokens if t]
        if not tokens_list:
            return 0, 0

        success = 0
        failure = 0

        # FCM позволяет до 1000 токенов за запрос
        chunk_size = 1000
        headers = {
            "Authorization": f"key={server_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=10) as client:
            for i in range(0, len(tokens_list), chunk_size):
                chunk = tokens_list[i : i + chunk_size]
                payload = {
                    "registration_ids": chunk,
                    "notification": {
                        "title": title,
                        "body": body,
                    },
                    "data": data or {},
                }
                try:
                    resp = await client.post(settings.FCM_API_URL, json=payload, headers=headers)
                    resp.raise_for_status()
                    result = resp.json()
                    
                    # Логируем полный ответ для отладки
                    logger.debug(
                        "FCM API response",
                        extra={
                            "response": result,
                            "chunk_size": len(chunk),
                        }
                    )
                    
                    # FCM legacy API возвращает успешные и неуспешные отправки
                    chunk_success = int(result.get("success", 0))
                    chunk_failure = int(result.get("failure", 0))
                    
                    # Проверяем результаты каждой отправки в массиве results
                    results = result.get("results", [])
                    actual_success = 0
                    actual_failure = 0
                    
                    if results:
                        for idx, item in enumerate(results):
                            if item.get("error"):
                                actual_failure += 1
                                error_code = item.get("error")
                                logger.warning(
                                    "FCM delivery failed for token",
                                    extra={
                                        "token_index": idx,
                                        "error": error_code,
                                        "chunk_size": len(chunk),
                                    }
                                )
                            else:
                                actual_success += 1
                                # Проверяем наличие message_id как подтверждение успеха
                                message_id = item.get("message_id")
                                if not message_id:
                                    logger.warning(
                                        "FCM response missing message_id",
                                        extra={
                                            "token_index": idx,
                                            "response_item": item,
                                        }
                                    )
                        
                        # Используем реальные результаты вместо агрегированных
                        success += actual_success
                        failure += actual_failure
                        
                        if actual_success != chunk_success or actual_failure != chunk_failure:
                            logger.warning(
                                "FCM result mismatch",
                                extra={
                                    "reported_success": chunk_success,
                                    "actual_success": actual_success,
                                    "reported_failure": chunk_failure,
                                    "actual_failure": actual_failure,
                                }
                            )
                    else:
                        # Если нет массива results, используем агрегированные значения
                        success += chunk_success
                        failure += chunk_failure
                        actual_success = chunk_success
                        actual_failure = chunk_failure
                        logger.warning(
                            "FCM response missing results array",
                            extra={
                                "chunk_size": len(chunk),
                                "response_keys": list(result.keys()) if isinstance(result, dict) else None,
                            }
                        )
                    
                    logger.info(
                        "FCM chunk processed",
                        extra={
                            "chunk_size": len(chunk),
                            "reported_success": chunk_success,
                            "reported_failure": chunk_failure,
                            "actual_success": actual_success,
                            "actual_failure": actual_failure,
                        }
                    )
                except httpx.HTTPStatusError as e:
                    logger.error(
                        "FCM HTTP error",
                        extra={
                            "status_code": e.response.status_code,
                            "response": e.response.text[:500] if e.response.text else None,
                            "chunk_size": len(chunk),
                        },
                        exc_info=True,
                    )
                    failure += len(chunk)
                except Exception as e:  # noqa: BLE001
                    logger.exception(
                        "FCM request failed",
                        extra={"chunk_size": len(chunk), "error": str(e)},
                    )
                    failure += len(chunk)

        logger.info("FCM send completed", extra={"success": success, "failure": failure})
        return success, failure



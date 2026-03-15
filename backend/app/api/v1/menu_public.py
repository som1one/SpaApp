from typing import List
import asyncio

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.service import MenuTreeItem
from app.services.menu_service import MenuService

router = APIRouter(prefix="/menu", tags=["Menu"])


@router.get("/tree", response_model=List[MenuTreeItem])
async def get_public_menu_tree(db: Session = Depends(get_db)):
    try:
        # Выполняем синхронный метод в отдельном потоке, чтобы не блокировать event loop
        # В публичном API показываем только активные услуги (include_inactive=False)
        loop = asyncio.get_event_loop()
        tree = await loop.run_in_executor(None, lambda: MenuService.get_menu_tree(db, include_inactive=False))
        return tree
    except Exception as e:
        # Логируем ошибку для отладки
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка при получении дерева меню: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не удалось загрузить меню: {str(e)}"
        )



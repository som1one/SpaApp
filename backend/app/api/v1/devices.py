import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.device_token import DeviceToken, DevicePlatform
from app.schemas.device import DeviceRegisterRequest, DeviceUnregisterRequest

router = APIRouter(prefix="/devices", tags=["Devices"])
logger = logging.getLogger(__name__)


@router.post("/register")
async def register_device(
    payload: DeviceRegisterRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    token = payload.token.strip()
    platform = payload.platform

    if platform not in (DevicePlatform.ANDROID, DevicePlatform.IOS):
        raise HTTPException(status_code=400, detail="Unknown platform")

    device = db.query(DeviceToken).filter(DeviceToken.token == token).first()
    if not device:
        device = DeviceToken(token=token, platform=platform)

    device.user_id = user.id
    device.platform = platform
    device.is_active = True

    db.add(device)
    db.commit()
    logger.info("Device registered", extra={"user_id": device.user_id, "platform": platform})
    return {"ok": True}


@router.post("/unregister")
async def unregister_device(
    payload: DeviceUnregisterRequest,
    db: Session = Depends(get_db),
):
    token = payload.token.strip()
    device = db.query(DeviceToken).filter(DeviceToken.token == token).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    device.is_active = False
    db.commit()
    logger.info("Device unregistered", extra={"token": token})
    return {"ok": True}



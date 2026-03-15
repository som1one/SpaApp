from pydantic import BaseModel, Field


class DeviceRegisterRequest(BaseModel):
    token: str = Field(..., min_length=10)
    platform: str = Field(..., pattern="^(android|ios)$")


class DeviceUnregisterRequest(BaseModel):
    token: str = Field(..., min_length=10)



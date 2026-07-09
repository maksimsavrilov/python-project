from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from common import DeviceSetupModel, DeviceSetupSchema, SwitchLogModel, SwitchStateSchema, UserModel, get_current_user, get_db_session

router = APIRouter(tags=["devices"])

@router.post("/api/device/toggle")
async def toggle_device(
    data: SwitchStateSchema,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    user_id = current_user.id
    db_status = 1 if data.status else 0

    query = text("INSERT INTO switch_logs (status, user_id) VALUES (:status, :user_id)")
    await db.execute(query, {"status": db_status, "user_id": user_id})

    return {
        "success": True,
        "message": f"User {current_user.username} (ID: {user_id}) toggled the light!",
    }


@router.post("/device/setup")
async def setup_device(
    device: DeviceSetupSchema,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    query = select(DeviceSetupModel).where(DeviceSetupModel.name == device.name)
    result = await db.execute(query)
    existing_device = result.scalar_one_or_none()

    if existing_device is None:
        new_device = DeviceSetupModel(name=device.name, brightness=device.brightness)
        db.add(new_device)
        return {
            "success": True,
            "message": f"User '{current_user.username}' added a new device '{device.name}'",
        }

    existing_device.brightness = device.brightness
    return {
        "success": True,
        "message": f"User '{current_user.username}' successfully configured '{device.name}'!",
    }


@router.get("/device/status/{device_id}", response_model=DeviceSetupSchema)
async def get_device_status(
    device_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    query = select(DeviceSetupModel).where(DeviceSetupModel.id == device_id)
    result = await db.execute(query)
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    return device


@router.get("/api/device/logs")
async def get_device_logs(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    query = select(SwitchLogModel)\
        .options(joinedload(SwitchLogModel.user))\
        .order_by(desc(SwitchLogModel.changed_at))\
        .limit(10)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    return [
        {
            "id": log.id,
            "status": log.status,
            "user_id": log.user_id,
            "username": log.user.username if log.user else "Unknown user",
            "changed_at": log.changed_at.isoformat()
        } 
        for log in logs
    ]

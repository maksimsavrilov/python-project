import datetime

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common import (
    ALGORITHM,
    SECRET_KEY,
    UserModel,
    UserSchema,
    get_db_session,
    get_password_hash,
    verify_password,
)

router = APIRouter(tags=["auth"])


@router.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserSchema,
    db: AsyncSession = Depends(get_db_session),
):
    query = select(UserModel).where(UserModel.username == user_data.username)
    result = await db.execute(query)
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже зарегистрирован",
        )

    hashed_pwd = get_password_hash(user_data.password)

    new_user = UserModel(
        username=user_data.username,
        password_hash=hashed_pwd,
        is_active=True,
    )
    print(f"Registering new user: {new_user.username}")

    db.add(new_user)

    return {
        "success": True,
        "message": f"Пользователь {new_user.username} успешно зарегистрирован",
    }


@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session),
):
    query = select(UserModel).where(UserModel.username == form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
    payload = {
        "sub": form_data.username,
        "exp": expire,
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

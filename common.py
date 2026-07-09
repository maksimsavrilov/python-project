import datetime
import os
import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


JWT_SECRET_KEY = str(os.getenv("JWT_SECRET_KEY"))
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://app_user:app_password@localhost:5432/smart_home",
)

engine = create_async_engine(DATABASE_URL, echo=True)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Base(DeclarativeBase):
    pass

class UserSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username for registration")
    password: str = Field(..., min_length=6, max_length=100, description="Plain password")

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    # (One-to-Many)
    logs: Mapped[list["SwitchLogModel"]] = relationship(back_populates="user")


class SwitchLogModel(Base):
    __tablename__ = "switch_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    status: Mapped[int] = mapped_column(nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    changed_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # one-to-one relationship with UserModel
    user: Mapped[UserModel | None] = relationship(back_populates="logs")

class DeviceSetupSchema(BaseModel):
    id: int
    name: str = Field(..., max_length=100)
    brightness: int = Field(50, ge=1, le=100)

class DeviceSetupModel(Base):
    __tablename__ = "devices"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column()
    brightness: Mapped[int] = mapped_column(
        CheckConstraint("brightness >= 1 AND brightness <= 100", name="chk_device_brightness"),
        nullable=False,
        server_default=text("50"),
    )


class SwitchStateSchema(BaseModel):
    status: bool


async def get_db_session():
    async with AsyncSession(engine) as session:
        async with session.begin():
            yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session),
):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = str(payload.get("sub"))
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен")
    except (jwt.PyJWTError, jwt.ExpiredSignatureError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ошибка авторизации или токен истек")

    query = select(UserModel).where(UserModel.username == username)
    result = await db.execute(query)
    user = result.scalars().first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден в базе данных")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Пользователь заблокирован")

    return user


def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

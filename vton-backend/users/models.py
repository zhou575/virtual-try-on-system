from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship
from app.config import BEIJING_TZ


# 用户账号模型
class UserAccount(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    nickname: Optional[str] = None
    email: str | None = Field(index=True, unique=True)
    phone: str | None = Field(index=True, unique=True)
    avatar: str | None = None
    password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone(BEIJING_TZ)))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone(BEIJING_TZ)))
    is_active: bool = True
    last_login_at: datetime | None = None


# 用户身体信息模型
class UserBody(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)  # 关联用户ID
    gender: str = Field()  # 性别：'男性' 或 '女性'
    age: int = Field()
    height: float = Field()  # 身高（厘米）
    weight: float = Field()  # 体重（千克）
    bust: float = Field()  # 胸围（厘米）
    waist: float = Field()  # 腰围（厘米）
    hip: float = Field()  # 臀围（厘米）
    arm_length: float = Field()  # 臂长（厘米）
    leg_length: float = Field()  # 腿长（厘米）
    shoe_size: float = Field()  # 鞋码
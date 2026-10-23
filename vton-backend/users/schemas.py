import re
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator
from app.config import PHONE_PATTERN, EMAIL_PATTERN


class GenderEnum(str, Enum):
    MALE = "男性"
    FEMALE = "女性"


# 用户注册请求模型
class UserCreate(BaseModel):
    account: str
    nickname: str | None = None
    password: str
    password_confirm: str
    code: str  # 验证码
    avatar: str | None = None

    @field_validator('password_confirm')
    @classmethod
    def passwords_match(cls, v, info):
        # 通过 info.data 访问其他字段的值, v就是被校验的password_confirm
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('两次输入的密码必须一致')
        return v

    @field_validator('account')
    @classmethod
    def validate_account(cls, v, info):
        if not re.match(PHONE_PATTERN, v) and not re.match(EMAIL_PATTERN, v):
            raise ValueError('账号必须是有效的手机号或邮箱')
        return v

# 用户登录请求模型
class UserLogin(BaseModel):
    account: str    # email or phone
    password: str


# 验证码请求模型
class VerificationCodeRequest(BaseModel):
    account: str    # email or phone

    @field_validator('account')
    @classmethod
    def validate_account(cls, v):
        if not re.match(PHONE_PATTERN, v) and not re.match(EMAIL_PATTERN, v):
            raise ValueError('账号必须是有效的手机号或邮箱')
        return v

# 验证码验证模型
class VerificationCodeVerify(BaseModel):
    account: str
    code: str

# 用户响应模型
class UserResponse(BaseModel):
    id: int
    username: str
    nickname: str | None
    email: str | None
    phone: str | None
    avatar: str | None
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# 用户身材信息模型
class UserBodyCreate(BaseModel):
    gender: GenderEnum
    age: int
    height: float
    weight: float
    bust: float
    waist: float
    hip: float
    arm_length: float
    leg_length: float
    shoe_size: float

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        if v not in ['男性', '女性']:
            raise ValueError('性别必须是 男性 或 女性')
        return v


# Token模型
class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


# Token数据模型
class TokenData(BaseModel):
    user_id: Optional[int] = None
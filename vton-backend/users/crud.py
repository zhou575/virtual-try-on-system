import random
import re
import string
from datetime import datetime, timezone, timedelta

from fastapi import Depends, status, HTTPException
from jose import jwt, JWTError
from sqlmodel import Session, select
from app import config
from app.database import get_db
from .models import UserAccount, UserBody
from .schemas import UserCreate, UserBodyCreate


def verify_password(plain_password, hashed_password):
    return config.pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return config.pwd_context.hash(password)


def generate_unique_username(account: str, db: Session) -> str:
    base_chars = ''.join(c.lower() for c in account if c.isalnum())
    if len(base_chars) < 4:
        base_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    base_username = base_chars[:4]
    while True:
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        username = f"{base_username}{random_suffix}"
        existing = db.exec(select(UserAccount).where(UserAccount.username == username)).first()
        if not existing:
            return username


def create_user(db: Session, user_create: UserCreate):
    # 验证账号类型并设置相应字段
    phone = email = None
    if re.match(config.PHONE_PATTERN, user_create.account):
        phone = user_create.account
    elif re.match(config.EMAIL_PATTERN, user_create.account):
        email = user_create.account
    # 构造用户账号数据
    user_data = user_create.model_dump(exclude_unset=True, exclude={"password_confirm", "code", "account"})
    user_data["phone"] = phone
    user_data["email"] = email
    # 生成Hash密码
    user_data["password"] = get_password_hash(user_create.password)
    # 根据用户账号信息生成username
    user_data["username"] = generate_unique_username(user_create.account, db)
    # 如果user_create没有提供avatar,则设置default_avatar为默认头像链接
    user_data["avatar"] = user_create.avatar or random.choice(config.DEFAULT_AVATARS)
    # 如果user_create没有提供nickname,则设置username为昵称
    user_data["nickname"] = user_create.nickname or user_data["username"]
    # 构造用户账号实例
    db_user = UserAccount(**user_data)
    # 写入到数据库
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# 根据不同账号类型获取用户
def get_user_by_account(db: Session, account: str):
    if re.match(config.PHONE_PATTERN, account):
        # 手机号查询
        return db.exec(select(UserAccount).where(UserAccount.phone == account)).first()
    elif re.match(config.EMAIL_PATTERN, account):
        # 邮箱查询
        return db.exec(select(UserAccount).where(UserAccount.email == account)).first()
    else:
        # 使用username查询
        return db.exec(select(UserAccount).where(UserAccount.username == account)).first()


# 创建访问令牌
def create_access_token(data: dict):
    # 令牌中的用户信息
    to_encode = data.copy()
    # 设置令牌过期时间
    expire = datetime.now(timezone.utc) + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # JWT 编码
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(config.oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # 从 jwt token 中获得 user_id
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # 根据user_id获得用户对象
    user = db.get(UserAccount, int(user_id))
    if user is None:
        raise credentials_exception
    return user


def update_user_avatar(db: Session, user: UserAccount, file_path: str):
    user.avatar = file_path
    user.updated_at = datetime.now(timezone(config.BEIJING_TZ))
    db.commit()
    db.refresh(user)


def get_or_create_user_body(db: Session, user_id: int, body_data: UserBodyCreate):
    # 检查是否存在现有记录
    existing_body = db.exec(select(UserBody).where(UserBody.user_id == user_id)).first()
    if existing_body:
        # 更新现有记录
        for key, value in body_data.model_dump().items():
            setattr(existing_body, key, value)
        db.commit()
        db.refresh(existing_body)
        return existing_body
    else:
        # 创建新记录
        new_body = UserBody(**body_data.model_dump(), user_id=user_id)
        db.add(new_body)
        db.commit()
        db.refresh(new_body)
        return new_body


def get_user_body_by_user_id(db: Session, user_id: int):
    return db.exec(select(UserBody).where(UserBody.user_id == user_id)).first()

import os
import re
import uuid
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request, Body
from sqlmodel import Session
from app.config import BEIJING_TZ, PHONE_PATTERN, EMAIL_PATTERN
from app.database import get_db

from . import schemas, crud
from .models import UserAccount, UserBody

router = APIRouter()

# 验证码存储（实际应用中应该使用Redis等持久化存储）
verification_codes: Dict[str, Dict[str, str]] = {}

def generate_verification_code():
    return ''.join(random.choices('0123456789', k=6))

# 发送验证码（模拟实现，实际应用中需要集成短信和邮件服务）
def send_verification_code(account: str, code: str):
    if re.match(PHONE_PATTERN, account):
        # 模拟发送短信
        print(f"向手机号 {account} 发送验证码: {code}")
        return {"message": "短信验证码发送成功"}
    elif re.match(EMAIL_PATTERN, account):
        # 模拟发送邮件
        print(f"向邮箱 {account} 发送验证码: {code}")
        return {"message": "邮箱验证码发送成功"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账号必须是有效的手机号或邮箱"
        )


# 发送验证码接口
@router.post("/send-verification-code")
def send_code(request: schemas.VerificationCodeRequest, db: Session = Depends(get_db)):
    # 检查账号是否已存在
    existing = crud.get_user_by_account(db, request.account)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="账号已存在",
                            headers={"WWW-Authenticate": "Bearer"})
    # 生成验证码
    code = generate_verification_code()
    # 存储验证码（实际应用中应该设置过期时间）
    verification_codes[request.account] = {
        "code": code,
        "created_at": datetime.now(timezone(BEIJING_TZ)).isoformat()
    }
    # 发送验证码
    send_verification_code(request.account, code)
    return {"message": "验证码发送成功"}

# 验证验证码接口
@router.post("/verify-code")
def verify_code(request: schemas.VerificationCodeVerify):
    # 检查验证码是否存在
    if request.account not in verification_codes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="验证码不存在或已过期",
                            headers={"WWW-Authenticate": "Bearer"})
    # 检查验证码是否正确
    if verification_codes[request.account]["code"] != request.code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="验证码错误",
                            headers={"WWW-Authenticate": "Bearer"})
    return {"message": "验证码验证成功"}

# --- 用户注册/登录 ---
# 用户注册接口
@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    # 验证验证码
    if user_create.account not in verification_codes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="验证码不存在或已过期",
                            headers={"WWW-Authenticate": "Bearer"})
    if verification_codes[user_create.account]["code"] != user_create.code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="验证码错误",
                            headers={"WWW-Authenticate": "Bearer"})
    # 检查账号是否已存在
    existing = crud.get_user_by_account(db, user_create.account)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="账号已存在",
                            headers={"WWW-Authenticate": "Bearer"})
    # 新增用户
    user = crud.create_user(db, user_create)
    # 删除验证码
    del verification_codes[user_create.account]
    return user


# 用户登录接口
@router.post("/login", response_model=schemas.Token)
def login(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    # 获取用户
    user = crud.get_user_by_account(db, user_login.account)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="找不到该账号对应的用户",
                            headers={"WWW-Authenticate": "Bearer"}
                            )
    # 验证密码
    if not crud.verify_password(user_login.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="该账号对应的密码输入错误",
            headers={"WWW-Authenticate": "Bearer"}
        )
    # 更新最后登录时间
    user.last_login_at = datetime.now(timezone(BEIJING_TZ))
    db.commit()
    # 创建访问令牌
    token = crud.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

# 基于表单的登录接口
@router.post("/login-by-form", response_model=dict)
def login_form(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """
    基于表单的登录接口，用于 Swagger UI 的 Authorize 功能
    """
    return login(schemas.UserLogin(account=username, password=password), db)

# 获取当前用户信息
@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(request: Request, current_user: UserAccount = Depends(crud.get_current_user)):
    # 如果avatar字段存在且不是默认头像，则拼接完整URL
    if current_user.avatar and not current_user.avatar.startswith("http"):
        current_user.avatar = str(request.url_for("media", path=current_user.avatar.replace("media/", "")))
    return current_user

# 退出登录接口
@router.post("/logout")
def logout():
    # 只要前端把访问令牌(access_token)删除，即可退出登录
    return {"message": "退出登录成功"}

# 用户上传头像接口
@router.post("/avatar", response_model=schemas.UserResponse)
def upload_avatar(
    request: Request,
    file: UploadFile = File(...),
    current_user: UserAccount = Depends(crud.get_current_user),
    db: Session = Depends(get_db)
):
    # 验证文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件必须是图片类型")
    # 生成唯一文件名
    ext = Path(file.filename).suffix
    filename = f"{uuid.uuid4()}{ext}"
    # 保存文件
    file_path = os.path.join("media/avatars", filename).replace("\\", "/")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    # 更新用户头像路径
    crud.update_user_avatar(db, current_user, file_path)
    # 返回前端的时候，拼接上HTTP协议和服务器的IP地址
    current_user.avatar = str(request.url_for("media", path=file_path.replace("media/", "")))
    return current_user

# 获取用户身材信息
@router.get("/body", response_model=UserBody)
def get_user_body(current_user: UserAccount = Depends(crud.get_current_user), db: Session = Depends(get_db)):
    body = crud.get_user_body_by_user_id(db, current_user.id)
    if not body:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到用户身材信息")
    return body

# 更新用户身材信息
@router.post("/body", response_model=UserBody)
def update_user_body(
    body_data: schemas.UserBodyCreate,
    current_user: UserAccount = Depends(crud.get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_or_create_user_body(db, current_user.id, body_data)

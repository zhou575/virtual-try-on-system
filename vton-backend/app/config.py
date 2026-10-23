import os
from datetime import timedelta

from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

# 加载 .env 文件
load_dotenv()

# 安全配置
SECRET_KEY = os.getenv("SECRET_KEY") or os.urandom(32).hex()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2密码承载令牌
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login-by-form")   # 用于SWagger UI的Authorization表单登录

# 数据库
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vton.db")

# 默认头像
DEFAULT_AVATARS = [
    "https://img.daren336.com/upload/ai666/20240802/1537/8d935f1c42ad4987cf28b73a20541759.webp",
    "https://c-ssl.dtstatic.com/uploads/blog/202403/13/xDS9Anpds2w2W4W.thumb.400_0.jpg",
    "https://img1.baidu.com/it/u=2423477223,422080146&fm=253&fmt=auto&app=138&f=JPEG?w=380&h=380",
    "https://gips3.baidu.com/it/u=3947786586,4229171972&fm=3074&app=3074&f=PNG?w=256&h=256",
    "https://gss0.baidu.com/9fo3dSag_xI4khGko9WTAnF6hhy/zhidao/wh%3D450%2C600/sign=f62eb83294dda144da5c64b68787fc94/7af40ad162d9f2d3add538ceaaec8a136227cccf.jpg"
]

# 正则
PHONE_PATTERN = r'^1[3-9]\d{9}$'
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# 时区
BEIJING_TZ = timedelta(hours=8)

# 火山引擎 API 配置
VOLC_AK = os.getenv("VOLC_ACCESSKEY")
VOLC_SK = os.getenv("VOLC_SECRETKEY")

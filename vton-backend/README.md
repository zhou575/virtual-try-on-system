# 虚拟试穿项目说明

## 项目介绍
虚拟试穿项目，
前端框架： Vue+ElementUI+Axios+Vite+TypeScript+Vuex+VueRouter+Pina
后端框架： FASTAI + SQLite + Redis

## 项目目录

```plaintext
vton_project/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 实例 & 路由挂载
│   ├── database.py             # 引擎、会话、表创建
│   ├── config.py               # 配置常量（SECRET_KEY 等）
│   └── core/
│       ├── __init__.py
│       └── security.py         # 密码哈希、JWT、验证逻辑
│
├── users/
│   ├── __init__.py
│   ├── models.py               # UserAccount, UserBody
│   ├── schemas.py              # Pydantic 模型（UserCreate, UserLogin, UserResponse 等）
│   ├── crud.py                 # 数据库操作（create_user, get_user_by_account 等）
│   └── api.py                  # 所有 /users 相关路由 + 验证码 + 登录
│
├── garments/
│   ├── __init__.py
│   ├── models.py               # GarmentType, Garment
│   ├── schemas.py              # GarmentCreate, GarmentUpdate 等
│   ├── crud.py                 # garment CRUD + init_garment_types
│   └── api.py                  # garment 路由（增删改查、初始化）
│
├── media/                      # （运行时自动创建）
├── vton.db                     # SQLite 数据库
└── requirements.txt            # 包含 fastapi, uvicorn, sqlalchemy, python-jose, passlib, python-multipart 等
```
## 项目运行

1. 创建并激活虚拟环境：
2. 运行uvicorn命令启动服务：
    
3. 访问浏览器：http://127.0.0.1:8000

如需启动时创建管理员账号，请在本地 `.env` 中设置 `PRESET_ADMIN_USERNAME`、
`PRESET_ADMIN_PASSWORD` 和 `PRESET_ADMIN_EMAIL`。这些值只用于本地开发，
不要把真实凭证提交到 Git。

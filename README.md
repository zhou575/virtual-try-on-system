# 灵动幻衣：虚拟试穿系统

一个基于 Vue 3 + TypeScript + FastAPI 的虚拟试穿系统，包含用户登录、服装管理、图片试穿和动作视频生成等功能。

## 项目结构

```text
vton-backend/   # FastAPI 后端
vton-frontend/  # Vue 3 前端
```

## 本地运行

### 后端

```bash
cd vton-backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

请在 `.env` 中填写 DashScope、阿里云 OSS 和其他云服务凭证。`.env` 不应提交到 Git。

### 前端

```bash
cd vton-frontend
npm install
npm run dev
```

## 说明

- 数据库、用户上传图片、运行日志和依赖目录属于本地运行数据，已通过 `.gitignore` 排除。
- 云服务密钥只从环境变量读取，不写入源码。


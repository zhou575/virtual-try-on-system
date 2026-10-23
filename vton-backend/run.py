# vton-backend/run.py
import uvicorn

if __name__ == "__main__":
    # 使用 uvicorn 启动应用
    # reload=True 支持热更新，适合开发环境
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
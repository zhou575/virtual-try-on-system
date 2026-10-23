import os
import httpx
import base64
import time
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select
from volcengine.visual.VisualService import VisualService

from app.database import create_db_and_tables, engine
from app import config
from users.api import router as users_router
from garments.api import router as garments_router
from users.models import UserAccount
from users.crud import get_password_hash

# ==========================================
# 🚨 请在这里填入你真实的阿里云 API KEY
# ==========================================
ALIYUN_API_KEY = os.getenv("DASHSCOPE_API_KEY")

def init_preset_users():
    """按本地环境变量可选地初始化管理员账号。"""
    username = os.getenv("PRESET_ADMIN_USERNAME")
    password = os.getenv("PRESET_ADMIN_PASSWORD")
    email = os.getenv("PRESET_ADMIN_EMAIL")
    if not all([username, password, email]):
        return
    with Session(engine) as db:
        admin = db.exec(select(UserAccount).where(UserAccount.username == username)).first()
        if not admin:
            user1 = UserAccount(
                id=1, username=username, nickname="admin", email=email,
                password=get_password_hash(password), avatar="", is_active=True
            )
            db.add(user1)
            db.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    os.makedirs("media/avatars", exist_ok=True)
    os.makedirs("media/garments", exist_ok=True)
    init_preset_users()
    yield

app = FastAPI(
    lifespan=lifespan, docs_url="/docs", openapi_url="/openapi.json",
    title="灵动幻衣虚拟试衣间 (整合版)", description="一个基于 FastAPI 的虚拟试衣间系统", version="1.0.0"
)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.mount("/media", StaticFiles(directory="media"), name="media")
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(garments_router, prefix="/garments", tags=["Garments"])

@app.get("/")
def root():
    return {"Hello": "欢迎来到灵动幻衣虚拟试衣间"}

# =========================================================================
# 终极整合流水线：火山引擎 (VTON) + 阿里云 DashScope (动作生成)
# =========================================================================
VIDEO_SYNTHESIS_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis"
TASK_STATUS_URL_TEMPLATE = "https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"

pipeline_router = APIRouter()

visual_service = VisualService()
if hasattr(config, 'VOLC_AK') and hasattr(config, 'VOLC_SK'):
    visual_service.set_ak(config.VOLC_AK)
    visual_service.set_sk(config.VOLC_SK)

@pipeline_router.post("/generate_magic_video")
async def generate_magic_video(
    avatar: UploadFile = File(..., description="上传用户原图"),
    garment: UploadFile = File(..., description="上传衣服平铺图"),
    video_url: str = Form(..., description="填入动作视频的公网URL(如OSS链接)")
):
    try:
        print("\n🚀 [Pipeline] 阶段 1：调用火山引擎生成静态试穿图...")
        model_b64 = base64.b64encode(await avatar.read()).decode("utf-8")
        garment_b64 = base64.b64encode(await garment.read()).decode("utf-8")

        submit_body = {
            "req_key": "dressing_diffusionV2",
            "req_image_store_type": 0,
            "binary_data_base64": [model_b64, garment_b64],
            "garment": {"data": [{"type": "upper"}]}
        }

        if not hasattr(visual_service, "cv_submit_task"):
            submit_res = visual_service.json_invoke("CVSubmitTask", {"Version": "2022-08-31"}, submit_body)
        else:
            submit_res = visual_service.cv_submit_task(submit_body)

        submit_dict = submit_res if isinstance(submit_res, dict) else json.loads(submit_res)
        if submit_dict.get("code") != 10000:
            raise Exception(f"换装任务失败: {submit_dict.get('message')}")

        vton_task_id = submit_dict["data"]["task_id"]
        
        result_image_url = None
        while True:
            time.sleep(3)
            query_body = {"req_key": "dressing_diffusionV2", "task_id": vton_task_id, "req_json": json.dumps({"return_url": True})}
            
            if not hasattr(visual_service, "cv_get_result"):
                query_res = visual_service.json_invoke("CVGetResult", {"Version": "2022-08-31"}, query_body)
            else:
                query_res = visual_service.cv_get_result(query_body)
                
            query_dict = query_res if isinstance(query_res, dict) else json.loads(query_res)
            task_status = query_dict["data"]["status"]
            
            if task_status == "done":
                result_image_url = query_dict["data"]["image_urls"][0]
                break
            elif task_status in ["not_found", "expired"]:
                raise Exception("火山引擎试穿任务失效")

        print(f"✅ [Pipeline] 阶段 1 成功！获得试穿公网 URL: {result_image_url}")
        print("🚀 [Pipeline] 阶段 2：正在将试穿图和视频提交给 阿里云 DashScope ...")

        headers = {
            "Authorization": f"Bearer {ALIYUN_API_KEY}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable"
        }
        
        payload = {
            "model": "wan2.2-animate-move",
            "input": {"image_url": result_image_url, "video_url": video_url, "watermark": False},
            "parameters": {"mode": "video"}
        }
        print("\n====== 准备发送给阿里云的真实 Payload ======")
        print(payload)
        print("==========================================\n")

        async with httpx.AsyncClient(timeout=30.0) as client:
            motion_resp = await client.post(VIDEO_SYNTHESIS_URL, headers=headers, json=payload)
            motion_resp.raise_for_status()
            motion_data = motion_resp.json()
            task_id = motion_data["output"]["task_id"]
            
        print(f"✅ [Pipeline] 阶段 2 成功！阿里云视频生成排队中，Task ID: {task_id}")
        return {"code": 200, "message": "流水线任务提交成功", "task_id": task_id}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"流水线崩溃: {str(e)}")

@pipeline_router.get("/status/{task_id}")
async def get_magic_video_status(task_id: str):
    try:
        url = TASK_STATUS_URL_TEMPLATE.format(task_id=task_id)
        headers = {"Authorization": f"Bearer {ALIYUN_API_KEY}"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=headers)
            return resp.json() 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

# 挂载流水线路由
app.include_router(pipeline_router, prefix="/api/pipeline", tags=["Pipeline (核心大串联接口)"])

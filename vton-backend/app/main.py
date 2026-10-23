import os
import httpx
import base64
import time
import json
import uuid
import oss2
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

from app.database import create_db_and_tables, engine
from users.api import router as users_router
from garments.api import router as garments_router
from garments.api import visual_service
from users.models import UserAccount
from users.crud import get_password_hash

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
                id=1,
                username=username,
                nickname="admin",
                email=email,
                password=get_password_hash(password),
                avatar="",
                is_active=True
            )
            db.add(user1)
            db.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. 创建数据库表
    create_db_and_tables()
    # 2. 确保媒体文件夹存在
    os.makedirs("media", exist_ok=True)
    os.makedirs("media/avatars", exist_ok=True)
    os.makedirs("media/garments", exist_ok=True)
    # 3. 初始化预设账号
    init_preset_users()
    yield

app = FastAPI(
    lifespan=lifespan,
    docs_url="/docs",
    openapi_url="/openapi.json",
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
    title="灵动幻衣虚拟试衣间",
    description="一个基于 FastAPI 的虚拟试衣间系统",
    version="0.1.0",
    debug=True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# 🚨 API KEY
ALIYUN_API_KEY = os.getenv("DASHSCOPE_API_KEY")

# 🚨🚨🚨 请在这里填入你真实的阿里云 OSS 凭证 🚨🚨🚨
OSS_ACCESS_KEY_ID = os.getenv("OSS_ACCESS_KEY_ID")
OSS_ACCESS_KEY_SECRET = os.getenv("OSS_ACCESS_KEY_SECRET")
OSS_ENDPOINT = os.getenv("OSS_ENDPOINT", "oss-cn-beijing.aliyuncs.com")
OSS_BUCKET_NAME = os.getenv("OSS_BUCKET_NAME")

# 🚨 终极修复：必须使用 image2video 这个端点！这是你最初 Demo 跑通的原版端点！
VIDEO_SYNTHESIS_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/video-synthesis"
pipeline_router = APIRouter()

def upload_bytes_to_oss(file_bytes: bytes, filename: str, content_type: str) -> dict:
    """内部工具函数：将字节流上传到 OSS，并返回内外网双链接"""
    if not all([OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET, OSS_BUCKET_NAME, ALIYUN_API_KEY]):
        raise HTTPException(status_code=500, detail="云服务配置缺失，请检查环境变量")
    auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
    bucket = oss2.Bucket(auth, f"https://{OSS_ENDPOINT}", OSS_BUCKET_NAME)
    
    ext = ".png" if "image" in content_type else ".mp4"
    unique_filename = f"pipeline_{uuid.uuid4().hex[:10]}{ext}"
    
    headers = {'Content-Type': content_type}
    bucket.put_object(unique_filename, file_bytes, headers=headers)
    
    # 🚨 核心改动：同时返回公网链接（供前端预览）和内网链接（供大模型读取）
    return {
        "http_url": f"https://{OSS_BUCKET_NAME}.{OSS_ENDPOINT}/{unique_filename}",
        "oss_url": f"oss://{OSS_BUCKET_NAME}/{unique_filename}"
    }

@pipeline_router.post("/generate_magic_video")
async def generate_magic_video(
    avatar: UploadFile = File(..., description="上传用户原图"),
    garment: UploadFile = File(..., description="上传衣服平铺图"),
    video: UploadFile = File(..., description="上传本地动作视频")
):
    try:
        # --- 阶段 1：【真实执行】调用火山引擎 (为了终端日志好看，体现真实的 AI 等待感) ---
        print("\n🚀 [Pipeline] 阶段 1：开始调用火山引擎处理用户真实图片...")
        model_b64 = base64.b64encode(await avatar.read()).decode("utf-8")
        garment_b64 = base64.b64encode(await garment.read()).decode("utf-8")

        submit_body = {
            "req_key": "dressing_diffusionV2",
            "req_image_store_type": 0,
            "binary_data_base64": [model_b64, garment_b64],
            "garment": {"data": [{"type": "upper"}]}
        }
        
        print("正在提交火山视觉任务...")
        submit_res = visual_service.cv_submit_task(submit_body)
        submit_dict = submit_res if isinstance(submit_res, dict) else json.loads(submit_res)
        if submit_dict.get("code") != 10000:
            raise Exception(f"火山引擎提交失败: {submit_dict.get('message')}")

        vton_task_id = submit_dict["data"]["task_id"]
        result_image_url = None
        print(f"任务提交成功，ID: {vton_task_id}，正在云端渲染衣服材质...")
        
        while True:
            time.sleep(3)
            query_body = {
                "req_key": "dressing_diffusionV2", 
                "task_id": vton_task_id, 
                "req_json": json.dumps({"return_url": True})
            }
            query_res = visual_service.cv_get_result(query_body)
            query_dict = query_res if isinstance(query_res, dict) else json.loads(query_res)
            
            status = query_dict["data"]["status"]
            if status == "done":
                result_image_url = query_dict["data"]["image_urls"][0]
                break
            elif status in ["failed", "expired"]:
                raise Exception(f"火山引擎任务失败，状态: {status}")
        
        print(f"✅ [Pipeline] 阶段 1 成功！已拿到基础合成结果。")

        # --- 阶段 1.5：【演示作弊启动】狸猫换太子 ---
# --- 阶段 1.5：【演示作弊启动】狸猫换太子 ---
# --- 阶段 1.5：【演示作弊启动】狸猫换太子 ---
        # --- 阶段 1.5：上传前端传来的真实动作视频到 OSS ---
        print("🚀 [Pipeline] 阶段 1.5：正在将动作视频上传至云端 OSS...")

        # 1. 读取前端上传的视频字节流
        video_bytes = await video.read()

        # 2. 调用你已经写好的上传函数，传到阿里云 OSS
        video_oss_info = upload_bytes_to_oss(
            file_bytes=video_bytes,
            filename=video.filename,
            content_type=video.content_type or "video/mp4"
        )

        # 3. 拿到真实的公网访问链接
        real_video_url = video_oss_info["http_url"]
        print(f"✅ 动作视频上传完成！云端链接为: {real_video_url}")

        # --- 阶段 2：【真实执行】提交任务至阿里云 DashScope ---
        print("🚀 [Pipeline] 阶段 2：正式唤醒阿里云万相动作生成大模型...")
        headers = {
            "Authorization": f"Bearer {ALIYUN_API_KEY}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable"
        }

        payload = {
            "model": "wan2.2-animate-move",
            "input": {
                "image_url": result_image_url,  # 火山引擎生成的换装后图片
                "video_url": real_video_url,  # 👈 换成刚刚上传的真实视频链接！
                "watermark": False
            },
            "parameters": {
                "mode": "wan-std"
            }
        }
        print("\n====== 准备发送给阿里云的真实 Payload ======")
        print(payload)
        print("==========================================\n")
        
        print(">>> 准备发给阿里云的图片链接是：", payload["input"]["image_url"])


        async with httpx.AsyncClient(timeout=60.0) as client:
            motion_resp = await client.post(VIDEO_SYNTHESIS_URL, headers=headers, json=payload)
            if motion_resp.status_code >= 400:
                print(f"❌ 阿里云报错: {motion_resp.text}")
                raise Exception(f"阿里云无法读取素材: {motion_resp.text}")
                
            motion_data = motion_resp.json()
            task_id = motion_data["output"]["task_id"]
            
        print(f"🎉 [Pipeline] 阶段 2 成功！动作合成任务 ID: {task_id}")
        return {"code": 200, "message": "提交成功", "task_id": task_id}
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ 发生崩溃: {str(e)}")
        raise HTTPException(status_code=500, detail=f"流水线崩溃: {str(e)}")

@pipeline_router.get("/status/{task_id}")
async def check_task_status(task_id: str):
    """前端轮询查询任务状态的接口"""
    url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
    headers = {"Authorization": f"Bearer {ALIYUN_API_KEY}"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, headers=headers)
            if response.status_code >= 400:
                return {"status": "FAILED", "error": f"请求阿里云失败: {response.text}"}
                
            data = response.json()
            status = data["output"]["task_status"]

            if status == "SUCCEEDED":
                video_url = data["output"]["results"]["video_url"]
                print(f"🎉 任务 {task_id} 彻底完成！视频出炉: {video_url}")
                return {"status": status, "video_url": video_url}
            elif status in ["FAILED", "CANCELED"]:
                error_msg = data['output'].get('message', '未知错误')
                print(f"❌ 任务 {task_id} 失败: {error_msg}")
                return {"status": status, "error": error_msg}
            else:
                # 状态为 PENDING 或 RUNNING
                print(f"⏳ 任务 {task_id} 正在云端疯狂渲染中... 当前进度: {status}")
                return {"status": status}
                
        except Exception as e:
            print(f"❌ 查询状态报错: {str(e)}")
            return {"status": "FAILED", "error": str(e)}
        
# 把这组接口挂载到真实的 app 上
app.include_router(pipeline_router, prefix="/api/pipeline", tags=["Pipeline (核心大串联接口)"])

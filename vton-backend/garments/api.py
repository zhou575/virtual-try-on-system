import base64
import json
import os
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import requests
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Request
from sqlmodel import Session, select
from volcengine.visual.VisualService import VisualService

from app.database import get_db
from app import config
from users.crud import get_current_user
from . import schemas, crud
# 注意：这里已经删除了原先的 .aliyun 导入
from .models import Garment, GarmentType, GarmentCategory

router = APIRouter()
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

# 初始化火山引擎视觉服务客户端
visual_service = VisualService()
if hasattr(config, 'VOLC_AK') and hasattr(config, 'VOLC_SK'):
    visual_service.set_ak(config.VOLC_AK)
    visual_service.set_sk(config.VOLC_SK)


def get_image_base64(image_path_or_url: str) -> str:
    """辅助函数：将本地图片或网络图片转换为 Base64 字符串"""
    try:
        if image_path_or_url.startswith("http"):
            response = requests.get(image_path_or_url)
            return base64.b64encode(response.content).decode("utf-8")
        else:
            with open(image_path_or_url, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片读取失败: {str(e)}")


@router.post("/init-garment-types")
def initialize_garment_types(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """ 初始化服装款式数据 """
    if not ADMIN_EMAIL or current_user.email != ADMIN_EMAIL:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问")
    crud.init_garment_types(db)
    return {"message": "服装款式数据初始化完成"}


@router.get("/garment-types")
def get_garment_types(category: GarmentCategory | None = Query(None), db: Session = Depends(get_db)):
    """ 查询服装款式数据 """
    query = select(GarmentType)
    if category:
        query = query.where(GarmentType.category == category)
    return db.exec(query).all()


@router.post("/garment-types")
def create_garment_type(garment_type: schemas.GarmentTypeCreate, current_user=Depends(get_current_user),
                        db: Session = Depends(get_db)):
    """ 新增服装款式数据 """
    if not ADMIN_EMAIL or current_user.email != ADMIN_EMAIL:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问")
    return crud.create_garment_type(db, garment_type)


@router.post("/", response_model=Garment)
def create_garment(
        garment_create: schemas.GarmentCreate,
        image: UploadFile = File(...),
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """ 新增服装数据，支持上传图片 """
    # 验证gtype是否存在
    gtype = db.exec(select(GarmentType).where(GarmentType.name == garment_create.gtype)).first()
    if not gtype:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="指定的款式不存在")
    # 验证文件类型
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件必须是图片类型")
    # 生成唯一文件名
    ext = Path(image.filename).suffix
    filename = f"{uuid.uuid4()}{ext}"
    # 保存文件
    file_path = os.path.join("media/garments", filename).replace("\\", "/")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(image.file.read())
    return crud.create_garment(db, garment_create, file_path)


@router.put("/{id}", response_model=Garment)
def update_garment(
        id: int,
        garment_update: schemas.GarmentUpdate,
        image: UploadFile | None = File(None),
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # 获取要更新的服装记录
    garment = db.get(Garment, id)
    if not garment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="服装数据不存在")
    # 验证gtype是否有效（如果提供了）
    if garment_update.gtype:
        gtype = db.exec(select(GarmentType).where(GarmentType.name == garment_update.gtype)).first()
        if not gtype:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="指定的款式不存在")
    # 转换为字典
    update_data = garment_update.model_dump(exclude_unset=True)
    # 处理图片上传
    if image:
        # 验证文件类型
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=status.HTTP_400_NOT_FOUND, detail="文件必须是图片类型")
        # 生成唯一文件名
        ext = Path(image.filename).suffix
        filename = f"{uuid.uuid4()}{ext}"
        # 保存文件
        file_path = os.path.join("media/garments", filename).replace("\\", "/")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(image.file.read())
        # 更新图片路径
        update_data["image"] = file_path
    return crud.update_garment(db, id, update_data)


@router.delete("/{id}")
def delete_garment(id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not crud.delete_garment(db, id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="服装数据不存在")
    return {"message": "删除成功"}


@router.get("/")
def get_garments(
        request: Request,
        category: GarmentCategory | None = Query(None),
        gtype: str | None = Query(None),
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
):
    # 获得服装列表
    items, total = crud.get_garments(db, category, gtype, page, limit)
    # 服装图像URL
    for item in items:
        if not item.image.startswith("http"):
            item.image = str(request.url_for("media", path=item.image.replace("media/", "")))

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }


@router.post("/try-on", response_model=schemas.TryOnResponse)
def try_on_garments(
        try_on_request: schemas.TryOnRequest,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """虚拟试穿接口 - 切换为火山引擎 V2 API"""

    # 1. 获取本地服装对象 (兼容前端可能只传了上装或下装的情况)
    top_garment = None
    bottom_garment = None

    if hasattr(try_on_request, 'top_garment_id') and try_on_request.top_garment_id:
        top_garment = db.get(Garment, try_on_request.top_garment_id)

    if hasattr(try_on_request, 'bottom_garment_id') and try_on_request.bottom_garment_id:
        bottom_garment = db.get(Garment, try_on_request.bottom_garment_id)

    if not top_garment and not bottom_garment:
        raise HTTPException(status_code=404, detail="未提供有效的服装数据")

    # 2. 将模特图和服装图转为 Base64 字符串
    model_b64 = get_image_base64(try_on_request.person_image_url)
    binary_data_base64 = [model_b64]
    garment_data = []

    # 按顺序添加服装图和类型，支持上衣(upper)、下衣(bottom)
    if top_garment:
        binary_data_base64.append(get_image_base64(top_garment.image))
        garment_data.append({"type": "upper"})

    if bottom_garment:
        binary_data_base64.append(get_image_base64(bottom_garment.image))
        garment_data.append({"type": "bottom"})

    # 3. 构造提交任务请求体
    submit_body = {
        "req_key": "dressing_diffusionV2",
        "req_image_store_type": 0,  # 0代表通过 base64 传入图片
        "binary_data_base64": binary_data_base64,
        "garment": {
            "data": garment_data
        }
    }

    try:
        # Step 1: 提交生成任务
        print("正在向火山引擎提交换装任务...")

        # 兼容处理1：有些版本的 SDK 可能没有 cv_submit_task 方法，我们使用底层通用方法
        if not hasattr(visual_service, "cv_submit_task"):
            print("当前 SDK 版本不支持快捷方法，使用通用 json_invoke...")
            submit_res = visual_service.json_invoke("CVSubmitTask", {"Version": "2022-08-31"}, submit_body)
        else:
            submit_res = visual_service.cv_submit_task(submit_body)

        # 兼容处理2：SDK 可能直接返回字典，也可能返回 JSON 字符串
        if isinstance(submit_res, dict):
            submit_dict = submit_res
        else:
            submit_dict = json.loads(submit_res)

        if submit_dict.get("code") != 10000:
            raise Exception(f"任务提交失败: {submit_dict.get('message')} (错误码:{submit_dict.get('code')})")

        task_id = submit_dict["data"]["task_id"]
        print(f"任务提交成功，Task ID: {task_id}")

        # 4. 构造查询任务请求体
        query_body = {
            "req_key": "dressing_diffusionV2",
            "task_id": task_id,
            "req_json": json.dumps({"return_url": True})  # 要求返回图片URL
        }

        # Step 2: 轮询查询结果
        task_status = "in_queue"
        while task_status in ["in_queue", "generating"]:
            time.sleep(3)  # 每3秒查询一次

            # 同样做查询方法的兼容处理
            if not hasattr(visual_service, "cv_get_result"):
                query_res = visual_service.json_invoke("CVGetResult", {"Version": "2022-08-31"}, query_body)
            else:
                query_res = visual_service.cv_get_result(query_body)

            # 同样做返回类型的兼容处理
            if isinstance(query_res, dict):
                query_dict = query_res
            else:
                query_dict = json.loads(query_res)

            if query_dict.get("code") != 10000:
                raise Exception(f"查询任务异常: {query_dict.get('message')}")

            task_status = query_dict["data"]["status"]
            print(f"当前任务状态: {task_status}")

            if task_status == "done":
                # 任务完成，提取结果
                image_urls = query_dict["data"].get("image_urls", [])
                if not image_urls:
                    raise Exception("任务显示完成，但未返回图片URL")

                result_image_url = image_urls[0]
                print(f"试穿成功！结果图片: {result_image_url}")

                return schemas.TryOnResponse(
                    task_id=task_id,
                    task_status=task_status,
                    submit_time="",
                    scheduled_time="",
                    end_time="",
                    image_url=result_image_url
                )
            elif task_status in ["not_found", "expired"]:
                raise Exception(f"任务已失效或未找到: {task_status}")

    except Exception as e:
        import traceback
        print("\n" + "=" * 40)
        print("🚨 试穿发生严重错误，详细堆栈如下：")
        traceback.print_exc()  # 这行代码会把真正的报错原因暴露在终端里！
        print("=" * 40 + "\n")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"试穿处理失败: {str(e)}")

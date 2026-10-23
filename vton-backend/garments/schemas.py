from pydantic import BaseModel
from .models import GarmentCategory

# 服装款式数据请求模型
class GarmentTypeCreate(BaseModel):
    category: GarmentCategory
    name: str                  # 款式名称

# 服装数据请求模型
class GarmentCreate(BaseModel):
    category: GarmentCategory
    gtype: str                  # 关联GarmentType的name列
    gender: str
    sizes: str | None = None    # JSON格式字符串，如 '{"S": "160-165", "M": "165-170"}'

class GarmentUpdate(BaseModel):
    category: GarmentCategory | None = None
    gtype: str | None = None    # 关联GarmentType的name列
    gender: str | None = None
    sizes: str | None = None

# 发起试穿的请求模型
class TryOnRequest(BaseModel):
    top_garment_id: int | None = None     # 允许为空
    bottom_garment_id: int | None = None  # 允许为空
    person_image_url: str
    # prompt: str  # 火山引擎不需要 prompt

# 试穿任务结果数据模型
class TryOnResponse(BaseModel):
    task_id: str            # 任务ID
    task_status: str        # 任务状态
    submit_time: str  | None = None      # 提交时间
    scheduled_time: str  | None = None   # 调度时间
    end_time: str  | None = None         # 结束时间
    image_url: str  | None = None        # 结果图片URL

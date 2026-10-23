from enum import Enum
from sqlmodel import SQLModel, Field

# 服装类别枚举类
class GarmentCategory(str, Enum):
    Top = "上装"
    Bottom = "下装"
    Whole = "全身装"


# 服装款式数据模型类
class GarmentType(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str                   # 款式名称
    category: GarmentCategory   # 服装类型，使用枚举值


# 服装数据模型类
class Garment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    category: GarmentCategory = Field()
    gtype: str = Field()
    gender: str = Field()
    image: str = Field()
    sizes: str | None = Field(default=None)  # 允许 sizes 存入 None
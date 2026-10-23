from sqlalchemy import func
from sqlmodel import Session, select
from .models import Garment, GarmentType, GarmentCategory
from .schemas import GarmentCreate, GarmentTypeCreate


# 初始化服装款式数据，将字典中的数据写入数据库表
def init_garment_types(db: Session, gtypes: dict=None):
    # 服装款式数据列表
    GarmentTypeList = {
        "上装": ["T恤", "衬衫", "POLO衫", "羽绒服", "棉服", "皮衣", "夹克", "卫衣", "毛呢大衣", "西服上衣", "风衣",
                 "针织衫", "马甲/背心/吊带", "羊毛衫", "羊绒衫", "毛衣", "皮草", "唐装", "中山装"],
        "下装": ["牛仔裤", "休闲裤", "西裤", "短裤", "卫裤/运动裤", "打底裤", "半身裙", "短裙", ],
        "全身装": ["西服套装", "旗袍", "汉服", "毛呢大衣", "礼服", "婚纱", "连衣裙"]
    }
    if not gtypes:
        gtypes = GarmentTypeList
    # 遍历每个分类下的款式
    for cat_name, names in gtypes.items():
        # 获取对应的枚举值
        cat_enum = GarmentCategory(cat_name)
        for name in names:
            # 检查是否已存在该款式
            exists = db.exec(select(GarmentType).where(GarmentType.name == name, GarmentType.category == cat_enum)).first()
            if not exists:
                # 创建新的服装款式记录
                new_garment = GarmentType(name=name, category=cat_enum)
                db.add(new_garment)
    # 全部遍历完毕，最后提交事务，保存到数据库
    db.commit()


def create_garment_type(db: Session, garment_type: GarmentTypeCreate):
    """创建服装款式"""
    # 判断是否已存在
    existing = db.exec(select(GarmentType).where(GarmentType.name == garment_type.name)).first()
    if existing:
        return None
    gtype = GarmentType(**garment_type.model_dump())
    db.add(gtype)
    db.commit()
    db.refresh(gtype)   # 获得新创建的款式的ID
    return gtype


def create_garment(db: Session, garment_in: GarmentCreate, file_path: str):
    """创建服装"""
    garment = Garment(
        category=garment_in.category,
        gtype=garment_in.gtype,
        gender=garment_in.gender,
        image=file_path,
        sizes=garment_in.sizes
    )
    db.add(garment)
    db.commit()
    db.refresh(garment)
    return garment


def update_garment(db: Session, garment_id: int, update_data: dict):
    """更新服装"""
    garment = db.get(Garment, garment_id)
    if not garment:
        return None
    for key, value in update_data.items():
        if value is not None:
            setattr(garment, key, value)
    db.commit()
    db.refresh(garment)
    return garment


def delete_garment(db: Session, garment_id: int):
    """删除服装"""
    garment = db.get(Garment, garment_id)
    if garment:
        db.delete(garment)
        db.commit()
        return True
    return False


def get_garments(db: Session, category=None, gtype=None, page=0, limit=100):
    """获得服装列表"""

    query = select(Garment)

    # 按category过滤
    if category:
        query = query.where(Garment.category == category)

    # 按gtype过滤
    if gtype:
        query = query.where(Garment.gtype == gtype)

    # 使用子查询计算总数
    count_query = select(func.count()).select_from(query.subquery())
    total_count = db.exec(count_query).first()

    # 分页处理
    offset = (page - 1) * limit
    paginated_query = query.offset(offset).limit(limit)

    garments = db.exec(paginated_query).all()

    return garments, total_count


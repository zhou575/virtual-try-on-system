/**
 * 服装类别枚举
 */
export enum GarmentCategory {
  Top = '上装',
  Bottom = '下装',
  Whole = '全身装',
}

/**
 * 服装款式数据模型
 */
export interface GarmentType {
  /**
   * 款式ID
   */
  id?: number

  /**
   * 款式名称
   */
  name: string

  /**
   * 服装类型
   */
  category: GarmentCategory
}

/**
 * 服装数据模型
 */
export interface Garment {
  /**
   * 服装ID
   */
  id?: number

  /**
   * 服装类型
   */
  category: GarmentCategory

  /**
   * 款式名称（关联GarmentType表的name列）
   */
  gtype: string

  /**
   * 性别：'男性' 或 '女性'
   */
  gender: '男性' | '女性'

  /**
   * 图像链接
   */
  image: string

  /**
   * 尺码信息，JSON格式字符串
   * 例如: '{"S": "160-165", "M": "165-170"}'
   */
  sizes: string
}

/**
 * 服装类型创建请求数据
 */
export interface GarmentTypeCreateRequest {
  name: string // 服装款式名称
  category: GarmentCategory // 服装类型
}

/**
 * 服装创建请求数据
 */
export interface GarmentCreateRequest {
  /**
   * 服装类型
   */
  category: GarmentCategory

  /**
   * 款式名称（关联GarmentType表的name列）
   */
  gtype: string

  /**
   * 性别：'男性' 或 '女性'
   */
  gender: string

  /**
   * 尺码信息，JSON格式字符串（可选）
   * 例如: '{"S": "160-165", "M": "165-170"}'
   */
  sizes?: string | null
}

/**
 * 服装更新请求数据
 */
export interface GarmentUpdateRequest {
  /**
   * 服装类型（可选）
   */
  category?: GarmentCategory

  /**
   * 款式名称（可选）
   */
  gtype?: string

  /**
   * 性别（可选）
   */
  gender?: string

  /**
   * 尺码信息，JSON格式字符串（可选）
   */
  sizes?: string
}

/**
 * 尺码信息接口
 * 用于解析sizes字段中的JSON数据
 */
export interface SizeInfo {
  [key: string]: string
  // 示例:
  // "S": "160-165"
  // "M": "165-170"
  // "L": "170-175"
}

// 试穿请求模型
export interface TryOnRequest {
  top_garment_id?: number | null
  bottom_garment_id?: number | null
  person_image_url: string
}

// 试穿任务结果数据模型
export interface TryOnResponse {
  task_id: string // 任务ID
  task_status: string // 任务状态
  submit_time: string // 提交时间
  scheduled_time: string // 调度时间
  end_time: string // 结束时间
  image_url: string // 结果图片URL
}

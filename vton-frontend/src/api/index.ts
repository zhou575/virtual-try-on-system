import request from './axios'
import type {
  UserAccount,
  UserBody,
  SendCodeRequest,
  VerifyCodeRequest,
  UserRegisterRequest,
  UserLoginRequest,
  LoginTokenResponse,
} from '@/types/user'
import type {
  Garment,
  GarmentCategory,
  GarmentType,
  GarmentTypeCreateRequest,
  GarmentCreateRequest,
  GarmentUpdateRequest,
  TryOnRequest,
  TryOnResponse,
} from '@/types/garment'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

/**
 * 发送验证码
 * @param data 包含账号信息的请求数据
 * @returns 响应消息
 */
export const sendVerificationCode = async (data: SendCodeRequest) => {
  const response = await request.post<{ message: string }>(
    `${API_BASE_URL}/users/send-verification-code`,
    data,
  )
  return response.data
}

/**
 * 验证验证码
 * @param data 包含账号和验证码的请求数据
 * @returns 响应消息
 */
export const verifyVerificationCode = async (data: VerifyCodeRequest) => {
  const response = await request.post<{ message: string }>(
    `${API_BASE_URL}/users/verify-code`,
    data,
  )
  return response.data
}

/**
 * 用户注册
 * @param data 包含账号、密码、确认密码和验证码的注册数据
 * @returns 注册成功的用户信息
 */
export const registerUser = async (data: UserRegisterRequest) => {
  const response = await request.post<UserAccount>(`${API_BASE_URL}/users/register`, data)
  return response.data
}

/**
 * 用户登录
 * @param data 包含账号和密码的登录数据
 * @returns 登录成功后的令牌信息
 */
export const loginUser = async (data: UserLoginRequest): Promise<LoginTokenResponse> => {
  const response = await request.post<LoginTokenResponse>(`${API_BASE_URL}/users/login`, data)
  return response.data
}

/**
 * 获取当前登录用户的账号信息
 * @returns 当前用户的账户信息
 */
export const getCurrentUserInfo = async (): Promise<UserAccount> => {
  const response = await request.get<UserAccount>(`${API_BASE_URL}/users/me`)
  return response.data
}

/**
 * 修改当前登录用户的头像
 * @param file 要上传的头像文件（File 对象）
 * @returns 更新后的用户信息
 */
export const updateAvatar = async (file: File): Promise<UserAccount> => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await request.post<UserAccount>(`${API_BASE_URL}/users/avatar`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

/**
 * 修改当前登录用户的身材信息
 * @param body 用户的身体信息数据
 * @returns 更新后的身体信息
 */
export const updateBodyInfo = async (body: UserBody): Promise<UserBody> => {
  const response = await request.post<UserBody>(`${API_BASE_URL}/users/body`, body)
  return response.data
}

/**
 * 获取当前登录用户的身材信息
 * @returns 用户的身体信息
 */
export const getCurrentBodyInfo = async (): Promise<UserBody> => {
  const response = await request.get<UserBody>(`${API_BASE_URL}/users/body`)
  return response.data
}

// 将所有用户相关的API函数组织到一个 usersAPI 对象中，
// 这样就可以通过 usersAPI.functionName() 的方式调用各个API函数
export const usersAPI = {
  sendVerificationCode,
  verifyVerificationCode,
  registerUser,
  loginUser,
  getCurrentUserInfo,
  updateAvatar,
  updateBodyInfo,
  getCurrentBodyInfo,
} as const

/**
 * 新增服装款式
 * @param data 服装款式创建请求数据
 * @returns 创建后的服装款式信息
 */
export const createGarmentType = async (data: GarmentTypeCreateRequest): Promise<GarmentType> => {
  const response = await request.post<GarmentType>(`${API_BASE_URL}/garments/garment-types`, data)
  return response.data
}

/**
 * 获取所有服装款式
 * @param category 可选的服装类别，用于筛选数据
 * @returns 服装款式列表
 */
export const getGarmentTypes = async (category?: GarmentCategory): Promise<GarmentType[]> => {
  const params = category ? { category } : {}

  const response = await request.get<GarmentType[]>(`${API_BASE_URL}/garments/garment-types`, {
    params,
  })
  return response.data
}

/**
 * 新增服装
 * @param data 服装创建请求数据
 * @param file 图片文件（File 对象）
 * @returns 创建后的服装信息
 */
export const createGarment = async (data: GarmentCreateRequest, file: File): Promise<Garment> => {
  const formData = new FormData()
  formData.append('garment_create', JSON.stringify(data))
  formData.append('image', file)

  const response = await request.post<Garment>(`${API_BASE_URL}/garments/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

/**
 * 更新服装
 * @param id 服装ID
 * @param data 服装更新请求数据
 * @param file 可选的图片文件（File 对象）
 * @returns 更新后的服装信息
 */
export const updateGarment = async (
  id: number,
  data: GarmentUpdateRequest,
  file?: File,
): Promise<Garment> => {
  const formData = new FormData()
  formData.append('garment_update', JSON.stringify(data))

  if (file) {
    formData.append('image', file)
  }

  const response = await request.put<Garment>(`${API_BASE_URL}/garments/${id}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

/**
 * 获取服装列表
 * @param category 可选的服装类别，用于筛选数据
 * @param gtype 可选的款式名称，用于筛选数据
 * @param page 当前页码，默认为 1
 * @param limit 每页数量，默认为 10
 * @returns 包含服装列表和分页信息的响应数据
 */
export const getGarments = async (
  category?: GarmentCategory,
  gtype?: string,
  page: number = 1,
  limit: number = 30,
): Promise<{
  items: Garment[]
  total: number
  page: number
  limit: number
  pages: number
}> => {
  // 构造查询参数
  const params = {
    category,
    gtype,
    page,
    limit,
  }
  // 发起请求
  const response = await request.get<{
    items: Garment[]
    total: number
    page: number
    limit: number
    pages: number
  }>(`${API_BASE_URL}/garments/`, { params })
  return response.data
}

/**
 * 提交试穿请求
 * @param data 包含上装ID、下装ID、模特图片URL和提示词的请求数据
 * @returns 试穿任务响应数据
 */
export const tryOnGarments = async (data: TryOnRequest): Promise<TryOnResponse> => {
  const response = await request.post<TryOnResponse>(`${API_BASE_URL}/garments/try-on`, data)
  return response.data
}

// 将所有服装相关的API函数组织到一个 garmentsAPI 对象中，
// 这样就可以通过 garmentsAPI.functionName() 的方式调用各个API函数
export const garmentsAPI = {
  createGarmentType,
  getGarmentTypes,
  createGarment,
  updateGarment,
  getGarments,
  tryOnGarments,
} as const

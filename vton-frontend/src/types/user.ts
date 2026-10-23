
/**
 * 用户账号数据模型
 */
export interface UserAccount {
  /**
   * 用户ID
   */
  id?: number;
  
  /**
   * 用户名
   */
  username?: string | null;
  
  /**
   * 昵称
   */
  nickname?: string | null;
  
  /**
   * 邮箱
   */
  email?: string | null;
  
  /**
   * 手机号
   */
  phone?: string | null;
  
  /**
   * 头像URL
   */
  avatar?: string | null;
  
  /**
   * 密码（加密后的）
   */
  password?: string | null;
  
  /**
   * 账号创建时间
   */
  created_at?: string | null; // ISO 8601 格式日期时间字符串
  
  /**
   * 最后更新时间
   */
  updated_at?: string | null; // ISO 8601 格式日期时间字符串
  
  /**
   * 账号是否激活
   */
  is_active?: boolean | null;
  
  /**
   * 最后登录时间
   */
  last_login_at?: string | null; // ISO 8601 格式日期时间字符串
}

/**
 * 用户身体信息模型
 */
export interface UserBody {
  /**
   * 身体信息记录ID
   */
  id?: number;
  
  /**
   * 关联的用户ID
   */
  user_id?: number;
  
  /**
   * 性别：'男性' 或 '女性'
   */
  gender: '男性' | '女性';
  
  /**
   * 年龄
   */
  age: number;
  
  /**
   * 身高（厘米）
   */
  height: number;
  
  /**
   * 体重（千克）
   */
  weight: number;
  
  /**
   * 胸围（厘米）
   */
  bust: number;
  
  /**
   * 腰围（厘米）
   */
  waist: number;
  
  /**
   * 臀围（厘米）
   */
  hip: number;
  
  /**
   * 臂长（厘米）
   */
  arm_length: number;
  
  /**
   * 腿长（厘米）
   */
  leg_length: number;
  
  /**
   * 鞋码
   */
  shoe_size: number;
}

// 发送验证码的请求体
export interface SendCodeRequest {
  account: string;
}

// 验证验证码的请求体
export interface VerifyCodeRequest {
  account: string;
  code: string;
}

/**
 * 用户注册的请求体
 */
export interface UserRegisterRequest {
  account: string;  // 账号(邮箱或手机号)
  code: string;     // 验证码
  password: string; // 密码
  password_confirm: string; // 确认密码
}

/**
 * 用户登录的请求体
 */
export interface UserLoginRequest {
  account: string;  // 账号(邮箱或手机号)
  password: string; // 密码
}

/**
 * 用户登录成功后返回的响应体
 */
export interface LoginTokenResponse {
  access_token: string;
  token_type: string;
}

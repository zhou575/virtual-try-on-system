// 服装类型
export interface Clothing {
  id: number
  name: string
  category: 'top' | 'bottom'
  type: string // 服装种类，如毛衣、外套等
  imageUrl: string
}

// 试穿结果类型
export interface TryOnResult {
  id: number
  mainImage: string
  thumbnails: string[]
}

// 用户信息类型
export interface User {
  id: number
  account: string
  email?: string
  phone?: string
  password: string
  nickname?: string
  avatar?: string
}

// 用户身材信息类型
export interface BodyInfo {
  id: number
  userId: number
  gender: 'male' | 'female'
  age: number
  height: number
  weight: number
  bust: number
  waist: number
  hip: number
  armLength: number
  legLength: number
  shoeSize: number
}

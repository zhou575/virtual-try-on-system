/**
 * 分页信息接口
 * 用于封装分页相关数据
 */
export interface PaginationInfo {
  total: number;    // 总数
  page: number;     // 当前页码
  limit: number;    // 每页数量
  pages: number;    // 总页数
}
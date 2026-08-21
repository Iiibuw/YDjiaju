/** 类型化 API 客户端（与后端 Pydantic schemas 1:1 对齐，通过 shared/ts-types 同步）。
 * 当后端未启动时，所有方法回退到 mock 数据（开发演示用，M2 接入自动生成的类型后去掉 mock）。
 */
import { http, unwrap, type ApiEnvelope } from './http'

// ===== 类型（与 schemas/product.py / schemas/case.py 对齐） =====

export interface ProductListItem {
  id: number
  product_code: string | null
  name: string
  subtitle: string | null
  cover_url: string | null
  min_price_cents: number | null
  max_price_cents: number | null
  price_yuan: string | null
  is_top: number
  status: 'draft' | 'on_sale' | 'off_sale'
  category_id: number | null
  series_id: number | null
  space_id: number | null
}

export interface ProductDetail extends ProductListItem {
  other_images: string[]
  description: string | null
  specs: Record<string, unknown> | null
  series: { id: number; name: string } | null
  space: { id: number; name: string } | null
  category: { id: number; name: string } | null
}

export interface PageData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ListParams {
  category_id?: number
  space_id?: number
  series_id?: number
  keyword?: string
  is_top?: number
  page?: number
  page_size?: number
}

// ===== Mock 数据（dev 演示） =====

const MOCK_DELAY = 200

const MOCK_PRODUCTS: ProductDetail[] = [
  {
    id: 1,
    product_code: 'YD-001-180',
    name: '胡桃禮·实木餐桌',
    subtitle: '现代简约 · 餐厅精选',
    cover_url: 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800',
    min_price_cents: 128000,
    max_price_cents: 168000,
    price_yuan: '¥1280.00 – ¥1680.00',
    is_top: 1,
    status: 'on_sale',
    category_id: 1,
    series_id: 1,
    space_id: 1,
    other_images: [
      'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=800',
      'https://images.unsplash.com/photo-1577140917170-285929fb55b5?w=800',
    ],
    description: '<p>选用北美黑胡桃木，纹理自然、质地坚硬。1800mm 长度适合 4-6 人家庭聚餐。</p>',
    specs: { 材质: '黑胡桃木', 颜色: '胡桃色', 尺寸: '1800×900×750mm', 可定制: '是' },
    series: { id: 1, name: '胡桃禮' },
    space: { id: 1, name: '餐厅' },
    category: { id: 1, name: '餐桌' },
  },
  {
    id: 2,
    product_code: 'YD-002-150',
    name: '胡桃禮·实木餐边柜',
    subtitle: '收纳美学 · 餐厅必备',
    cover_url: 'https://images.unsplash.com/photo-1567538096342-cd31b4c75e9b?w=800',
    min_price_cents: 98000,
    max_price_cents: 98000,
    price_yuan: '¥980.00',
    is_top: 1,
    status: 'on_sale',
    category_id: 2,
    series_id: 1,
    space_id: 1,
    other_images: [],
    description: '<p>三抽两门设计，实木导轨，抽拉顺滑。</p>',
    specs: { 材质: '黑胡桃木', 尺寸: '1500×450×850mm' },
    series: { id: 1, name: '胡桃禮' },
    space: { id: 1, name: '餐厅' },
    category: { id: 2, name: '餐边柜' },
  },
  {
    id: 3,
    product_code: 'YD-003-180',
    name: '北欧·白橡木床',
    subtitle: '自然原木 · 卧室首选',
    cover_url: 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=800',
    min_price_cents: 198000,
    max_price_cents: 198000,
    price_yuan: '¥1980.00',
    is_top: 0,
    status: 'on_sale',
    category_id: 3,
    series_id: 2,
    space_id: 2,
    other_images: [],
    description: '<p>FAS 级白橡木，纹理细腻，承重 500kg。</p>',
    specs: { 材质: '白橡木', 尺寸: '1800×2000mm' },
    series: { id: 2, name: '北欧系列' },
    space: { id: 2, name: '卧室' },
    category: { id: 3, name: '床' },
  },
  {
    id: 4,
    product_code: 'YD-004',
    name: '现代极简·真皮沙发',
    subtitle: '意式设计 · 客厅焦点',
    cover_url: 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800',
    min_price_cents: 588000,
    max_price_cents: 888000,
    price_yuan: '¥5880.00 – ¥8880.00',
    is_top: 1,
    status: 'on_sale',
    category_id: 4,
    series_id: null,
    space_id: 3,
    other_images: [],
    description: '<p>头层牛皮 + 高密度海绵，符合人体工学。</p>',
    specs: { 材质: '头层牛皮 + 实木框架', 可定制: '是' },
    series: null,
    space: { id: 3, name: '客厅' },
    category: { id: 4, name: '沙发' },
  },
  {
    id: 5,
    product_code: 'YD-005',
    name: '原木·茶几',
    subtitle: '极简设计 · 客厅搭配',
    cover_url: 'https://images.unsplash.com/photo-1532372320572-cda25653a26d?w=800',
    min_price_cents: 68000,
    max_price_cents: 68000,
    price_yuan: '¥680.00',
    is_top: 0,
    status: 'on_sale',
    category_id: 5,
    series_id: 1,
    space_id: 3,
    other_images: [],
    description: '<p>整板拼接，自然纹理，每件独一无二。</p>',
    specs: { 材质: '黑胡桃', 尺寸: '1200×600×400mm' },
    series: { id: 1, name: '胡桃禮' },
    space: { id: 3, name: '客厅' },
    category: { id: 5, name: '茶几' },
  },
  {
    id: 6,
    product_code: 'YD-006',
    name: '北欧·书桌椅套装',
    subtitle: '学习办公 · 极简之选',
    cover_url: 'https://images.unsplash.com/photo-1592078615290-033ee584e267?w=800',
    min_price_cents: 168000,
    max_price_cents: 198000,
    price_yuan: '¥1680.00 – ¥1980.00',
    is_top: 0,
    status: 'on_sale',
    category_id: 6,
    series_id: 2,
    space_id: 4,
    other_images: [],
    description: '<p>人体工学设计，5 档高度可调。</p>',
    specs: { 材质: '白橡木', 颜色: '原木色/胡桃色' },
    series: { id: 2, name: '北欧系列' },
    space: { id: 4, name: '书房' },
    category: { id: 6, name: '书桌椅' },
  },
]

function delay<T>(value: T, ms = MOCK_DELAY): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(value), ms))
}

// ===== 业务接口 =====

const USE_MOCK = false // ✅ 已切换真实 API(commit)

export async function listProducts(params: ListParams = {}): Promise<PageData<ProductListItem>> {
  if (USE_MOCK) {
    let items = MOCK_PRODUCTS.filter((p) => p.status === 'on_sale')
    if (params.category_id) items = items.filter((p) => p.category_id === params.category_id)
    if (params.space_id) items = items.filter((p) => p.space_id === params.space_id)
    if (params.series_id) items = items.filter((p) => p.series_id === params.series_id)
    if (params.keyword)
      items = items.filter((p) => p.name.toLowerCase().includes(params.keyword!.toLowerCase()))
    if (params.is_top !== undefined) items = items.filter((p) => p.is_top === params.is_top)
    const page = params.page ?? 1
    const page_size = params.page_size ?? 20
    const start = (page - 1) * page_size
    return delay({
      items: items.slice(start, start + page_size),
      total: items.length,
      page,
      page_size,
      total_pages: Math.ceil(items.length / page_size) || 0,
    })
  }
  const resp = await http.get<ApiEnvelope<PageData<ProductListItem>>>('/public/products', { params })
  return unwrap(resp)
}

export async function getProductDetail(id: number): Promise<ProductDetail> {
  if (USE_MOCK) {
    const p = MOCK_PRODUCTS.find((x) => x.id === id)
    if (!p) throw new Error('Product not found')
    return delay(p)
  }
  const resp = await http.get<ApiEnvelope<ProductDetail>>(`/public/products/${id}`)
  return unwrap(resp)
}

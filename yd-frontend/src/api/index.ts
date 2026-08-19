// ===== HTTP 底层 =====
export * from './http'

// ===== Auth 模块 =====
export * from './auth'

// ===== Product 模块（同时作为命名空间导出，供 `products.listProducts()` 使用） =====
export * from './products'
export * as products from './products'

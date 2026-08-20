/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** 后台管理系统地址（默认 http://localhost:5181） */
  readonly VITE_ADMIN_BASE_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
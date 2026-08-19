/**
 * Pydantic → TypeScript 自动生成的 API 类型
 * 由 `bash scripts/gen-types.sh` 生成，请勿手改
 *
 * 当前状态：M0 占位。M1 后端跑通后会被覆盖为真实类型。
 */
export interface HealthResponse {
  service: string
  version: string
  env: string
  db_ok: boolean
  db_error: string | null
  ts: string
}

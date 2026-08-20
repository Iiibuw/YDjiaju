/**
 * 轻量富文本编辑器（contenteditable + 工具栏，零依赖）。
 *
 * 支持:
 * - 加粗 / 斜体 / 下划线 / 删除线
 * - 文字颜色 / 高亮背景色
 * - 字号
 * - 左 / 居中 / 右 对齐
 * - 有序 / 无序列表
 * - 链接
 * - 图片上传（POST /upload/image，自动插入 <img> 到光标位置）
 * - 清除格式
 *
 * 输出 HTML（保留原有字段提交逻辑）。
 *
 * 用法：
 *   <Form.Item name="content" label="正文">
 *     <RichTextEditor placeholder="请输入正文..." minHeight={300} />
 *   </Form.Item>
 */
import { useEffect, useRef, useState } from 'react'
import { Button, ColorPicker, InputNumber, Popover, Space, Tooltip, Upload, message } from 'antd'
import {
  BoldOutlined,
  ItalicOutlined,
  UnderlineOutlined,
  StrikethroughOutlined,
  AlignLeftOutlined,
  AlignCenterOutlined,
  AlignRightOutlined,
  OrderedListOutlined,
  UnorderedListOutlined,
  LinkOutlined,
  PictureOutlined,
  ClearOutlined,
} from '@ant-design/icons'

import { uploadImage } from '../api/uploads'

interface Props {
  value?: string
  onChange?: (html: string) => void
  placeholder?: string
  minHeight?: number
}

const PRESET_COLORS = [
  '#000000', '#5B5B5B', '#1677ff', '#52c41a', '#fa8c16',
  '#f5222d', '#722ed1', '#13c2c2', '#eb2f96', '#ffffff',
]

export default function RichTextEditor({ value, onChange, placeholder = '请输入内容...', minHeight = 200 }: Props) {
  const editorRef = useRef<HTMLDivElement>(null)
  const isInternalChange = useRef(false)
  const [uploading, setUploading] = useState(false)
  const [textColor, setTextColor] = useState<string>('#000000')
  const [bgColor, setBgColor] = useState<string>('#ffffff')
  const [fontSize, setFontSize] = useState<number>(14)

  // ===== 受控同步：外部 value 变化时写入编辑器 =====
  useEffect(() => {
    if (!editorRef.current) return
    if (isInternalChange.current) {
      isInternalChange.current = false
      return
    }
    const incoming = value ?? ''
    if (editorRef.current.innerHTML !== incoming) {
      editorRef.current.innerHTML = incoming
    }
  }, [value])

  // ===== execCommand 包装 =====
  const exec = (cmd: string, val?: string) => {
    if (!editorRef.current) return
    editorRef.current.focus()
    // execCommand 已 deprecated，但现代浏览器仍支持
    document.execCommand(cmd, false, val)
    // 同步到 onChange
    triggerChange()
  }

  const triggerChange = () => {
    if (editorRef.current && onChange) {
      isInternalChange.current = true
      onChange(editorRef.current.innerHTML)
    }
  }

  // ===== 图片上传 =====
  const handleUpload = async (file: File) => {
    setUploading(true)
    try {
      const r = await uploadImage(file)
      // 在光标位置插入 <img>
      editorRef.current?.focus()
      const html = `<img src="${r.url}" alt="${r.filename}" style="max-width:100%;height:auto;display:block;margin:8px 0;border-radius:4px;" />`
      document.execCommand('insertHTML', false, html)
      triggerChange()
      message.success('图片已插入')
    } catch (e: any) {
      const msg = e?.response?.data?.message || '上传失败'
      message.error(msg)
    } finally {
      setUploading(false)
    }
    return false // 阻止 antd 默认上传
  }

  // ===== 插入超链接 =====
  const insertLink = () => {
    const url = window.prompt('请输入链接地址：', 'https://')
    if (!url) return
    exec('createLink', url)
  }

  // ===== 工具栏按钮 =====
  const tool = (cmd: string, val: string | undefined, icon: React.ReactNode, tip?: string) => (
    <Tooltip title={tip} key={cmd}>
      <Button
        type="text"
        size="small"
        icon={icon}
        onMouseDown={(e) => e.preventDefault() /* 防止工具栏抢焦点 */}
        onClick={() => exec(cmd, val)}
      />
    </Tooltip>
  )

  return (
    <div className="rounded-md border border-gray-300 bg-white">
      {/* ===== 工具栏 ===== */}
      <div className="flex flex-wrap items-center gap-0.5 border-b border-gray-200 bg-gray-50 px-2 py-1.5">
        {/* 文字样式 */}
        {tool('bold', undefined, <BoldOutlined />, '加粗 (Ctrl+B)')}
        {tool('italic', undefined, <ItalicOutlined />, '斜体 (Ctrl+I)')}
        {tool('underline', undefined, <UnderlineOutlined />, '下划线 (Ctrl+U)')}
        {tool('strikeThrough', undefined, <StrikethroughOutlined />, '删除线')}

        <span className="mx-1 h-4 w-px bg-gray-300" />

        {/* 文字颜色 */}
        <Popover
          trigger="click"
          content={
            <div>
              <ColorPicker
                value={textColor}
                onChange={(c) => setTextColor(c.toHexString())}
                presets={[{ label: '预设', colors: PRESET_COLORS }]}
              />
              <div className="mt-2 text-center">
                <Button
                  size="small"
                  type="primary"
                  onClick={() => exec('foreColor', textColor)}
                >
                  应用
                </Button>
              </div>
            </div>
          }
        >
          <Tooltip title="文字颜色">
            <Button type="text" size="small" onMouseDown={(e) => e.preventDefault()}>
              <span style={{ borderBottom: `2px solid ${textColor}`, paddingBottom: 1 }}>A</span>
            </Button>
          </Tooltip>
        </Popover>

        {/* 高亮颜色 */}
        <Popover
          trigger="click"
          content={
            <div>
              <ColorPicker
                value={bgColor}
                onChange={(c) => setBgColor(c.toHexString())}
                presets={[{ label: '预设', colors: PRESET_COLORS }]}
              />
              <div className="mt-2 text-center">
                <Button size="small" type="primary" onClick={() => exec('hiliteColor', bgColor)}>
                  应用
                </Button>
              </div>
            </div>
          }
        >
          <Tooltip title="背景高亮">
            <Button type="text" size="small" onMouseDown={(e) => e.preventDefault()}>
              <span style={{ backgroundColor: bgColor, padding: '0 4px' }}>A</span>
            </Button>
          </Tooltip>
        </Popover>

        {/* 字号 */}
        <Popover
          trigger="click"
          content={
            <Space direction="vertical">
              <InputNumber
                min={10}
                max={72}
                value={fontSize}
                onChange={(v) => v && setFontSize(v)}
              />
              <Button size="small" type="primary" onClick={() => exec('fontSize', String(Math.max(1, Math.min(7, Math.ceil(fontSize / 6)))))}>
                应用（实际 HTML 1-7）
              </Button>
            </Space>
          }
        >
          <Tooltip title="字号">
            <Button type="text" size="small" onMouseDown={(e) => e.preventDefault()}>
              {fontSize}px
            </Button>
          </Tooltip>
        </Popover>

        <span className="mx-1 h-4 w-px bg-gray-300" />

        {/* 对齐 */}
        {tool('justifyLeft', undefined, <AlignLeftOutlined />, '左对齐')}
        {tool('justifyCenter', undefined, <AlignCenterOutlined />, '居中')}
        {tool('justifyRight', undefined, <AlignRightOutlined />, '右对齐')}

        <span className="mx-1 h-4 w-px bg-gray-300" />

        {/* 列表 */}
        {tool('insertOrderedList', undefined, <OrderedListOutlined />, '有序列表')}
        {tool('insertUnorderedList', undefined, <UnorderedListOutlined />, '无序列表')}

        <span className="mx-1 h-4 w-px bg-gray-300" />

        {/* 链接 */}
        <Tooltip title="插入链接">
          <Button type="text" size="small" icon={<LinkOutlined />} onMouseDown={(e) => e.preventDefault()} onClick={insertLink} />
        </Tooltip>

        {/* 图片上传 */}
        <Upload
          accept="image/png,image/jpeg,image/jpg,image/webp,image/gif"
          showUploadList={false}
          beforeUpload={handleUpload}
          disabled={uploading}
        >
          <Tooltip title="插入图片">
            <Button type="text" size="small" icon={<PictureOutlined />} loading={uploading}>
              图片
            </Button>
          </Tooltip>
        </Upload>

        <span className="mx-1 h-4 w-px bg-gray-300" />

        {/* 清除格式 */}
        {tool('removeFormat', undefined, <ClearOutlined />, '清除格式')}
      </div>

      {/* ===== 编辑区 ===== */}
      <div
        ref={editorRef}
        contentEditable
        suppressContentEditableWarning
        onInput={triggerChange}
        onBlur={triggerChange}
        data-placeholder={placeholder}
        style={{
          minHeight,
          padding: '12px 16px',
          outline: 'none',
          fontSize: 14,
          lineHeight: 1.7,
          wordBreak: 'break-word',
        }}
        className="rte-content"
      />

      {/* ===== 空状态 placeholder（纯 CSS 实现） ===== */}
      <style>{`
        .rte-content:empty::before {
          content: attr(data-placeholder);
          color: rgba(0, 0, 0, 0.35);
          pointer-events: none;
        }
        .rte-content img {
          max-width: 100%;
          height: auto;
          border-radius: 4px;
          margin: 6px 0;
        }
        .rte-content p { margin: 0 0 8px; }
        .rte-content a { color: #1677ff; text-decoration: underline; }
        .rte-content ul, .rte-content ol { padding-left: 24px; margin: 4px 0; }
      `}</style>
    </div>
  )
}
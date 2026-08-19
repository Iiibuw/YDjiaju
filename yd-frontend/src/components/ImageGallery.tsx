import { useState } from 'react'

interface Props {
  images: string[]
  alt: string
}

/**
 * 产品图集（详情页）。主图 + 缩略图。
 * M1 简单版：上下布局，无 lightbox。
 */
export default function ImageGallery({ images, alt }: Props) {
  const [active, setActive] = useState(0)
  if (!images.length) {
    return (
      <div className="aspect-square bg-stone-100 grid place-items-center text-stone-400">暂无图片</div>
    )
  }
  return (
    <div className="space-y-3">
      <div className="aspect-square overflow-hidden bg-stone-100">
        <img
          key={active}
          src={images[active]}
          alt={alt}
          className="w-full h-full object-cover"
        />
      </div>
      {images.length > 1 && (
        <div className="grid grid-cols-5 gap-2">
          {images.map((url, i) => (
            <button
              key={i}
              onClick={() => setActive(i)}
              className={`aspect-square overflow-hidden border-2 transition-colors ${
                i === active ? 'border-ink' : 'border-transparent hover:border-ink/30'
              }`}
            >
              <img src={url} alt={`${alt}-${i}`} className="w-full h-full object-cover" />
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

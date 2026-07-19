import { useState, type ImgHTMLAttributes } from 'react'

const fallback = `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600"><defs><linearGradient id="g" x1="0" x2="1"><stop stop-color="#edf1e7"/><stop offset="1" stop-color="#f7ead8"/></linearGradient></defs><rect width="100%" height="100%" fill="url(#g)"/><circle cx="400" cy="260" r="90" fill="#fff" opacity=".7"/><text x="400" y="285" text-anchor="middle" font-size="72">🥣</text><text x="400" y="410" text-anchor="middle" font-family="sans-serif" font-size="28" fill="#657060">知味集 · 食品图片</text></svg>`)}`

export function SafeImage(props: ImgHTMLAttributes<HTMLImageElement>) {
  const [src, setSrc] = useState(String(props.src || fallback))
  return <img {...props} src={src} onError={() => setSrc(fallback)} />
}

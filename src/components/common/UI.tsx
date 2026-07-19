import { AlertCircle, CheckCircle2, HelpCircle, Info, LoaderCircle, ShieldAlert, X, type LucideIcon } from 'lucide-react'
import { useEffect, type ReactNode } from 'react'
import type { MatchStatus } from '../../types'

export const statusMeta: Record<MatchStatus, { icon: LucideIcon; cls: string; hint: string }> = {
  完全匹配: { icon: CheckCircle2, cls: 'success', hint: '满足当前硬约束' },
  存在风险: { icon: ShieldAlert, cls: 'warning', hint: '含可能接触或待确认风险' },
  不匹配: { icon: AlertCircle, cls: 'danger', hint: '明确命中排除条件' },
  信息不足: { icon: HelpCircle, cls: 'muted', hint: '数据不足，不能推断为安全' },
}

export function MatchBadge({ status, compact = false }: { status: MatchStatus; compact?: boolean }) {
  const meta = statusMeta[status]; const Icon = meta.icon
  return <span className={`status-badge ${meta.cls}`} title={meta.hint}><Icon size={14}/>{status}{!compact && <small>{meta.hint}</small>}</span>
}

export function SectionTitle({ eyebrow, title, desc, action }: { eyebrow?: string; title: string; desc?: string; action?: ReactNode }) {
  return <div className="section-title"><div>{eyebrow && <span className="eyebrow">{eyebrow}</span>}<h2>{title}</h2>{desc && <p>{desc}</p>}</div>{action}</div>
}

export function EmptyState({ title = '暂无数据', text = '当前条件下还没有内容', action }: { title?: string; text?: string; action?: ReactNode }) {
  return <div className="empty-state"><div className="empty-illustration">✦</div><h3>{title}</h3><p>{text}</p>{action}</div>
}

export function InlineNotice({ tone = 'info', title, children }: { tone?: 'info' | 'warning' | 'danger' | 'success'; title: string; children?: ReactNode }) {
  const Icon = tone === 'warning' || tone === 'danger' ? AlertCircle : tone === 'success' ? CheckCircle2 : Info
  return <div className={`notice ${tone}`}><Icon size={18}/><div><strong>{title}</strong>{children && <p>{children}</p>}</div></div>
}

export function LoadingBlock({ text = '正在加载数据…' }: { text?: string }) { return <div className="loading-block"><LoaderCircle className="spin"/><span>{text}</span></div> }

export function Modal({ open, title, children, onClose, footer }: { open: boolean; title: string; children: ReactNode; onClose: () => void; footer?: ReactNode }) {
  useEffect(() => { const fn = (e: KeyboardEvent) => e.key === 'Escape' && onClose(); if (open) document.addEventListener('keydown', fn); return () => document.removeEventListener('keydown', fn) }, [open, onClose])
  if (!open) return null
  return <div className="modal-backdrop" onMouseDown={(e) => e.target === e.currentTarget && onClose()}><div className="modal"><div className="modal-head"><h3>{title}</h3><button className="icon-btn" onClick={onClose} aria-label="关闭"><X/></button></div><div className="modal-body">{children}</div>{footer && <div className="modal-footer">{footer}</div>}</div></div>
}

export function ConfirmButton({ children, confirmText = '确定执行此操作？', onConfirm, className = 'btn danger' }: { children: ReactNode; confirmText?: string; onConfirm: () => void; className?: string }) {
  return <button className={className} onClick={() => window.confirm(confirmText) && onConfirm()}>{children}</button>
}

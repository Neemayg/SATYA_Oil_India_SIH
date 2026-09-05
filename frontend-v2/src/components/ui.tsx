import type { ReactNode } from 'react';
import { cn } from '../lib/utils';

export type Tone = 'ok' | 'warn' | 'bad' | 'brand' | 'muted';
const toneCls: Record<Tone, string> = {
  ok: 'border-ok text-ok', warn: 'border-amber text-amber', bad: 'border-bad text-bad',
  brand: 'border-brand text-brand', muted: 'border-line text-ink-2',
};
const toneFill: Record<Tone, string> = {
  ok: 'bg-ok-soft', warn: 'bg-warn-soft', bad: 'bg-bad-soft', brand: 'bg-brand-soft', muted: 'bg-surface-2',
};

export function Badge({ tone = 'muted', children, className, filled }: { tone?: Tone; children: ReactNode; className?: string; filled?: boolean }) {
  return <span className={cn('inline-flex items-center px-2 py-0.5 border rounded-sm text-[11px] font-semibold tracking-[0.12em] uppercase whitespace-nowrap', toneCls[tone], filled && toneFill[tone], className)}>{children}</span>;
}

export function Label({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn('text-[11px] tracking-[0.2em] uppercase text-ink-3 font-medium', className)}>{children}</div>;
}

export function Card({ children, className, title, action }: { children: ReactNode; className?: string; title?: string; action?: ReactNode }) {
  return (
    <section className={cn('bg-surface border border-line rounded-md', className)}>
      {(title || action) && (
        <header className="flex items-center justify-between px-5 py-3.5 border-b border-line">
          <Label className="text-ink">{title}</Label>
          {action}
        </header>
      )}
      {children}
    </section>
  );
}

export function Button({ children, onClick, variant = 'primary', disabled, className, type = 'button' }:
  { children: ReactNode; onClick?: () => void; variant?: 'primary' | 'secondary' | 'ghost' | 'danger'; disabled?: boolean; className?: string; type?: 'button' | 'submit' }) {
  const v = {
    primary: 'bg-amber text-black hover:opacity-90 font-semibold',
    secondary: 'bg-surface-2 border border-line text-ink hover:border-ink-3',
    ghost: 'text-ink-2 hover:text-ink hover:bg-surface-2',
    danger: 'bg-surface-2 border border-bad/60 text-bad hover:bg-bad-soft',
  }[variant];
  return (
    <button type={type} onClick={onClick} disabled={disabled}
      className={cn('inline-flex items-center gap-2 px-4 py-2 rounded-sm text-sm transition-colors disabled:opacity-40 disabled:cursor-not-allowed', v, className)}>
      {children}
    </button>
  );
}

export function Stat({ label, value, tone, hint }: { label: string; value: ReactNode; tone?: Tone; hint?: string }) {
  const color = tone === 'ok' ? 'text-ok' : tone === 'warn' ? 'text-amber' : tone === 'bad' ? 'text-bad' : tone === 'brand' ? 'text-brand' : 'text-ink';
  return (
    <div className="bg-surface border border-line rounded-md px-5 py-5">
      <Label>{label}</Label>
      <div className={cn('text-3xl font-semibold mt-2 tabular-nums', color)}>{value}</div>
      {hint && <div className={cn('text-xs mt-1', tone ? color : 'text-ink-3')}>{hint}</div>}
    </div>
  );
}

export function Row({ k, v, mono }: { k: string; v: ReactNode; mono?: boolean }) {
  return (
    <div className="flex justify-between gap-4 py-2.5 text-sm border-b border-line last:border-0">
      <span className="text-ink-3">{k}</span>
      <span className={cn('text-ink text-right', mono && 'font-mono text-xs')}>{v}</span>
    </div>
  );
}

export function Empty({ children }: { children: ReactNode }) {
  return <div className="p-10 text-center text-sm text-ink-3">{children}</div>;
}

export function Spinner() {
  return <div className="p-10 flex justify-center"><div className="w-5 h-5 border-2 border-line border-t-brand rounded-full animate-spin" /></div>;
}

export function PageHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: ReactNode }) {
  return (
    <div className="flex items-end justify-between px-8 py-5 border-b border-line bg-surface/40">
      <div>
        <h1 className="text-lg font-bold tracking-[0.2em] uppercase text-ink">{title}</h1>
        {subtitle && <p className="text-sm text-ink-3 mt-1">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

export const pct = (n?: number | null) => n == null ? '—' : `${Math.round(n * 100)}%`;
export const fmtDate = (s?: string | null) => s ? new Date(s).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' }).toUpperCase() : '—';
export const outcomeTone = (o?: string): Tone => o === 'MATCHED' ? 'ok' : o === 'AMBIGUOUS' || o === 'INSUFFICIENT_EVIDENCE' ? 'warn' : o === 'UNMATCHED' ? 'bad' : 'muted';
export const trustTone = (t?: string): Tone => t === 'TRUSTED' ? 'ok' : t === 'REVIEW_REQUIRED' ? 'warn' : t === 'UNTRUSTED' ? 'bad' : 'muted';
export const nice = (s?: string | null) => (s ?? '').replace(/_/g, ' ').toLowerCase().replace(/^\w/, c => c.toUpperCase());

// Chip — pill with optional check-icon for active, and palette variants
// Patterns: filter-chip (outline+fill when active), tag-chip (soft-tint), status-chip
const Chip = ({
  children,
  variant = 'filter',   // filter | tag | status
  color = 'teal',       // teal | pink | warm | muted | error
  active = false,
  onClick,
  icon,
  style = {},
}) => {
  const palettes = {
    teal:  { soft: 'rgba(118,221,230,0.30)', softFg: 'var(--teal-800)',
             fill: 'var(--steel-button)',    fillFg: '#fff',
             line: 'var(--border-strong)',   lineFg: 'var(--text-primary)' },
    pink:  { soft: 'var(--pink-100)',        softFg: 'var(--pink-700)',
             fill: 'var(--pink-primary)',    fillFg: '#fff',
             line: 'var(--border-strong)',   lineFg: 'var(--text-primary)' },
    warm:  { soft: 'rgba(251,192,136,0.45)', softFg: 'var(--warm-deep)',
             fill: 'var(--warm-primary)',    fillFg: 'var(--warm-deep)',
             line: 'var(--border-strong)',   lineFg: 'var(--text-primary)' },
    muted: { soft: 'var(--surface-muted)',   softFg: 'var(--text-primary)',
             fill: 'var(--steel-button)',    fillFg: '#fff',
             line: 'var(--border-strong)',   lineFg: 'var(--text-primary)' },
    error: { soft: 'var(--pink-50)',         softFg: 'var(--feedback-error)',
             fill: 'var(--feedback-error)',  fillFg: '#fff',
             line: 'var(--feedback-error)',  lineFg: 'var(--feedback-error)' },
  };
  const p = palettes[color] || palettes.teal;

  let look = {};
  if (variant === 'filter') {
    look = active
      ? { background: p.fill, color: p.fillFg, border: `1px solid ${p.fill}` }
      : { background: 'transparent', color: p.lineFg, border: `1px solid ${p.line}` };
  } else if (variant === 'tag') {
    look = { background: p.soft, color: p.softFg, border: 'none' };
  } else { // status
    look = { background: p.soft, color: p.softFg, border: 'none' };
  }

  const Tag = onClick ? 'button' : 'span';
  return (
    <Tag
      onClick={onClick}
      className={onClick ? 'velo-btn' : undefined}
      style={{
        display: 'inline-flex', alignItems: 'center', gap: 6,
        borderRadius: 200, padding: '6px 14px',
        fontFamily: 'var(--font-display)', fontSize: 13, lineHeight: 1.2,
        cursor: onClick ? 'pointer' : 'default',
        WebkitTapHighlightColor: 'transparent',
        ...look, ...style,
      }}
    >
      {active && variant === 'filter' && (
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
      )}
      {icon}
      {children}
    </Tag>
  );
};

// ChipRow — horizontal filter chip bar with "Все / X / Y ▼" dropdown caret at the end
const ChipRow = ({ items, active, onSelect, endCaret = false }) => (
  <div style={{
    display: 'flex', gap: 8, alignItems: 'center',
    overflowX: 'auto', padding: '2px 2px 6px', margin: '0 -2px',
  }}>
    {items.map(it => (
      <Chip key={it.id} color={it.color || 'teal'}
            active={it.id === active}
            onClick={() => onSelect && onSelect(it.id)}>
        {it.label}
      </Chip>
    ))}
    {endCaret && (
      <button className="velo-btn" style={{
        width: 32, height: 32, border: '1px solid var(--border-strong)',
        background: 'transparent', borderRadius: 200,
        display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
        color: 'var(--text-primary)', cursor: 'pointer', flex: '0 0 32px',
      }}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </button>
    )}
  </div>
);

window.Chip = Chip;
window.ChipRow = ChipRow;

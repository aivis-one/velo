// Chip — single pill (filter/status/tag)
const Chip = ({ children, active, onClick, color = 'default', icon, size = 'md', style = {} }) => {
  // color: default | teal | pink | warm | neutral
  const palettes = {
    default: {
      bg: 'var(--surface-elevated)', fg: 'var(--text-primary)',
      border: '1px solid var(--border-strong)',
      activeBg: 'var(--steel-button)', activeFg: '#fff', activeBorder: 'var(--steel-button)',
    },
    teal:    { bg: 'rgba(118,221,230,0.3)',  fg: 'var(--teal-800)',   border: 'none' },
    pink:    { bg: 'var(--pink-100)',        fg: 'var(--pink-700)',   border: 'none' },
    warm:    { bg: 'rgba(251,192,136,0.5)',  fg: 'var(--warm-deep)',  border: 'none' },
    neutral: { bg: 'var(--surface-subtle)',  fg: 'var(--text-secondary)', border: 'none' },
  };
  const p = palettes[color];
  const isFilter = color === 'default';
  const pad = size === 'sm' ? '4px 10px' : '8px 14px';
  const fs  = size === 'sm' ? 11 : 13;
  return (
    <button
      onClick={onClick}
      style={{
        display: 'inline-flex', alignItems: 'center', gap: 6,
        padding: pad,
        borderRadius: 200,
        fontFamily: 'var(--font-display)', fontSize: fs, lineHeight: 1,
        background: isFilter && active ? p.activeBg : p.bg,
        color:      isFilter && active ? p.activeFg : p.fg,
        border:     isFilter && active ? '1px solid ' + p.activeBorder : p.border,
        cursor: onClick ? 'pointer' : 'default',
        WebkitTapHighlightColor: 'transparent',
        whiteSpace: 'nowrap',
        transition: 'background 200ms, color 200ms',
        ...style,
      }}
    >
      {icon}
      {children}
    </button>
  );
};

// Tag cluster under master name: Медитация · Mindfulness · MBSR (mixed colors)
const TagCluster = ({ tags }) => (
  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
    {tags.map((t, i) => (
      <Chip key={i} color={t.color || 'teal'} size="sm">{t.label}</Chip>
    ))}
  </div>
);

window.Chip = Chip;
window.TagCluster = TagCluster;

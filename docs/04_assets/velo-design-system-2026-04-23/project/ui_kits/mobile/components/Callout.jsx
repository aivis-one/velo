// Callout — warning / info strip with icon, title, optional subtitle.
// Variants: warning (peach border), info (teal tint)
const Callout = ({ variant = 'warning', title, subtitle, icon }) => {
  const variants = {
    warning: {
      bg: 'rgba(251,192,136,0.4)',
      border: '2px solid var(--warm-primary)',
      fg: 'var(--warm-deep)',
    },
    info: {
      bg: 'rgba(118,221,230,0.25)',
      border: '1px solid var(--accent-teal)',
      fg: 'var(--teal-800)',
    },
  };
  const v = variants[variant];
  const DefaultIcon = variant === 'warning' ? (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor"
         strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10.3 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
      <line x1="12" y1="9" x2="12" y2="13"/>
      <line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>
  ) : null;

  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 12,
      padding: '12px 14px',
      background: v.bg, border: v.border, borderRadius: 15,
      color: v.fg,
    }}>
      <span style={{ flex: '0 0 auto' }}>{icon || DefaultIcon}</span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{
          fontFamily: 'var(--font-display)', fontSize: 14,
          textTransform: variant === 'warning' ? 'uppercase' : 'none',
          letterSpacing: variant === 'warning' ? '0.05em' : 0,
          lineHeight: 1.2,
        }}>{title}</div>
        {subtitle && (
          <div style={{ fontFamily: 'var(--font-display)', fontSize: 13,
                        opacity: 0.9, marginTop: 2, lineHeight: 1.3 }}>
            {subtitle}
          </div>
        )}
      </div>
    </div>
  );
};

// VideoTile — placeholder rectangle "video" + live dot badge
const VideoTile = ({ label = 'video', live = true }) => (
  <div style={{
    position: 'relative',
    aspectRatio: '16 / 10',
    background: 'var(--steel-button)',
    borderRadius: 15,
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    boxShadow: 'var(--shadow-md)',
    overflow: 'hidden',
  }}>
    <span style={{ color: 'rgba(255,255,255,0.7)',
                   fontFamily: 'var(--font-display)', fontSize: 28 }}>
      {label}
    </span>
    {live && (
      <div style={{
        position: 'absolute', top: 12, right: 12,
        display: 'inline-flex', alignItems: 'center', gap: 6,
        padding: '4px 10px', borderRadius: 200,
        background: 'rgba(255,255,255,0.9)',
        fontFamily: 'var(--font-display)', fontSize: 12,
        color: 'var(--teal-800)',
      }}>
        <span style={{ width: 8, height: 8, borderRadius: 999,
                       background: 'var(--feedback-error)',
                       animation: 'velo-pulse 1.4s ease-in-out infinite' }}/>
        В эфире
        <style>{`@keyframes velo-pulse {
          0%,100% { opacity: 1; }
          50%     { opacity: 0.35; }
        }`}</style>
      </div>
    )}
  </div>
);

window.Callout = Callout;
window.VideoTile = VideoTile;

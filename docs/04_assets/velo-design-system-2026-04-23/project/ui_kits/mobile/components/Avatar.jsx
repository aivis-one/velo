// Avatar — circular; accepts initials or image.
const Avatar = ({ size = 40, initials, color = 'muted', src, style = {} }) => {
  const palettes = {
    muted: { bg: 'var(--surface-muted)', fg: 'var(--text-primary)' },
    teal:  { bg: 'rgba(118,221,230,0.5)', fg: 'var(--teal-800)' },
    pink:  { bg: 'var(--pink-100)', fg: 'var(--pink-700)' },
    warm:  { bg: 'var(--warm-100)', fg: 'var(--warm-deep)' },
  };
  const p = palettes[color] || palettes.muted;
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: 999,
        background: src ? 'transparent' : p.bg,
        color: p.fg,
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: 'var(--font-display)',
        fontSize: Math.round(size * 0.36),
        flex: '0 0 auto',
        overflow: 'hidden',
        ...style,
      }}
    >
      {src ? (
        <img src={src} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
      ) : (
        initials
      )}
    </div>
  );
};

window.Avatar = Avatar;

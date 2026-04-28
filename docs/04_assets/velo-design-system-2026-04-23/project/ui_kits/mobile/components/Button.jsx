// Primitive: Button
// Follows VELO button spec — pill radius, 44+ touch, glow halo on primary.
// Variants: primary (filled steel + glow), secondary (muted blue), ghost (transparent teal).

const Button = ({ variant = 'primary', onClick, children, fullWidth, icon, style = {}, disabled }) => {
  const base = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    border: 0,
    borderRadius: 200,
    padding: '14px 28px',
    minHeight: 52,
    width: fullWidth ? '100%' : undefined,
    fontFamily: 'var(--font-display)',
    fontSize: 16,
    lineHeight: 1,
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.4 : 1,
    transition: 'filter 150ms ease, transform 80ms ease',
    WebkitTapHighlightColor: 'transparent',
  };
  const styles = {
    primary: {
      background: 'var(--steel-button)',
      color: 'var(--text-on-accent)',
      boxShadow: 'var(--shadow-glow-white)',
    },
    secondary: {
      background: 'var(--surface-muted)',
      color: 'var(--text-primary)',
    },
    ghost: {
      background: 'transparent',
      color: 'var(--text-accent)',
      padding: '10px 12px',
      minHeight: 44,
    },
    outline: {
      background: 'transparent',
      color: 'var(--text-primary)',
      boxShadow: 'inset 0 0 0 1.5px var(--border-strong)',
    },
  };
  return (
    <button
      className="velo-btn"
      style={{ ...base, ...styles[variant], ...style }}
      onClick={disabled ? undefined : onClick}
      disabled={disabled}
    >
      {icon}{children}
    </button>
  );
};

window.Button = Button;

// BackHeader — pill-shaped back button + optional title. Matches mockup top bar.
const BackHeader = ({ title, onBack, trailing }) => (
  <div style={{
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: '8px 16px 4px',
  }}>
    <button
      onClick={onBack}
      className="velo-btn"
      style={{
        display: 'inline-flex', alignItems: 'center', gap: 10,
        padding: '8px 18px 8px 14px',
        height: 44,
        border: 0,
        background: 'var(--surface-elevated)',
        boxShadow: 'var(--shadow-md)',
        borderRadius: 200,
        color: 'var(--text-primary)',
        fontFamily: 'var(--font-display)',
        fontSize: 15, cursor: 'pointer',
        WebkitTapHighlightColor: 'transparent',
      }}
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
           strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="19" y1="12" x2="5" y2="12"/>
        <polyline points="12 19 5 12 12 5"/>
      </svg>
      {title && <span>{title}</span>}
    </button>
    {trailing}
  </div>
);

// ArrowPillButton — small round pill with a forward arrow (used on master-card, calendar nav)
const ArrowPillButton = ({ direction = 'right', onClick, style = {} }) => (
  <button
    onClick={onClick}
    className="velo-btn"
    style={{
      width: 56, height: 40, border: 0,
      background: 'var(--surface-elevated)', boxShadow: 'var(--shadow-md)',
      borderRadius: 200, cursor: 'pointer',
      color: 'var(--text-primary)',
      display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
      WebkitTapHighlightColor: 'transparent',
      ...style,
    }}
  >
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
         strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
         style={{ transform: direction === 'left' ? 'rotate(180deg)' : 'none' }}>
      <line x1="5" y1="12" x2="19" y2="12"/>
      <polyline points="12 5 19 12 12 19"/>
    </svg>
  </button>
);

window.BackHeader = BackHeader;
window.ArrowPillButton = ArrowPillButton;

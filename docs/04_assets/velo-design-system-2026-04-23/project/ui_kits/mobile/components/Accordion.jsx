// Accordion — "О практике ↓" / "Что подготовить ↓" style collapsible row
const Accordion = ({ title, defaultOpen = false, children }) => {
  const [open, setOpen] = React.useState(defaultOpen);
  return (
    <div style={{
      background: 'var(--surface-elevated)',
      borderRadius: 15,
      boxShadow: 'var(--shadow-md)',
      overflow: 'hidden',
    }}>
      <button
        onClick={() => setOpen(!open)}
        className="velo-btn"
        style={{
          width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '16px 18px', border: 0, background: 'transparent',
          color: 'var(--text-primary)', fontFamily: 'var(--font-display)',
          fontSize: 16, cursor: 'pointer', textAlign: 'left',
          WebkitTapHighlightColor: 'transparent',
        }}
      >
        <span>{title}</span>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
             style={{ transform: open ? 'rotate(180deg)' : 'none', transition: 'transform 200ms' }}>
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </button>
      {open && (
        <div style={{
          padding: '0 18px 16px',
          fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.5,
        }}>
          {children}
        </div>
      )}
    </div>
  );
};

// Segmented — Неделя / Месяц toggle
const Segmented = ({ items, active, onChange }) => (
  <div style={{
    display: 'inline-flex', padding: 4,
    background: 'var(--surface-muted)', borderRadius: 200,
    gap: 4,
  }}>
    {items.map(it => {
      const isActive = it.id === active;
      return (
        <button
          key={it.id}
          onClick={() => onChange && onChange(it.id)}
          className="velo-btn"
          style={{
            border: 0, cursor: 'pointer', padding: '8px 18px',
            borderRadius: 200, fontFamily: 'var(--font-display)', fontSize: 14,
            background: isActive ? 'var(--steel-button)' : 'transparent',
            color: isActive ? 'var(--text-on-accent)' : 'var(--text-primary)',
            boxShadow: isActive ? 'var(--shadow-sm)' : 'none',
            transition: 'background 200ms, color 200ms',
            WebkitTapHighlightColor: 'transparent',
          }}
        >
          {it.label}
        </button>
      );
    })}
  </div>
);

// PageDots — onboarding pagination · · ·
const PageDots = ({ total, active }) => (
  <div style={{ display: 'inline-flex', gap: 8, alignItems: 'center' }}>
    {Array.from({ length: total }).map((_, i) => (
      <span key={i} style={{
        width: i === active ? 10 : 8,
        height: i === active ? 10 : 8,
        borderRadius: 999,
        background: i === active ? 'var(--steel-primary)' : 'var(--border-strong)',
        opacity: i === active ? 1 : 0.5,
        transition: 'all 200ms',
      }}/>
    ))}
  </div>
);

window.Accordion = Accordion;
window.Segmented = Segmented;
window.PageDots = PageDots;

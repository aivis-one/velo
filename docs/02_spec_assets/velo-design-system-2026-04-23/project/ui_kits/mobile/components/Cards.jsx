// Card — base VELO card. Radius 15, shadow-md in light, border in dark.
const Card = ({ children, variant = 'default', style = {}, onClick }) => {
  const variants = {
    default: {
      background: 'var(--surface-elevated)',
      boxShadow: 'var(--shadow-md)',
      border: 'none',
    },
    warm: {
      background: 'rgba(251,192,136,0.4)',
      border: '2px solid var(--warm-primary)',
      boxShadow: 'none',
    },
    flat: {
      background: 'var(--surface-subtle)',
      border: 'none',
      boxShadow: 'none',
    },
  };
  return (
    <div
      onClick={onClick}
      style={{
        borderRadius: 15,
        padding: 16,
        cursor: onClick ? 'pointer' : 'default',
        ...variants[variant],
        ...style,
      }}
    >
      {children}
    </div>
  );
};

// CheckInCard — the warm "Пора на check-in!" card
const CheckInCard = ({ title, subtitle, time, onClick }) => (
  <Card variant="warm" onClick={onClick}>
    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
      <div style={{
        width: 44, height: 44, borderRadius: 12,
        background: 'var(--warm-primary)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flex: '0 0 44px',
      }}>
        <img src="../../assets/brand-icons/spa.png"
             alt="" style={{ width: 26, height: 26, filter: 'brightness(0) saturate(100%) invert(27%) sepia(47%) saturate(1080%) hue-rotate(355deg) brightness(94%) contrast(91%)' }} />
      </div>
      <div style={{ flex: 1 }}>
        <div style={{
          fontSize: 16, color: 'var(--warm-deep)',
          marginBottom: 2,
        }}>{title}</div>
        <div style={{ fontSize: 13, color: 'var(--warm-deep)', opacity: 0.85 }}>
          {subtitle}
        </div>
      </div>
      {time && (
        <div style={{
          fontSize: 12, color: 'var(--warm-deep)',
          padding: '4px 10px', borderRadius: 200,
          background: 'rgba(255,255,255,0.5)',
          alignSelf: 'center', flex: '0 0 auto',
        }}>{time}</div>
      )}
    </div>
  </Card>
);

// BalanceCard — "Ближайшая практика" stats card with icon and meta
const BalanceCard = ({ title, subtitle, meta, iconSrc, cta, onClick }) => (
  <Card onClick={onClick}>
    <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
      <div style={{
        width: 56, height: 56, borderRadius: 14,
        background: 'var(--surface-muted)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flex: '0 0 56px',
      }}>
        {iconSrc && <img src={iconSrc} alt="" style={{ width: 34, height: 34 }} />}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 11, color: 'var(--text-muted)',
                      letterSpacing: '0.04em', textTransform: 'uppercase', marginBottom: 4 }}>
          {subtitle}
        </div>
        <div style={{ fontSize: 17, color: 'var(--text-primary)', marginBottom: 4 }}>
          {title}
        </div>
        <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
          {meta}
        </div>
      </div>
      {cta && (
        <div style={{
          width: 36, height: 36, borderRadius: 999,
          background: 'var(--accent-teal)', color: 'var(--text-on-accent)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          flex: '0 0 36px',
        }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
        </div>
      )}
    </div>
  </Card>
);

// PracticeItem — a single row in the list
const PracticeItem = ({ title, meta, iconSrc, tag, tagColor = 'teal' }) => {
  const tagPalette = {
    teal: { bg: 'rgba(118,221,230,0.3)', fg: 'var(--teal-800)' },
    warm: { bg: 'rgba(251,192,136,0.5)', fg: 'var(--warm-deep)' },
    pink: { bg: 'var(--pink-100)', fg: 'var(--pink-700)' },
  }[tagColor];
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 14,
      padding: '12px 14px',
      background: 'var(--surface-elevated)',
      borderRadius: 15,
      boxShadow: 'var(--shadow-sm)',
    }}>
      <div style={{
        width: 44, height: 44, borderRadius: 12,
        background: 'var(--surface-subtle)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flex: '0 0 44px',
      }}>
        {iconSrc && <img src={iconSrc} alt="" style={{ width: 28, height: 28 }} />}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 15, color: 'var(--text-primary)', marginBottom: 2 }}>{title}</div>
        <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{meta}</div>
      </div>
      {tag && (
        <div style={{
          fontSize: 11, padding: '4px 10px', borderRadius: 200,
          background: tagPalette.bg, color: tagPalette.fg,
          flex: '0 0 auto',
        }}>{tag}</div>
      )}
    </div>
  );
};

// Section header — "Ближайшая практика" + "Все →"
const SectionHeader = ({ title, action, onAction }) => (
  <div style={{
    display: 'flex', alignItems: 'baseline', justifyContent: 'space-between',
    padding: '0 4px',
  }}>
    <span style={{ fontSize: 18, color: 'var(--text-primary)' }}>{title}</span>
    {action && (
      <button
        onClick={onAction}
        style={{
          border: 0, background: 'transparent',
          color: 'var(--text-accent)', fontSize: 13,
          fontFamily: 'var(--font-display)', cursor: 'pointer',
        }}
      >{action}</button>
    )}
  </div>
);

window.Card = Card;
window.CheckInCard = CheckInCard;
window.BalanceCard = BalanceCard;
window.PracticeItem = PracticeItem;
window.SectionHeader = SectionHeader;

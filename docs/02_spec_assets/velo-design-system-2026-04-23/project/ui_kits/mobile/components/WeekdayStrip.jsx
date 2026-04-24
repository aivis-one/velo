// WeekdayStrip — 7 pill cells ПН..ВС + number + dot indicator. Active = steel-filled.
const WEEKDAY_LABELS = ['ПН','ВТ','СР','ЧТ','ПТ','СБ','ВС'];

const WeekdayStrip = ({ days, activeIndex, onSelect }) => (
  <div style={{
    display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 6,
  }}>
    {days.map((d, i) => {
      const isActive = i === activeIndex;
      return (
        <button
          key={i}
          onClick={() => onSelect && onSelect(i)}
          className="velo-btn"
          style={{
            border: 0, cursor: 'pointer',
            background: isActive ? 'var(--steel-button)' : 'var(--surface-elevated)',
            boxShadow: isActive ? 'var(--shadow-md)' : 'var(--shadow-sm)',
            borderRadius: 200, padding: '8px 2px 10px',
            color: isActive ? 'var(--text-on-accent)' : 'var(--text-primary)',
            display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2,
            fontFamily: 'var(--font-display)',
            position: 'relative',
            WebkitTapHighlightColor: 'transparent',
          }}
        >
          <span style={{ fontSize: 11, opacity: isActive ? 0.9 : 0.6 }}>
            {WEEKDAY_LABELS[i]}
          </span>
          <span style={{ fontSize: 17, lineHeight: 1 }}>{d.num}</span>
          {d.dot && (
            <span style={{
              width: 4, height: 4, borderRadius: 999,
              background: isActive ? '#fff' : 'var(--accent-teal)',
              marginTop: 2,
            }}/>
          )}
        </button>
      );
    })}
  </div>
);

window.WeekdayStrip = WeekdayStrip;

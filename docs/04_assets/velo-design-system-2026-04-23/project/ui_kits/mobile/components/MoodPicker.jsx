// MoodPicker — 3 face tiles + slider + central moodball. Matches Check-in screen.
// Labels are positioned BELOW the face tile; active tile is elevated + outlined.
const MoodPicker = ({ value = 1, onChange }) => {
  // value: 0 = bad, 1 = neutral, 2 = good
  const moods = [
    { id: 0, label: 'Не очень', src: '../../assets/mood/mood-sad.svg' },
    { id: 1, label: 'Нормально', src: '../../assets/mood/mood-neutral.svg' },
    { id: 2, label: 'Хорошо',   src: '../../assets/mood/mood-calm.svg' },
  ];
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Face tiles */}
      <div style={{ display: 'flex', gap: 12, alignItems: 'flex-end', justifyContent: 'center' }}>
        {moods.map(m => {
          const isActive = m.id === value;
          return (
            <button
              key={m.id}
              onClick={() => onChange && onChange(m.id)}
              className="velo-btn"
              style={{
                flex: 1, maxWidth: 110,
                border: 0, cursor: 'pointer',
                background: isActive ? 'var(--surface-elevated)' : 'var(--surface-subtle)',
                boxShadow: isActive ? 'var(--shadow-md)' : 'none',
                borderRadius: 15,
                padding: isActive ? '16px 8px' : '12px 8px',
                transform: isActive ? 'scale(1.1)' : 'scale(1)',
                transformOrigin: 'center bottom',
                transition: 'all 200ms',
                display: 'flex', flexDirection: 'column',
                alignItems: 'center', gap: 6,
                opacity: isActive ? 1 : 0.55,
                WebkitTapHighlightColor: 'transparent',
              }}
            >
              <img src={m.src} alt="" style={{
                width: isActive ? 64 : 44, height: isActive ? 64 : 44,
                transition: 'all 200ms',
              }}/>
              <span style={{
                fontFamily: 'var(--font-display)',
                fontSize: 13, color: 'var(--text-primary)',
              }}>
                {m.label}
              </span>
            </button>
          );
        })}
      </div>

      {/* Slider — visual representation of the value */}
      <div style={{ padding: '0 8px' }}>
        <div style={{
          position: 'relative',
          height: 28,
          display: 'flex', alignItems: 'center',
        }}>
          {/* Track */}
          <div style={{
            position: 'absolute', left: 0, right: 0, height: 2,
            background: 'var(--border-subtle)', borderRadius: 2,
          }}/>
          {/* Filled portion */}
          <div style={{
            position: 'absolute', left: 0, height: 2,
            width: `calc(${(value / 2) * 100}% )`,
            background: 'var(--accent-teal)', borderRadius: 2,
            transition: 'width 200ms',
          }}/>
          {/* Knob */}
          <div style={{
            position: 'absolute',
            left: `calc(${(value / 2) * 100}% - 10px)`,
            width: 20, height: 20, borderRadius: 999,
            background: 'var(--steel-button)',
            boxShadow: 'var(--shadow-md)',
            transition: 'left 200ms',
          }}/>
        </div>
      </div>
    </div>
  );
};

window.MoodPicker = MoodPicker;

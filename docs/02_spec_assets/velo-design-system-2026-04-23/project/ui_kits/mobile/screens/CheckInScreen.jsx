// CheckIn — mood picker + optional note + submit
const CheckInScreen = ({ onBack, onSubmit }) => {
  const [mood, setMood] = React.useState(1);
  const [note, setNote] = React.useState('');
  return (
    <div style={{
      position: 'absolute', inset: 0,
      background: 'var(--surface-default)',
      display: 'flex', flexDirection: 'column',
    }}>
      <div style={{
        flex: 1, overflowY: 'auto',
        padding: '48px 0 120px',
        display: 'flex', flexDirection: 'column', gap: 20,
      }}>
        <BackHeader title="Check-in" onBack={onBack} />

        {/* Heading */}
        <div style={{ padding: '0 20px', textAlign: 'center' }}>
          <h2 style={{ margin: 0, fontFamily: 'var(--font-display)', fontWeight: 400,
                       fontSize: 24, color: 'var(--text-primary)', lineHeight: 1.2 }}>
            Как вы себя чувствуете?
          </h2>
          <p style={{ margin: '6px 0 0', fontSize: 13, color: 'var(--text-secondary)' }}>
            Отметьте своё состояние перед практикой
          </p>
        </div>

        {/* Moodball visual */}
        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <div style={{
            width: 200, height: 200, borderRadius: 999,
            background: mood === 0
              ? 'radial-gradient(circle at 40% 40%, rgba(247,149,162,0.55), rgba(247,149,162,0.2))'
              : mood === 2
              ? 'radial-gradient(circle at 40% 40%, rgba(118,221,230,0.55), rgba(118,221,230,0.15))'
              : 'radial-gradient(circle at 40% 40%, rgba(251,192,136,0.6), rgba(251,192,136,0.15))',
            filter: 'blur(2px)',
            transition: 'background 300ms',
          }}/>
        </div>

        {/* Mood picker */}
        <div style={{ padding: '0 20px' }}>
          <MoodPicker value={mood} onChange={setMood} />
        </div>

        {/* Note */}
        <div style={{ padding: '0 20px', display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Коротко о состоянии</div>
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Что сейчас в фокусе, что хочется отпустить..."
            style={{
              width: '100%', minHeight: 84, resize: 'none',
              border: '1px solid var(--border-strong)', borderRadius: 12,
              background: 'var(--surface-default)', color: 'var(--text-primary)',
              padding: 12, fontFamily: 'var(--font-display)', fontSize: 14,
              outline: 'none', boxSizing: 'border-box',
            }}
          />
        </div>
      </div>

      <div style={{
        position: 'absolute', bottom: 0, left: 0, right: 0,
        padding: '12px 16px 24px',
        background: 'linear-gradient(to top, var(--surface-default) 60%, transparent)',
      }}>
        <Button variant="primary" fullWidth onClick={() => onSubmit && onSubmit(mood, note)}>
          Завершить check-in
        </Button>
      </div>
    </div>
  );
};

// CheckInSuccess — teal-green circle + "Записано"
const CheckInSuccessScreen = ({ onDone }) => (
  <div style={{
    position: 'absolute', inset: 0,
    background: 'var(--surface-default)',
    overflow: 'hidden',
  }}>
    <MandalaBackdrop />
    <div style={{
      position: 'relative', zIndex: 1, height: '100%',
      display: 'flex', flexDirection: 'column',
      padding: '120px 28px 40px', boxSizing: 'border-box',
      textAlign: 'center',
    }}>
      <div style={{
        width: 140, height: 140, margin: '0 auto 24px',
        borderRadius: 999, background: 'var(--accent-teal)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        boxShadow: '0 0 80px rgba(118,221,230,0.5)',
      }}>
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#fff"
             strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
      </div>
      <h2 style={{ margin: '0 0 8px', fontFamily: 'var(--font-display)',
                   fontSize: 28, color: 'var(--text-primary)', fontWeight: 400 }}>
        Записано
      </h2>
      <p style={{ margin: 0, fontSize: 14, color: 'var(--text-secondary)',
                  lineHeight: 1.5, maxWidth: 280, marginInline: 'auto' }}>
        Ваше состояние сохранено. Мы учтём его в рекомендациях и аналитике.
      </p>
      <div style={{ flex: 1 }}/>
      <Button variant="primary" fullWidth onClick={onDone}>Продолжить</Button>
    </div>
  </div>
);

window.CheckInScreen = CheckInScreen;
window.CheckInSuccessScreen = CheckInSuccessScreen;

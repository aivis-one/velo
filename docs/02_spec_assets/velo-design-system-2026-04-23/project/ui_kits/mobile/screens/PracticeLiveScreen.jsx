// PracticeLive — during-session UI with video tile, timer, pause, "Покинуть" CTA
const PracticeLiveScreen = ({ onBack, onLeave }) => {
  const [elapsed, setElapsed] = React.useState(732); // 12:12
  React.useEffect(() => {
    const id = setInterval(() => setElapsed(e => e + 1), 1000);
    return () => clearInterval(id);
  }, []);
  const mm = String(Math.floor(elapsed / 60)).padStart(2, '0');
  const ss = String(elapsed % 60).padStart(2, '0');
  const total = 45 * 60;
  const pct = Math.min(1, elapsed / total);

  return (
    <div style={{
      position: 'absolute', inset: 0,
      background: 'var(--surface-default)',
      display: 'flex', flexDirection: 'column',
    }}>
      <div style={{
        flex: 1, overflowY: 'auto',
        padding: '48px 0 140px',
        display: 'flex', flexDirection: 'column', gap: 16,
      }}>
        <BackHeader title="" onBack={onBack} trailing={
          <Chip variant="status" color="error">
            <span style={{ width: 8, height: 8, borderRadius: 999, background: 'currentColor',
                           display: 'inline-block', marginRight: 4,
                           animation: 'velo-pulse 1.4s ease-in-out infinite' }}/>
            В эфире
          </Chip>
        } />

        {/* Video */}
        <div style={{ padding: '0 16px' }}>
          <VideoTile label="live video" />
        </div>

        {/* Title + master */}
        <div style={{ padding: '0 16px' }}>
          <div style={{ fontSize: 22, color: 'var(--text-primary)' }}>Утренняя медитация</div>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>
            Alex Mindful · 127 участников
          </div>
        </div>

        {/* Timer */}
        <div style={{ padding: '0 16px' }}>
          <Card>
            <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between',
                          marginBottom: 10 }}>
              <span style={{ fontFamily: 'var(--font-display)', fontSize: 36,
                             color: 'var(--text-primary)', letterSpacing: '0.02em' }}>
                {mm}:{ss}
              </span>
              <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>из 45:00</span>
            </div>
            <div style={{ height: 6, background: 'var(--surface-muted)', borderRadius: 200,
                          overflow: 'hidden' }}>
              <div style={{ width: `${pct * 100}%`, height: '100%',
                            background: 'var(--accent-teal)', transition: 'width 1000ms linear' }}/>
            </div>
          </Card>
        </div>

        {/* Current phase */}
        <div style={{ padding: '0 16px' }}>
          <Card variant="flat">
            <div style={{ fontSize: 11, color: 'var(--text-muted)',
                          textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 4 }}>
              Сейчас
            </div>
            <div style={{ fontSize: 15, color: 'var(--text-primary)' }}>
              Сканирование тела — грудь и плечи
            </div>
          </Card>
        </div>

        {/* Participant avatars */}
        <div style={{ padding: '0 16px', display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ display: 'flex' }}>
            {['АН','ДК','МВ','ЕЛ'].map((x, i) => (
              <div key={i} style={{ marginLeft: i === 0 ? 0 : -10 }}>
                <Avatar size={32}
                        initials={x}
                        color={['teal','pink','warm','muted'][i]}
                        style={{ border: '2px solid var(--surface-default)' }}/>
              </div>
            ))}
          </div>
          <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
            +123 практикуют с вами
          </span>
        </div>
      </div>

      {/* Sticky controls */}
      <div style={{
        position: 'absolute', bottom: 0, left: 0, right: 0,
        padding: '12px 16px 24px',
        background: 'linear-gradient(to top, var(--surface-default) 60%, transparent)',
        display: 'flex', gap: 10,
      }}>
        <Button variant="secondary" style={{ flex: 1 }}>Пауза</Button>
        <Button variant="ghost" onClick={onLeave}
                style={{ flex: 1, color: 'var(--feedback-error)' }}>
          Покинуть практику
        </Button>
      </div>
    </div>
  );
};

window.PracticeLiveScreen = PracticeLiveScreen;

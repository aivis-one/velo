// BookingSuccess — high-five illustration + "Готово!" + details + buttons
const BookingSuccessScreen = ({ onGoCalendar, onGoHome }) => (
  <div style={{
    position: 'absolute', inset: 0,
    background: 'var(--surface-default)',
    overflow: 'hidden',
  }}>
    <MandalaBackdrop />

    <div style={{
      position: 'relative', zIndex: 1, height: '100%',
      display: 'flex', flexDirection: 'column',
      padding: '100px 28px 40px', boxSizing: 'border-box',
    }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{
          width: 120, height: 120, margin: '0 auto 20px',
          borderRadius: 999, background: 'rgba(118,221,230,0.35)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 0 80px rgba(118,221,230,0.4)',
        }}>
          <img src="../../assets/brand-icons/high-five.png" alt=""
               style={{ width: 72, height: 72 }}/>
        </div>
        <h2 style={{ margin: '0 0 8px', fontFamily: 'var(--font-display)',
                     fontSize: 28, color: 'var(--text-primary)', fontWeight: 400 }}>
          Готово!
        </h2>
        <p style={{ margin: 0, fontFamily: 'var(--font-display)',
                    fontSize: 14, color: 'var(--text-secondary)',
                    lineHeight: 1.5, maxWidth: 280, marginInline: 'auto' }}>
          Вы записаны на «Утренняя медитация». Напомним за 15 минут до начала.
        </p>
      </div>

      <div style={{ marginTop: 28 }}>
        <Card>
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '2px 0' }}>
            <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Дата</span>
            <span style={{ fontSize: 13, color: 'var(--text-primary)' }}>Сегодня, 07:30</span>
          </div>
          <div style={{ height: 1, background: 'var(--border-subtle)', margin: '10px 0' }}/>
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '2px 0' }}>
            <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Мастер</span>
            <span style={{ fontSize: 13, color: 'var(--text-primary)' }}>Alex Mindful</span>
          </div>
          <div style={{ height: 1, background: 'var(--border-subtle)', margin: '10px 0' }}/>
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '2px 0' }}>
            <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Формат</span>
            <Chip variant="status" color="teal">Live</Chip>
          </div>
        </Card>
      </div>

      <div style={{ flex: 1 }}/>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <Button variant="primary" fullWidth onClick={onGoCalendar}>
          Открыть в календаре
        </Button>
        <Button variant="ghost" fullWidth onClick={onGoHome}>На главную</Button>
      </div>
    </div>
  </div>
);

window.BookingSuccessScreen = BookingSuccessScreen;

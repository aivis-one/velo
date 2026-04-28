// Dashboard — matches mockup "3 Home / Dashboard"
// weekday strip → warm check-in nudge → stats row → contraindications callout →
// ближайшая практика → рекомендации list
const DashboardScreen = ({ theme, setTheme, onGoState, onTab, activeTab,
                           onOpenPractice, onOpenCheckIn, onOpenBooking }) => {
  const today = new Date();
  const todayIdx = (today.getDay() + 6) % 7; // Mon=0..Sun=6
  const start = new Date(today);
  start.setDate(start.getDate() - todayIdx);
  const days = Array.from({ length: 7 }).map((_, i) => {
    const d = new Date(start);
    d.setDate(start.getDate() + i);
    return { num: d.getDate(), dot: [0, 2, 4, todayIdx].includes(i) };
  });
  const [activeDay, setActiveDay] = React.useState(todayIdx);

  const practices = [
    { title: 'Утренняя медитация', meta: 'Alex Mindful · 45 мин',
      iconSrc: '../../assets/brand-icons/meditation.png', tag: 'сегодня', tagColor: 'teal' },
    { title: 'Дыхание 4-7-8', meta: 'Maria Flow · 10 мин',
      iconSrc: '../../assets/brand-icons/wind.png', tag: 'скоро', tagColor: 'warm' },
    { title: 'Вечерний дневник', meta: 'Свободная форма · 15 мин',
      iconSrc: '../../assets/brand-icons/quill-pen.png', tag: 'вечером', tagColor: 'pink' },
    { title: 'Фокус на теле', meta: 'Дмитрий М. · 20 мин',
      iconSrc: '../../assets/brand-icons/brain.png', tag: 'завтра', tagColor: 'teal' },
  ];

  return (
    <div style={{
      position: 'absolute', inset: 0,
      background: 'var(--surface-default)',
      display: 'flex', flexDirection: 'column',
    }}>
      <div style={{
        flex: 1, overflowY: 'auto',
        padding: '48px 0 100px',
        display: 'flex', flexDirection: 'column', gap: 18,
      }}>
        <AppHeader theme={theme} setTheme={setTheme} />

        {/* Weekday strip */}
        <div style={{ padding: '0 16px' }}>
          <WeekdayStrip days={days} activeIndex={activeDay} onSelect={setActiveDay} />
        </div>

        {/* Warm check-in nudge */}
        <div style={{ padding: '0 16px' }}>
          <CheckInCard
            title="Пора на check-in!"
            subtitle="Утренняя медитация через 30 минут"
            time="07:30"
            onClick={onOpenCheckIn}
          />
        </div>

        {/* Stat row */}
        <div style={{ display: 'flex', gap: 12, padding: '0 16px' }}>
          <Card style={{ flex: 1, padding: 14 }}>
            <div style={{ fontSize: 11, color: 'var(--text-muted)',
                          textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: 6 }}>
              эта неделя
            </div>
            <div style={{ fontSize: 28, color: 'var(--text-primary)' }}>
              12<span style={{ fontSize: 14, color: 'var(--text-secondary)', marginLeft: 6 }}>практик</span>
            </div>
          </Card>
          <Card style={{ flex: 1, padding: 14 }}>
            <div style={{ fontSize: 11, color: 'var(--text-muted)',
                          textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: 6 }}>
              сегодня
            </div>
            <div style={{ fontSize: 28, color: 'var(--text-primary)' }}>
              45<span style={{ fontSize: 14, color: 'var(--text-secondary)', marginLeft: 6 }}>мин</span>
            </div>
          </Card>
        </div>

        {/* Contraindications callout */}
        <div style={{ padding: '0 16px' }}>
          <Callout
            variant="warning"
            title="Противопоказания"
            subtitle="При повышенном давлении — уточните у мастера перед Live"
          />
        </div>

        {/* Next practice */}
        <div style={{ padding: '0 16px', display: 'flex', flexDirection: 'column', gap: 12 }}>
          <SectionHeader title="Ближайшая практика" action="Все →" />
          <BalanceCard
            subtitle="на сегодня"
            title="Утренняя медитация"
            meta="Alex Mindful · 45 мин · рекомендовано"
            iconSrc="../../assets/brand-icons/meditation.png"
            cta
            onClick={onOpenPractice}
          />
        </div>

        {/* Recommended list */}
        <div style={{ padding: '0 16px', display: 'flex', flexDirection: 'column', gap: 10 }}>
          <SectionHeader title="Рекомендуем вам" action="Все →" onAction={() => onGoState('empty')} />
          {practices.map((p, i) => (
            <div key={i} onClick={onOpenPractice} style={{ cursor: 'pointer' }}>
              <PracticeItem {...p} />
            </div>
          ))}
        </div>
      </div>

      <div style={{ position: 'absolute', bottom: 24, left: 16, right: 16 }}>
        <TabBar active={activeTab} onChange={onTab} />
      </div>
    </div>
  );
};

window.DashboardScreen = DashboardScreen;

// Calendar — Месяц/Неделя toggle + weekday strip + day list with practice items
const CalendarScreen = ({ onBack, onOpenPractice }) => {
  const [view, setView] = React.useState('week');
  const today = new Date();
  const todayIdx = (today.getDay() + 6) % 7;
  const start = new Date(today);
  start.setDate(start.getDate() - todayIdx);
  const days = Array.from({ length: 7 }).map((_, i) => {
    const d = new Date(start);
    d.setDate(start.getDate() + i);
    return { num: d.getDate(), dot: [todayIdx, todayIdx + 1, todayIdx + 3].includes(i) };
  });
  const [activeDay, setActiveDay] = React.useState(todayIdx);

  const monthName = today.toLocaleDateString('ru-RU', { month: 'long', year: 'numeric' });

  return (
    <div style={{
      position: 'absolute', inset: 0,
      background: 'var(--surface-default)',
      display: 'flex', flexDirection: 'column',
    }}>
      <div style={{
        flex: 1, overflowY: 'auto',
        padding: '48px 0 40px',
        display: 'flex', flexDirection: 'column', gap: 18,
      }}>
        <BackHeader title="Календарь" onBack={onBack} />

        <div style={{ padding: '0 16px',
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ fontSize: 20, color: 'var(--text-primary)',
                        textTransform: 'capitalize' }}>{monthName}</div>
          <Segmented
            items={[{ id: 'week', label: 'Неделя' }, { id: 'month', label: 'Месяц' }]}
            active={view} onChange={setView}
          />
        </div>

        <div style={{ padding: '0 16px' }}>
          <WeekdayStrip days={days} activeIndex={activeDay} onSelect={setActiveDay} />
        </div>

        <div style={{ padding: '0 16px', display: 'flex', flexDirection: 'column', gap: 10 }}>
          <SectionHeader title="Сегодня" />
          <div onClick={onOpenPractice} style={{ cursor: 'pointer' }}>
            <PracticeItem
              title="Утренняя медитация"
              meta="Alex Mindful · 07:30 · 45 мин"
              iconSrc="../../assets/brand-icons/meditation.png"
              tag="Подтверждена" tagColor="teal"
            />
          </div>
          <div onClick={onOpenPractice} style={{ cursor: 'pointer' }}>
            <PracticeItem
              title="Дыхание 4-7-8"
              meta="Maria Flow · 19:00 · 10 мин"
              iconSrc="../../assets/brand-icons/wind.png"
              tag="Оплачено" tagColor="teal"
            />
          </div>
        </div>

        <div style={{ padding: '0 16px', display: 'flex', flexDirection: 'column', gap: 10 }}>
          <SectionHeader title="Завтра" />
          <div onClick={onOpenPractice} style={{ cursor: 'pointer' }}>
            <PracticeItem
              title="Фокус на теле"
              meta="Дмитрий М. · 08:00 · 20 мин"
              iconSrc="../../assets/brand-icons/brain.png"
              tag="Завтра" tagColor="warm"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

window.CalendarScreen = CalendarScreen;

// MyReservations — list of upcoming + past bookings with status chips
const MyReservationsScreen = ({ onBack, onOpenBooking }) => {
  const [tab, setTab] = React.useState('upcoming');

  const upcoming = [
    { title: 'Утренняя медитация', meta: 'Alex Mindful · сегодня 07:30',
      iconSrc: '../../assets/brand-icons/meditation.png',
      tag: 'Подтверждена', tagColor: 'teal' },
    { title: 'Дыхание 4-7-8', meta: 'Maria Flow · сегодня 19:00',
      iconSrc: '../../assets/brand-icons/wind.png',
      tag: 'Оплачено', tagColor: 'teal' },
    { title: 'Фокус на теле', meta: 'Дмитрий М. · завтра 08:00',
      iconSrc: '../../assets/brand-icons/brain.png',
      tag: 'Завтра', tagColor: 'warm' },
  ];
  const past = [
    { title: 'Вечерний дневник', meta: 'вчера · 21:00',
      iconSrc: '../../assets/brand-icons/quill-pen.png',
      tag: 'Завершена', tagColor: 'pink' },
    { title: 'Практика воды', meta: '18 апр · 08:30',
      iconSrc: '../../assets/brand-icons/spa.png',
      tag: 'Отменена', tagColor: 'pink' },
  ];
  const items = tab === 'upcoming' ? upcoming : past;

  return (
    <div style={{
      position: 'absolute', inset: 0,
      background: 'var(--surface-default)',
      display: 'flex', flexDirection: 'column',
    }}>
      <div style={{
        flex: 1, overflowY: 'auto',
        padding: '48px 0 40px',
        display: 'flex', flexDirection: 'column', gap: 16,
      }}>
        <BackHeader title="Мои брони" onBack={onBack} />

        <div style={{ padding: '0 16px' }}>
          <Segmented
            items={[
              { id: 'upcoming', label: 'Предстоящие' },
              { id: 'past',     label: 'Прошедшие' },
            ]}
            active={tab} onChange={setTab}
          />
        </div>

        <div style={{ padding: '0 16px', display: 'flex', flexDirection: 'column', gap: 10 }}>
          {items.map((p, i) => (
            <div key={i} onClick={onOpenBooking} style={{ cursor: 'pointer' }}>
              <PracticeItem {...p} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

window.MyReservationsScreen = MyReservationsScreen;

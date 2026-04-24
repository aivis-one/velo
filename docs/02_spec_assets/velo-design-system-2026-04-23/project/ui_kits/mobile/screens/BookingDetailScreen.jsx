// BookingDetail — the "Бронирование" screen with slot choice + confirm
const BookingDetailScreen = ({ onBack, onConfirm, onCancel }) => {
  const [slot, setSlot] = React.useState('07:30');

  const slots = ['06:30', '07:30', '08:30', '19:00'];

  return (
    <div style={{
      position: 'absolute', inset: 0,
      background: 'var(--surface-default)',
      display: 'flex', flexDirection: 'column',
    }}>
      <div style={{
        flex: 1, overflowY: 'auto',
        padding: '48px 0 180px',
        display: 'flex', flexDirection: 'column', gap: 16,
      }}>
        <BackHeader title="Бронирование" onBack={onBack} />

        {/* Summary */}
        <div style={{ padding: '0 16px' }}>
          <Card>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{
                width: 48, height: 48, borderRadius: 12,
                background: 'var(--surface-muted)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                flex: '0 0 48px',
              }}>
                <img src="../../assets/brand-icons/meditation.png"
                     alt="" style={{ width: 30, height: 30 }}/>
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 16, color: 'var(--text-primary)' }}>Утренняя медитация</div>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                  Alex Mindful · 45 мин
                </div>
              </div>
              <Chip variant="status" color="teal">Live</Chip>
            </div>
          </Card>
        </div>

        {/* Date */}
        <div style={{ padding: '0 16px', display: 'flex', flexDirection: 'column', gap: 10 }}>
          <SectionHeader title="Дата" />
          <Card style={{ padding: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ fontSize: 15, color: 'var(--text-primary)' }}>
                Сегодня, 22 апреля
              </div>
              <Chip variant="tag" color="teal">Доступно</Chip>
            </div>
          </Card>
        </div>

        {/* Slot picker */}
        <div style={{ padding: '0 16px', display: 'flex', flexDirection: 'column', gap: 10 }}>
          <SectionHeader title="Время" />
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {slots.map(s => (
              <Chip key={s} variant="filter" color="muted"
                    active={s === slot} onClick={() => setSlot(s)}>
                {s}
              </Chip>
            ))}
          </div>
        </div>

        {/* Price */}
        <div style={{ padding: '0 16px' }}>
          <Card>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ fontSize: 14, color: 'var(--text-secondary)' }}>Стоимость</div>
              <div style={{ fontSize: 22, color: 'var(--text-primary)' }}>
                1 200 <span style={{ fontSize: 14, color: 'var(--text-secondary)' }}>₽</span>
              </div>
            </div>
            <div style={{ marginTop: 10, fontSize: 12, color: 'var(--text-muted)' }}>
              Отмена бесплатно до 07:00
            </div>
          </Card>
        </div>

        <div style={{ padding: '0 16px' }}>
          <Callout variant="info" title="Live-трансляция"
                   subtitle="Ссылка придёт за 15 минут до начала" />
        </div>
      </div>

      {/* Sticky CTA */}
      <div style={{
        position: 'absolute', bottom: 0, left: 0, right: 0,
        padding: '12px 16px 24px',
        background: 'linear-gradient(to top, var(--surface-default) 60%, transparent)',
        display: 'flex', flexDirection: 'column', gap: 10,
      }}>
        <Button variant="primary" fullWidth onClick={onConfirm}>Подтвердить · {slot}</Button>
        <Button variant="ghost" fullWidth onClick={onCancel}>Отменить бронирование</Button>
      </div>
    </div>
  );
};

window.BookingDetailScreen = BookingDetailScreen;

// PracticeDetail — hero card + master + accordions + "Записаться" CTA
const PracticeDetailScreen = ({ onBack, onBook }) => (
  <div style={{
    position: 'absolute', inset: 0,
    background: 'var(--surface-default)',
    display: 'flex', flexDirection: 'column',
  }}>
    <div style={{
      flex: 1, overflowY: 'auto',
      padding: '48px 0 120px',
      display: 'flex', flexDirection: 'column', gap: 16,
    }}>
      <BackHeader title="Практика" onBack={onBack} />

      {/* Hero */}
      <div style={{ padding: '0 16px' }}>
        <div style={{
          position: 'relative',
          background: 'var(--surface-elevated)', borderRadius: 15,
          boxShadow: 'var(--shadow-md)',
          padding: 20, overflow: 'hidden',
        }}>
          <div style={{
            position: 'absolute', right: -40, top: -30, width: 180, height: 180,
            background: 'radial-gradient(circle, rgba(247,149,162,0.25), transparent 70%)',
          }}/>
          <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 10 }}>
            <Chip variant="tag" color="teal">Медитация</Chip>
            <Chip variant="tag" color="warm">45 мин</Chip>
          </div>
          <h2 style={{ margin: 0, fontFamily: 'var(--font-display)',
                       fontSize: 26, color: 'var(--text-primary)', lineHeight: 1.15 }}>
            Утренняя медитация
          </h2>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 8 }}>
            Мягкое пробуждение тела и ума через дыхание и сканирование внимания
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 20, marginTop: 16,
                        fontSize: 13, color: 'var(--text-secondary)' }}>
            <span>📅 Сегодня · 07:30</span>
            <span>🧘 Live</span>
          </div>
        </div>
      </div>

      {/* Master card */}
      <div style={{ padding: '0 16px' }}>
        <MasterCard
          name="Alex Mindful"
          photo="../../assets/masters/alex-mindful.svg"
          tags={[
            { label: 'Медитация', color: 'teal' },
            { label: 'Mindfulness', color: 'pink' },
            { label: 'MBSR', color: 'warm' },
          ]}
        />
      </div>

      {/* Contraindications */}
      <div style={{ padding: '0 16px' }}>
        <Callout variant="warning" title="Противопоказания"
                 subtitle="Не рекомендуется при остром состоянии тревоги" />
      </div>

      {/* Accordions */}
      <div style={{ padding: '0 16px', display: 'flex', flexDirection: 'column', gap: 10 }}>
        <Accordion title="О практике" defaultOpen>
          Утренняя медитация длится 45 минут и сочетает дыхательные техники,
          сканирование тела и мягкую фиксацию внимания. Подходит для новичков
          и регулярных практиков.
        </Accordion>
        <Accordion title="Что подготовить">
          Удобная одежда, тёплое одеяло или шаль, коврик или подушка для сидения,
          стакан тёплой воды рядом.
        </Accordion>
        <Accordion title="Методы">
          Pranayama · сканирование тела · осознанное дыхание · короткая визуализация
        </Accordion>
      </div>
    </div>

    {/* Sticky CTA */}
    <div style={{
      position: 'absolute', bottom: 0, left: 0, right: 0,
      padding: '12px 16px 24px',
      background: 'linear-gradient(to top, var(--surface-default) 60%, transparent)',
    }}>
      <Button variant="primary" fullWidth onClick={onBook}>Записаться</Button>
    </div>
  </div>
);

window.PracticeDetailScreen = PracticeDetailScreen;

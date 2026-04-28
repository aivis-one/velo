// AI Summary — feed-style insights card with mood dots, weekly recap, next focus
const AISummaryScreen = ({ onBack }) => (
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
      <BackHeader title="AI-аналитика" onBack={onBack} />

      {/* Header card */}
      <div style={{ padding: '0 16px' }}>
        <Card style={{ padding: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10 }}>
            <div style={{
              width: 40, height: 40, borderRadius: 12,
              background: 'var(--surface-muted)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <img src="../../assets/brand-icons/brain.png" alt=""
                   style={{ width: 26, height: 26 }}/>
            </div>
            <div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)',
                            textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Неделя 16
              </div>
              <div style={{ fontSize: 18, color: 'var(--text-primary)' }}>Саммари практик</div>
            </div>
          </div>
          <p style={{ margin: 0, fontSize: 14, lineHeight: 1.55, color: 'var(--text-primary)' }}>
            На этой неделе вы <span style={{ color: 'var(--steel-primary)' }}>практиковали 12 раз</span> —
            больше, чем в среднем. Настроение стабильное, с лёгким подъёмом
            к середине недели.
          </p>
        </Card>
      </div>

      {/* Mood row */}
      <div style={{ padding: '0 16px' }}>
        <Card>
          <div style={{ fontSize: 11, color: 'var(--text-muted)',
                        textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: 12 }}>
            Настроение по дням
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 8 }}>
            {['ПН','ВТ','СР','ЧТ','ПТ','СБ','ВС'].map((lbl, i) => {
              const moods = ['neutral','calm','calm','calm','sad','calm','neutral'];
              const src = `../../assets/mood/mood-${moods[i]}.svg`;
              return (
                <div key={i} style={{
                  display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6,
                }}>
                  <img src={src} alt="" style={{ width: 32, height: 32 }}/>
                  <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{lbl}</span>
                </div>
              );
            })}
          </div>
        </Card>
      </div>

      {/* Insights */}
      <div style={{ padding: '0 16px', display: 'flex', flexDirection: 'column', gap: 10 }}>
        <SectionHeader title="Инсайты" />
        <Card>
          <div style={{ fontSize: 14, color: 'var(--text-primary)', marginBottom: 4 }}>
            🌬 Дыхание — ваш якорь
          </div>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.4 }}>
            Практики дыхания 4-7-8 стабильно улучшают ваше состояние за 15 минут.
          </div>
        </Card>
        <Card>
          <div style={{ fontSize: 14, color: 'var(--text-primary)', marginBottom: 4 }}>
            🌅 Утром вы наиболее открыты
          </div>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.4 }}>
            Check-in до 9:00 — самые ровные оценки настроения.
          </div>
        </Card>
      </div>

      {/* Next focus */}
      <div style={{ padding: '0 16px', display: 'flex', flexDirection: 'column', gap: 10 }}>
        <SectionHeader title="Следующий фокус" />
        <Card variant="warm">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <img src="../../assets/brand-icons/quill-pen-story.png" alt=""
                 style={{ width: 40, height: 40 }}/>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 15, color: 'var(--warm-deep)' }}>Вечерний дневник</div>
              <div style={{ fontSize: 12, color: 'var(--warm-deep)', opacity: 0.85 }}>
                Добавит структуру к наблюдениям за собой
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  </div>
);

window.AISummaryScreen = AISummaryScreen;

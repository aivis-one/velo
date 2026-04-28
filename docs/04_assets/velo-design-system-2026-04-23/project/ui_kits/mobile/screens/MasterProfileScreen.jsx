// MasterProfile — photo hero + name + tags + bio + upcoming sessions + follow CTA
const MasterProfileScreen = ({ onBack, onBookPractice }) => (
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
      <BackHeader title="Мастер" onBack={onBack} />

      {/* Hero photo + overlay */}
      <div style={{ padding: '0 16px' }}>
        <div style={{
          position: 'relative',
          borderRadius: 15, overflow: 'hidden',
          boxShadow: 'var(--shadow-md)',
          aspectRatio: '4 / 5',
          background: 'linear-gradient(135deg, rgba(247,149,162,0.25), rgba(118,221,230,0.2))',
        }}>
          <img src="../../assets/masters/alex-mindful.svg" alt=""
               style={{ width: '100%', height: '100%', objectFit: 'contain',
                        padding: 16, boxSizing: 'border-box' }}/>
          <div style={{
            position: 'absolute', bottom: 0, left: 0, right: 0,
            padding: '60px 20px 20px',
            background: 'linear-gradient(to top, rgba(20,30,45,0.75), transparent)',
            color: '#fff',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
              <span style={{ fontFamily: 'var(--font-display)', fontSize: 24 }}>Alex Mindful</span>
              <span style={{
                width: 20, height: 20, borderRadius: 999,
                background: 'var(--accent-teal)',
                display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#fff"
                     strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </span>
            </div>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              <Chip variant="tag" color="teal">Медитация</Chip>
              <Chip variant="tag" color="pink">Mindfulness</Chip>
              <Chip variant="tag" color="warm">MBSR</Chip>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: 'flex', gap: 12, padding: '0 16px' }}>
        {[
          { num: '320', label: 'практик' },
          { num: '4.9', label: 'рейтинг' },
          { num: '12', label: 'лет опыта' },
        ].map((s, i) => (
          <Card key={i} style={{ flex: 1, padding: 14, textAlign: 'center' }}>
            <div style={{ fontSize: 22, color: 'var(--text-primary)' }}>{s.num}</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)',
                          textTransform: 'uppercase', letterSpacing: '0.04em', marginTop: 4 }}>
              {s.label}
            </div>
          </Card>
        ))}
      </div>

      {/* Bio */}
      <div style={{ padding: '0 16px', display: 'flex', flexDirection: 'column', gap: 10 }}>
        <SectionHeader title="О мастере" />
        <Card>
          <p style={{ margin: 0, fontSize: 14, lineHeight: 1.5, color: 'var(--text-secondary)' }}>
            Практикую медитацию 12 лет, преподаю — 7. Сертифицированный инструктор MBSR.
            В моих сессиях — мягкий, структурный подход, много дыхательных техник
            и внимания к телу.
          </p>
        </Card>
      </div>

      {/* Upcoming */}
      <div style={{ padding: '0 16px', display: 'flex', flexDirection: 'column', gap: 10 }}>
        <SectionHeader title="Ближайшие практики" action="Все →" />
        <div onClick={onBookPractice} style={{ cursor: 'pointer' }}>
          <PracticeItem
            title="Утренняя медитация"
            meta="Сегодня · 07:30 · 45 мин"
            iconSrc="../../assets/brand-icons/meditation.png"
            tag="Live" tagColor="teal"
          />
        </div>
        <div onClick={onBookPractice} style={{ cursor: 'pointer' }}>
          <PracticeItem
            title="Вечерняя расслабляющая"
            meta="Завтра · 21:00 · 30 мин"
            iconSrc="../../assets/brand-icons/spa.png"
            tag="Запись" tagColor="warm"
          />
        </div>
      </div>
    </div>

    {/* Sticky CTA */}
    <div style={{
      position: 'absolute', bottom: 0, left: 0, right: 0,
      padding: '12px 16px 24px',
      background: 'linear-gradient(to top, var(--surface-default) 60%, transparent)',
    }}>
      <Button variant="primary" fullWidth onClick={onBookPractice}>
        Записаться на практику
      </Button>
    </div>
  </div>
);

window.MasterProfileScreen = MasterProfileScreen;

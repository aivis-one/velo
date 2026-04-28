// Onboarding — 3 slides with illustration + title + description + page dots + next arrow.
// Illustrations: Live practices, Карта себя, AI-аналитика.

const ONBOARDING_SLIDES = [
  {
    illus: '../../assets/illustrations/live-practices.svg',
    title: 'Live практики\nс мастерами',
    text: 'Выбирайте практику под своё состояние и подключайтесь к live-сессии прямо из приложения',
  },
  {
    illus: '../../assets/illustrations/self-map.svg',
    title: 'Карта себя',
    text: 'Живая карта, которая меняется вместе с вами, оставаясь актуальной по мере того, как вы продолжаете исследовать себя',
  },
  {
    illus: '../../assets/illustrations/ai-analytics.svg',
    title: 'AI-аналитика',
    text: 'Собранный контекст из всех инструментов экосистемы — рекомендации, которые учитывают всю картину целиком',
  },
];

const OnboardingScreen = ({ onDone }) => {
  const [idx, setIdx] = React.useState(0);
  const slide = ONBOARDING_SLIDES[idx];
  const advance = () => {
    if (idx < ONBOARDING_SLIDES.length - 1) setIdx(idx + 1);
    else onDone && onDone();
  };
  return (
    <div style={{
      position: 'absolute', inset: 0,
      background: 'var(--surface-default)',
      overflow: 'hidden',
    }}>
      <MandalaBackdrop />

      {/* Skip */}
      <button
        onClick={onDone}
        className="velo-btn"
        style={{
          position: 'absolute', top: 56, right: 20, zIndex: 2,
          background: 'transparent', border: 0, cursor: 'pointer',
          fontFamily: 'var(--font-display)', fontSize: 14,
          color: 'var(--text-secondary)',
        }}
      >
        Пропустить
      </button>

      <div style={{
        position: 'relative', zIndex: 1,
        height: '100%', display: 'flex', flexDirection: 'column',
        padding: '120px 28px 40px', boxSizing: 'border-box',
      }}>
        {/* Illustration */}
        <div style={{
          display: 'flex', justifyContent: 'center', alignItems: 'center',
          minHeight: 180, marginBottom: 36,
        }}>
          <img src={slide.illus} alt="" style={{
            width: 176, height: 176, objectFit: 'contain',
          }}/>
        </div>

        {/* Title + text */}
        <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: 20 }}>
          <h2 style={{
            fontFamily: 'var(--font-display)', fontWeight: 400,
            fontSize: 28, lineHeight: 1.2, color: 'var(--text-primary)',
            margin: 0, whiteSpace: 'pre-line',
          }}>{slide.title}</h2>
          <p style={{
            fontFamily: 'var(--font-display)',
            fontSize: 14, lineHeight: 1.5, color: 'var(--text-secondary)',
            margin: 0, maxWidth: 300, marginInline: 'auto',
            textWrap: 'pretty',
          }}>{slide.text}</p>
        </div>

        <div style={{ flex: 1 }}/>

        {/* Dots + arrow */}
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <PageDots total={ONBOARDING_SLIDES.length} active={idx} />
          <ArrowPillButton onClick={advance} />
        </div>
      </div>
    </div>
  );
};

window.OnboardingScreen = OnboardingScreen;

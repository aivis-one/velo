// Welcome — splash/landing with VELΘ logo in mandala + tagline + Войти / Создать аккаунт
const WelcomeScreen = ({ onLogin, onRegister }) => (
  <div style={{
    position: 'absolute', inset: 0,
    overflow: 'hidden',
  }}>
    <MandalaBackdrop />
    <div style={{
      position: 'relative', zIndex: 1, height: '100%',
      display: 'flex', flexDirection: 'column',
      padding: '72px 28px 40px', boxSizing: 'border-box',
    }}>
      {/* Wordmark — mandala-motif backdrop provides the imagery */}
      <div style={{
        display: 'flex', justifyContent: 'center', alignItems: 'center',
        marginTop: 100, marginBottom: 40,
      }}>
        <span style={{
          fontFamily: 'var(--font-display)',
          fontSize: 56, lineHeight: 1,
          color: 'var(--steel-primary)',
          letterSpacing: '0.02em',
        }}>VELΘ</span>
      </div>

      <div style={{ textAlign: 'center', marginBottom: 32 }}>
        <p style={{
          fontFamily: 'var(--font-display)', fontSize: 16,
          lineHeight: 1.5, color: 'var(--text-secondary)',
          margin: 0, maxWidth: 280, marginInline: 'auto',
        }}>
          Пространство для практики<br/>и внутреннего развития
        </p>
      </div>

      <div style={{ flex: 1 }}/>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <Button variant="primary" fullWidth onClick={onLogin}>Войти</Button>
        <Button variant="outline" fullWidth onClick={onRegister}>Создать аккаунт</Button>
      </div>
    </div>
  </div>
);

// OAuthLoadingScreen — "Вход через Google..." splash
const OAuthLoadingScreen = ({ provider = 'Google' }) => (
  <div style={{
    position: 'absolute', inset: 0,
    overflow: 'hidden',
  }}>
    <MandalaBackdrop />
    <div style={{
      position: 'relative', zIndex: 1, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center', gap: 28,
      padding: '0 28px',
    }}>
      <div style={{ position: 'relative',
                    display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <img src="../../assets/brand/mandala-runes.svg" alt=""
             style={{ width: 180, height: 180, opacity: 0.85,
                      animation: 'velo-rotate 40s linear infinite' }}/>
        <span style={{
          position: 'absolute',
          fontFamily: 'var(--font-display)', fontSize: 28,
          color: 'var(--steel-primary)',
        }}>VELΘ</span>
      </div>
      <div style={{
        fontFamily: 'var(--font-display)', fontSize: 16,
        color: 'var(--text-primary)',
      }}>
        Вход через {provider}...
      </div>
      <style>{`@keyframes velo-rotate { to { transform: rotate(360deg); } }`}</style>
    </div>
  </div>
);

window.WelcomeScreen = WelcomeScreen;
window.OAuthLoadingScreen = OAuthLoadingScreen;

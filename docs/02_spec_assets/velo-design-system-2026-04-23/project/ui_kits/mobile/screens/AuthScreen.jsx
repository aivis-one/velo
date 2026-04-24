// Login — "С возвращением!" form with OAuth buttons. Matches mockup Login.png
const AuthScreen = ({ onLogin, onGoRegister, onOAuth, onBack }) => {
  const [email, setEmail] = React.useState('alina@velo.app');
  const [password, setPassword] = React.useState('');

  return (
    <div style={{
      position: 'absolute', inset: 0,
      background: 'var(--surface-default)',
      overflow: 'hidden',
    }}>
      <MandalaBackdrop />

      <div style={{
        position: 'relative', zIndex: 1,
        padding: '64px 24px 24px',
        display: 'flex', flexDirection: 'column',
        height: '100%', boxSizing: 'border-box',
        overflowY: 'auto',
      }}>
        {/* Logo-in-mandala + copy */}
        <div style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center',
          textAlign: 'center', marginBottom: 20,
        }}>
          <div style={{
            position: 'relative',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            marginBottom: 12,
          }}>
            <img src="../../assets/brand/mandala-runes.svg" alt=""
                 style={{ width: 120, height: 120, opacity: 0.9 }}/>
            <span style={{
              position: 'absolute',
              fontFamily: 'var(--font-display)', fontSize: 24,
              color: 'var(--steel-primary)',
            }}>VELΘ</span>
          </div>
          <div style={{ fontSize: 26, color: 'var(--text-primary)', marginBottom: 4 }}>
            С возвращением!
          </div>
          <div style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
            Войдите, чтобы продолжить практику
          </div>
        </div>

        {/* Form */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 8 }}>
          <Input value={email}    onChange={setEmail}    placeholder="E-mail"  type="email" />
          <Input value={password} onChange={setPassword} placeholder="Пароль" type="password" />
        </div>

        <div style={{ textAlign: 'right', marginBottom: 16 }}>
          <button className="velo-btn" style={{
            border: 0, background: 'transparent', cursor: 'pointer',
            color: 'var(--text-accent)', fontSize: 13,
            fontFamily: 'var(--font-display)',
          }}>Забыли пароль?</button>
        </div>

        <Button variant="primary" fullWidth onClick={onLogin}>Войти</Button>

        <div style={{
          display: 'flex', alignItems: 'center', gap: 10,
          margin: '20px 0',
          color: 'var(--text-secondary)', fontSize: 13,
        }}>
          <div style={{ flex: 1, height: 1, background: 'var(--border-subtle)' }}/>
          <span>или</span>
          <div style={{ flex: 1, height: 1, background: 'var(--border-subtle)' }}/>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <Button variant="outline" fullWidth
                  onClick={() => onOAuth && onOAuth('Google')}>
            Войти через Google
          </Button>
          <Button variant="outline" fullWidth
                  onClick={() => onOAuth && onOAuth('Apple')}>
            Войти через Apple
          </Button>
        </div>

        <div style={{ textAlign: 'center', marginTop: 20,
                      fontSize: 13, color: 'var(--text-secondary)' }}>
          Нет аккаунта?{' '}
          <button onClick={onGoRegister} className="velo-btn" style={{
            border: 0, background: 'transparent', cursor: 'pointer',
            color: 'var(--text-primary)',
            fontFamily: 'var(--font-display)', fontSize: 13,
            fontWeight: 400,
          }}>Создать</button>
        </div>

        <div style={{ flex: 1 }}/>

        {onBack && (
          <div style={{ marginTop: 24 }}>
            <button
              onClick={onBack}
              className="velo-btn"
              style={{
                width: 44, height: 44, border: 0,
                background: 'var(--surface-elevated)',
                boxShadow: 'var(--shadow-md)',
                borderRadius: 200, cursor: 'pointer',
                color: 'var(--text-primary)',
                display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
              }}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                   strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="19" y1="12" x2="5" y2="12"/>
                <polyline points="12 19 5 12 12 5"/>
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// Register — "Создать аккаунт" form
const RegisterScreen = ({ onCreate, onGoLogin, onOAuth, onBack }) => {
  const [name, setName] = React.useState('');
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');

  return (
    <div style={{
      position: 'absolute', inset: 0,
      background: 'var(--surface-default)',
      overflow: 'hidden',
    }}>
      <MandalaBackdrop />

      <div style={{
        position: 'relative', zIndex: 1,
        padding: '64px 24px 24px',
        display: 'flex', flexDirection: 'column',
        height: '100%', boxSizing: 'border-box',
        overflowY: 'auto',
      }}>
        <div style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center',
          textAlign: 'center', marginBottom: 20,
        }}>
          <div style={{
            position: 'relative',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            marginBottom: 12,
          }}>
            <img src="../../assets/brand/mandala-runes.svg" alt=""
                 style={{ width: 120, height: 120, opacity: 0.9 }}/>
            <span style={{
              position: 'absolute',
              fontFamily: 'var(--font-display)', fontSize: 24,
              color: 'var(--steel-primary)',
            }}>VELΘ</span>
          </div>
          <div style={{ fontSize: 26, color: 'var(--text-primary)', marginBottom: 4 }}>
            Создать аккаунт
          </div>
          <div style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
            Начните свой путь к осознанности
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 18 }}>
          <Input value={name}     onChange={setName}     placeholder="Как вас зовут?" />
          <Input value={email}    onChange={setEmail}    placeholder="E-mail"         type="email" />
          <Input value={password} onChange={setPassword} placeholder="Пароль (от 8 символов)" type="password" />
        </div>

        <Button variant="primary" fullWidth onClick={onCreate}>Создать аккаунт</Button>

        <div style={{
          display: 'flex', alignItems: 'center', gap: 10,
          margin: '18px 0',
          color: 'var(--text-secondary)', fontSize: 13,
        }}>
          <div style={{ flex: 1, height: 1, background: 'var(--border-subtle)' }}/>
          <span>или</span>
          <div style={{ flex: 1, height: 1, background: 'var(--border-subtle)' }}/>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <Button variant="outline" fullWidth
                  onClick={() => onOAuth && onOAuth('Google')}>
            Войти через Google
          </Button>
          <Button variant="outline" fullWidth
                  onClick={() => onOAuth && onOAuth('Apple')}>
            Войти через Apple
          </Button>
        </div>

        <div style={{ textAlign: 'center', marginTop: 20,
                      fontSize: 13, color: 'var(--text-secondary)' }}>
          Уже есть аккаунт?{' '}
          <button onClick={onGoLogin} className="velo-btn" style={{
            border: 0, background: 'transparent', cursor: 'pointer',
            color: 'var(--text-primary)',
            fontFamily: 'var(--font-display)', fontSize: 13,
          }}>Войти</button>
        </div>

        <div style={{ flex: 1 }}/>

        {onBack && (
          <div style={{ marginTop: 24 }}>
            <button
              onClick={onBack}
              className="velo-btn"
              style={{
                width: 44, height: 44, border: 0,
                background: 'var(--surface-elevated)',
                boxShadow: 'var(--shadow-md)',
                borderRadius: 200, cursor: 'pointer',
                color: 'var(--text-primary)',
                display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
              }}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                   strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="19" y1="12" x2="5" y2="12"/>
                <polyline points="12 19 5 12 12 5"/>
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

window.AuthScreen = AuthScreen;
window.RegisterScreen = RegisterScreen;

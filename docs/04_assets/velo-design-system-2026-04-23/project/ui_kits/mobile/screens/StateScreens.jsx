// State screens — Loading, Empty, Error
const LoadingScreen = () => (
  <div style={{
    position: 'absolute', inset: 0,
    background: 'var(--surface-default)',
    display: 'flex', flexDirection: 'column',
    alignItems: 'center', justifyContent: 'center',
    padding: 32, gap: 16,
  }}>
    <div style={{
      width: 64, height: 64, borderRadius: 999,
      border: '3px solid var(--teal-100)',
      borderTopColor: 'var(--accent-teal)',
      animation: 'velo-spin 1.1s linear infinite',
    }} />
    <style>{`@keyframes velo-spin { to { transform: rotate(360deg); } }`}</style>
    <div style={{ fontSize: 20, color: 'var(--text-primary)', marginTop: 8 }}>
      Загружаем практики
    </div>
    <div style={{ fontSize: 14, color: 'var(--text-secondary)', textAlign: 'center' }}>
      Это может занять пару секунд
    </div>
  </div>
);

const EmptyScreen = ({ onRetry, onBack }) => (
  <div style={{
    position: 'absolute', inset: 0,
    background: 'var(--surface-default)',
    display: 'flex', flexDirection: 'column',
    alignItems: 'center', justifyContent: 'center',
    padding: 32, gap: 16,
  }}>
    <div style={{
      width: 96, height: 96, borderRadius: 999,
      background: 'var(--warm-100)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
    }}>
      <img src="../../assets/brand-icons/spa.png"
           alt="" style={{ width: 48, height: 48, opacity: 0.7 }} />
    </div>
    <div style={{ fontSize: 20, color: 'var(--text-primary)', marginTop: 8 }}>
      Пока нет практик
    </div>
    <div style={{
      fontSize: 14, color: 'var(--text-secondary)',
      textAlign: 'center', maxWidth: 300,
    }}>
      Запишитесь на ближайшую сессию, и она появится здесь
    </div>
    <div style={{ height: 8 }} />
    <Button variant="primary" onClick={onRetry}>Найти практику</Button>
    <Button variant="ghost" onClick={onBack}>Назад</Button>
  </div>
);

const ErrorScreen = ({ onRetry, onBack }) => (
  <div style={{
    position: 'absolute', inset: 0,
    background: 'var(--surface-default)',
    display: 'flex', flexDirection: 'column',
    alignItems: 'center', justifyContent: 'center',
    padding: 32, gap: 16,
  }}>
    <div style={{
      width: 96, height: 96, borderRadius: 999,
      background: 'var(--feedback-error)',
      color: '#fff',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: 48, lineHeight: 1,
    }}>!</div>
    <div style={{ fontSize: 20, color: 'var(--text-primary)', marginTop: 8 }}>
      Что-то пошло не так
    </div>
    <div style={{
      fontSize: 14, color: 'var(--text-secondary)',
      textAlign: 'center', maxWidth: 300,
    }}>
      Не удалось загрузить данные. Проверьте соединение и попробуйте снова.
    </div>
    <div style={{ height: 8 }} />
    <Button variant="primary" onClick={onRetry}>Попробовать снова</Button>
    <Button variant="ghost" onClick={onBack}>Отмена</Button>
  </div>
);

window.LoadingScreen = LoadingScreen;
window.EmptyScreen = EmptyScreen;
window.ErrorScreen = ErrorScreen;

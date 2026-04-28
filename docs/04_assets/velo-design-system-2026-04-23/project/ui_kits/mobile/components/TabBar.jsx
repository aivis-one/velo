// TabBar — bottom, pill, signature glow-white.
const TabBar = ({ active, onChange }) => {
  const icons = {
    home:    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M3 10 12 3l9 7v11a1 1 0 0 1-1 1h-5v-7h-6v7H4a1 1 0 0 1-1-1z"/></svg>,
    search:  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>,
    plus:    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 5v14M5 12h14"/></svg>,
    journal: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>,
    user:    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>,
  };
  const tabs = [
    { id: 'home',    label: 'Главная' },
    { id: 'search',  label: 'Поиск'   },
    { id: 'plus',    label: 'Начать', accent: true },
    { id: 'journal', label: 'Дневник' },
    { id: 'user',    label: 'Профиль' },
  ];
  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-around',
      background: 'var(--surface-elevated)', borderRadius: 200, padding: 6,
      boxShadow: 'var(--shadow-glow-white), var(--shadow-md)',
      border: '1px solid var(--border-default)',
    }}>
      {tabs.map(t => {
        const isActive = t.id === active;
        let style;
        if (t.accent && isActive) {
          style = { background: 'var(--accent-teal)', color: 'var(--text-on-accent)' };
        } else if (isActive) {
          style = { background: 'var(--surface-muted)', color: 'var(--text-primary)' };
        } else {
          style = { background: 'transparent', color: 'var(--icon-muted)' };
        }
        return (
          <button
            key={t.id}
            onClick={() => onChange && onChange(t.id)}
            style={{
              flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center',
              gap: 2, padding: '8px 4px',
              borderRadius: 200, border: 0, cursor: 'pointer',
              fontFamily: 'var(--font-display)', fontSize: 10,
              transition: 'background 200ms, color 200ms',
              ...style,
            }}
          >
            <span style={{ width: 22, height: 22, display: 'inline-flex' }}>{icons[t.id]}</span>
            <span>{t.label}</span>
          </button>
        );
      })}
    </div>
  );
};

window.TabBar = TabBar;
